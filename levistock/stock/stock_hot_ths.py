"""
同花顺 - 人气股排行模块

数据源: 同花顺 (10jqka.com.cn) + 东方财富行情补充
模块说明: 提供A股人气股排行数据接口，含实时行情数据
"""

import re
import json
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.10jqka.com.cn/",
}

_HOT_URL = "https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock"

# 东财行情补充接口基础URL（JSONP格式，secids直接拼在后面）
_DETAIL_BASE_URL = (
    "http://push2delay.eastmoney.com/api/qt/ulist.np/get"
    "?fields=f2,f3,f4,f12&invt=2"
    "&cb=jQuery1124020910551869614946_1654180748613"
    "&ut=fa5fd1943c7b386f172d6893dbfba10b"
    "&wbp2u=%7C0%7C0%7C0%7Cweb"
    "&secids="
)


def _build_secid(code: str) -> str:
    """
    根据股票代码生成东财 secid（市场前缀.代码）
    沪市(6开头) → 1.xxxxxx
    深市/创业板(0/3开头) → 0.xxxxxx
    北交所/三板(8/4开头) → 0.xxxxxx
    """
    if code.startswith("6"):
        return f"1.{code}"
    elif code.startswith("0") or code.startswith("3"):
        return f"0.{code}"
    elif code.startswith("8") or code.startswith("4"):
        return f"0.{code}"
    return ""


def _enrich_stock_details(stock_list: list) -> list:
    """
    批量补充股票行情数据（现价、涨跌幅、涨跌额）
    调用东财 ulist 接口，返回 JSONP 格式，价格字段需除以100
    """
    secids = []
    for item in stock_list:
        code = item.get("code", "")
        if not code or code == "undefined":
            continue
        secid = _build_secid(code)
        if secid:
            secids.append(secid)

    if not secids:
        return stock_list

    # 直接拼 URL，secids 拼在末尾
    url = _DETAIL_BASE_URL + ",".join(secids)
    resp = requests.get(url, headers=_HEADERS, timeout=10)
    resp.raise_for_status()

    # 接口返回 JSONP 格式，去掉回调函数包装
    text = resp.text
    match = re.search(r'\((.*)\)', text, re.DOTALL)
    if not match:
        return stock_list

    data = json.loads(match.group(1))
    if data.get("rc") != 0:
        return stock_list

    detail_list = data.get("data", {}).get("diff", [])

    # 转成 code → detail 的映射
    detail_map = {}
    for detail in detail_list:
        code = str(detail.get("f12", ""))
        detail_map[code] = detail

    def parse(val):
        """价格字段除以100"""
        try:
            if str(val) == "-":
                return 0.0
            return round(float(val) / 100, 2)
        except (ValueError, TypeError):
            return 0.0

    # 补充行情数据
    for item in stock_list:
        code = item.get("code", "")
        detail = detail_map.get(code)
        if detail:
            item["price"]      = parse(detail.get("f2"))
            item["change_pct"] = parse(detail.get("f3"))
            item["change_amt"] = parse(detail.get("f4"))

    return stock_list


def stock_hot_rank_ths(limit: int = 100) -> list:
    """
    获取A股人气股排行榜（同花顺）

    数据源: 同花顺人气榜 + 东方财富行情补充
    接口地址: https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock
    更新频率: 交易日实时更新（小时级别）

    Args:
        limit (int): 返回条数，默认 100，排名越靠后参考价值越低

    Returns:
        list[dict]: 人气股列表，按人气排名由高到低排列，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        rank           排名                   1
        code           股票代码               "000001"
        name           股票名称               "平安银行"
        price          现价(元)               11.50
        change_pct     涨跌幅(%)              0.35
        change_amt     涨跌额                 0.04
        tag            标签信息(dict)          {"market_topic": "AI"}
        ============= ====================== ====================

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 获取默认前100条人气股
        >>> data = lk.stock_hot_rank_ths()
        >>> print(len(data))
        >>> print(data[0])
        >>>
        >>> # 获取前20条
        >>> data = lk.stock_hot_rank_ths(limit=20)
        >>> for item in data:
        ...     print(f"{item['rank']}. {item['name']} {item['change_pct']}%")
    """
    params = {
        "stock_type": "a",
        "type": "hour",
        "list_type": "normal",
    }

    resp = requests.get(_HOT_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status_code") != 0:
        raise RuntimeError(
            f"接口返回异常，status_code={data.get('status_code')}，"
            f"msg={data.get('status_msg')}"
        )

    stock_list = data.get("data", {}).get("stock_list", [])

    # 限制返回条数
    stock_list = stock_list[:limit]

    result = []
    for i, item in enumerate(stock_list):
        result.append({
            "rank":       i + 1,
            "code":       item.get("code", ""),
            "name":       item.get("name", ""),
            "price":      0.0,
            "change_pct": 0.0,
            "change_amt": 0.0,
            "tag":        item.get("tag", {}),
        })

    # 批量补充行情数据
    result = _enrich_stock_details(result)

    return result