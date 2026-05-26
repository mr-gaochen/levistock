"""
财联社 - 电报/快讯模块

数据源: 财联社 (cls.cn)
模块说明: 提供财联社电报快讯数据接口，支持全部/重要/公司公告三种类型，支持历史日期查询
说明: 数据超过20条（需要翻页）时自动显示进度条
"""

import hashlib
import datetime
import requests
from tqdm import tqdm

_BASE_PARAMS = {
    "app":           "cailianpress",
    "sv":            "8.7.4",
    "os":            "android",
    "mb":            "Xiaomi-2206123SC",
    "ov":            "32",
    "channel":       "8",
    "motif":         "0",
    "net":           "",
    "province_code": "3205",
    "token":         "",
    "uid":           "",
}

_HEADERS = {
    "User-Agent": "okhttp/4.9.0",
    "Host":       "api3.cls.cn",
}

_TELEGRAPH_URL = "https://api3.cls.cn/v1/roll/get_roll_list"

# 消息类型映射：用户传入直观名称 → 财联社接口参数
_CATEGORY_MAP = {
    "all":          "",              # 全部
    "important":   "red",           # 加红重要消息
    "company":     "announcement",  # 公司公告
}


def _make_sign(params: dict) -> str:
    """
    财联社签名算法
    参数按 key 字母序排序 → 拼接为 k=v&k=v → SHA1 → MD5
    """
    s = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sha1 = hashlib.sha1(s.encode()).hexdigest()
    return hashlib.md5(sha1.encode()).hexdigest()


def _fetch_page(last_time: str, category: str) -> dict:
    """请求单页电报数据"""
    p = dict(_BASE_PARAMS, refresh_type="1", last_time=last_time, rn="20")
    if category:
        p["category"] = category
    p["sign"] = _make_sign(p)
    resp = requests.get(_TELEGRAPH_URL, headers=_HEADERS, params=p, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _parse_items(roll_data: list, day_start: int, day_end: int) -> tuple:
    """
    解析单页数据
    返回 (当天的数据列表, 是否已超出当天范围)
    """
    items = []
    out_of_range = False
    for item in roll_data:
        ctime = item.get("ctime", 0)
        if ctime < day_start:
            out_of_range = True
            break
        if ctime <= day_end:
            items.append(item)
    return items, out_of_range


def news_telegraph_cls(date: str = None, category: str = "important") -> list:
    """
    获取财联社电报快讯（财联社）

    数据源: 财联社
    接口地址: https://api3.cls.cn/v1/roll/get_roll_list
    更新频率: 实时
    说明: 数据超过20条（需要翻页）时自动显示进度条

    Args:
        date (str): 查询日期，格式 "YYYY-MM-DD"，如 "2026-05-07"
                    默认为 None，查询今天的数据

        category (str): 消息类型，默认 important（加红重要消息），支持以下类型：
                        - "all":         全部电报
                        - "important":   加红重要消息
                        - "company":     公司公告

    Returns:
        list[dict]: 电报列表，按时间从新到旧排列，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        id             电报ID                 12345678
        title          标题                   "XX公司发布公告..."
        content        正文内容               "..."
        ctime          发布时间戳              1746691200
        time           发布时间（格式化）       "2026-05-07 09:30:00"
        ============= ====================== ====================

    Raises:
        ValueError: 日期格式不正确或 category 不支持时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 获取今天全部电报
        >>> data = lk.news_telegraph_cls()
        >>> print(f"今日电报: {len(data)} 条")
        >>>
        >>> # 获取今天重要消息
        >>> data = lk.news_telegraph_cls(category="important")
        >>> print(data[0]["title"])
        >>>
        >>> # 获取指定日期公司公告
        >>> data = lk.news_telegraph_cls(date="2026-05-07", category="company")
        >>> for item in data:
        ...     print(f"{item['time']} | {item['title']}")
    """
    if category not in _CATEGORY_MAP:
        raise ValueError(
            f"不支持的消息类型：{category}，"
            f"支持的类型：{list(_CATEGORY_MAP.keys())}"
        )

    # 解析日期
    if date is not None:
        try:
            day = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，实际传入：{date}")
    else:
        day = datetime.datetime.now()

    day_start = int(datetime.datetime(day.year, day.month, day.day, 0, 0, 0).timestamp())
    day_end   = int(datetime.datetime(day.year, day.month, day.day, 23, 59, 59).timestamp())

    api_category = _CATEGORY_MAP[category]
    all_items = []
    last_time = str(day_end)

    # 请求第一页
    data = _fetch_page(last_time, api_category)
    roll_data = data.get("data", {}).get("roll_data", [])

    if not roll_data:
        return []

    items, out_of_range = _parse_items(roll_data, day_start, day_end)
    all_items.extend(items)
    last_time = str(roll_data[-1]["sort_score"])

    # 第一页已超出范围或数据不足20条，直接返回
    if out_of_range or len(roll_data) < 20:
        return _format(all_items)

    # 需要翻页，开启进度条
    with tqdm(total=len(all_items), desc="获取电报", unit="条") as pbar:
        pbar.update(len(all_items))  # 更新第一页已获取的数量

        while True:
            data = _fetch_page(last_time, api_category)
            roll_data = data.get("data", {}).get("roll_data", [])

            if not roll_data:
                break

            items, out_of_range = _parse_items(roll_data, day_start, day_end)
            all_items.extend(items)
            pbar.update(len(items))
            last_time = str(roll_data[-1]["sort_score"])

            if out_of_range or len(roll_data) < 20:
                break

    return _format(all_items)


def _format(items: list) -> list:
    """格式化电报数据"""
    result = []
    for item in items:
        ctime = item.get("ctime", 0)
        result.append({
            "title":   item.get("title", ""),
            "content": item.get("content", ""),
            "time":    datetime.datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return result