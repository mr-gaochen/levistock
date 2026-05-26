"""
财联社 - 风口/主线模块

数据源: 财联社 (cls.cn)
模块说明: 提供A股每日风口板块、风口龙头股及主线机会数据接口
"""

import hashlib
import requests

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
    "User-Agent":      "okhttp/4.9.0",
    "Accept-Encoding": "gzip",
    "Connection":      "Keep-Alive",
}


def _make_sign(params: dict) -> str:
    """
    财联社签名算法
    参数按 key 字母序排序 → 拼接为 k=v&k=v → SHA1 → MD5
    """
    s = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sha1 = hashlib.sha1(s.encode()).hexdigest()
    return hashlib.md5(sha1.encode()).hexdigest()


def _build_params(**extra) -> dict:
    """在基础参数上追加额外参数，并自动计算签名"""
    p = dict(_BASE_PARAMS, **extra)
    p["sign"] = _make_sign(p)
    return p


def market_wind_cls() -> list:
    """
    获取今日风口板块列表（财联社）

    数据源: 财联社
    接口地址: https://api3.cls.cn/v2/todayTuyere
    更新频率: 交易日实时更新

    Returns:
        list[dict]: 风口板块列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        plate_code     板块代码               "cls80198"
        plate_name     板块名称               "锂电池"
        catalyst       催化剂描述              "新能源政策利好..."
        ============= ====================== ====================

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.market_wind_cls()
        >>> print(f"今日风口板块: {len(data)} 个")
        >>> for item in data:
        ...     print(f"{item['plate_name']}: {item['catalyst'][:20]}...")
    """
    params = _build_params()
    resp = requests.get(
        "https://api3.cls.cn/v2/todayTuyere",
        headers=dict(_HEADERS, Host="api3.cls.cn"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("errno") != 0:
        raise RuntimeError(f"接口返回异常：{data}")

    items = data.get("data", {}).get("today_tuyere", [])
    result = []
    for item in items:
        result.append({
            "plate_code": item.get("plate_code", ""),
            "plate_name": item.get("title", ""),
            "catalyst":   item.get("interpret", ""),
        })
    return result


def market_wind_stocks_cls(plate_code: str) -> list:
    """
    获取风口板块龙头股列表（财联社）

    数据源: 财联社
    接口地址: https://x-quote.cls.cn/v2/quote/a/plate/tuyere/stocks
    更新频率: 交易日实时更新

    Args:
        plate_code (str): 板块代码，如 "cls80198"
                          可通过 market_wind_cls() 获取各风口板块代码

    Returns:
        list[dict]: 龙头股列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        secu_code      股票代码（含市场前缀）   "sh603929"
        secu_name      股票名称               "亚翔集成"
        last_px        现价(元)               11.50
        change         涨跌幅                 0.10
        continuous     连板次数               3
        ============= ====================== ====================

    Raises:
        ValueError: plate_code 为空时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 先获取风口板块
        >>> wind = lk.market_wind_cls()
        >>> plate_code = wind[0]["plate_code"]
        >>> # 再获取该板块龙头股
        >>> stocks = lk.market_wind_stocks_cls(plate_code)
        >>> print(stocks)
    """
    if not plate_code:
        raise ValueError("plate_code 不能为空")

    params = _build_params(plate_code=plate_code)
    resp = requests.get(
        "https://x-quote.cls.cn/v2/quote/a/plate/tuyere/stocks",
        headers=dict(_HEADERS, Host="x-quote.cls.cn"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(f"接口返回异常：{data}")

    items = data.get("data", [])
    result = []
    for item in items:
        result.append({
            "secu_code": item.get("secu_code", ""),
            "secu_name": item.get("secu_name", ""),
            "last_px":   item.get("last_px", "-"),
            "change":    item.get("change", "-"),
            "continuous": item.get("continuous", "-"),
        })
    return result


def market_mainline_cls() -> dict:
    """
    获取今日主线机会（财联社）

    数据源: 财联社
    接口地址: https://api3.cls.cn/v2/dingPan/mainline
    更新频率: 交易日实时更新

    Returns:
        dict: 主线机会数据，包含主线题材、板块及龙头股信息
              原始接口返回结构，包含 faucet_1/faucet_2/faucet_3 等字段

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.market_mainline_cls()
        >>> print(data)
    """
    params = _build_params()
    resp = requests.get(
        "https://api3.cls.cn/v2/dingPan/mainline",
        headers=dict(_HEADERS, Host="api3.cls.cn"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("errno") != 0:
        raise RuntimeError(f"接口返回异常：{data}")

    return data.get("data", {})
