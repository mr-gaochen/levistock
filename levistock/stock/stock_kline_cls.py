"""
财联社 - 个股行情模块

数据源: 财联社 (cls.cn)
模块说明: 提供A股个股分时数据及K线数据接口
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.cls.cn/",
}

_TIMELINE_URL = "https://x-quote.cls.cn/quote/stock/tline"
_KLINE_URL = "https://x-quote.cls.cn/quote/stock/kline"

# K线类型映射：用户传入直观名称 → 财联社接口参数
_KLINE_TYPE_MAP = {
    "daily":   "fd1",   # 日K
    "weekly":  "fw",    # 周K
    "monthly": "fm",    # 月K
    "yearly":  "fy",    # 年K
}


def _build_secu_code(code: str) -> str:
    """
    根据股票代码自动添加市场前缀
    沪市(6开头)   → sh xxxxxx
    深市(0/3开头) → sz xxxxxx
    北交所(920开头) → bj xxxxxx

    Args:
        code: 纯数字股票代码，如 "605178"、"002664"、"920045"

    Returns:
        带市场前缀的代码，如 "sh605178"、"sz002664"、"bj920045"
        如果已经带前缀则直接返回
    """
    # 已经带前缀直接返回
    if code.startswith(("sh", "sz", "bj")):
        return code

    if code.startswith("6"):
        return f"sh{code}"
    elif code.startswith("0") or code.startswith("3"):
        return f"sz{code}"
    elif code.startswith("920"):
        return f"bj{code}"
    else:
        raise ValueError(f"无法识别的股票代码：{code}，请检查代码是否正确")


def stock_timeline_cls(stock_code: str) -> list:
    """
    获取个股分时数据（财联社）

    数据源: 财联社
    接口地址: https://x-quote.cls.cn/quote/stock/tline
    更新频率: 交易日实时更新

    Args:
        stock_code (str): 股票代码，支持以下格式：
                          - 纯代码: "002664"、"605178"、"920045"
                          - 带前缀: "sz002664"、"sh605178"、"bj920045"
                          SDK 会自动识别市场并添加前缀

    Returns:
        list[dict]: 分时数据列表，每条数据包含以下字段：

        ================= ====================== ====================
        字段名             说明                    示例
        ================= ====================== ====================
        date               交易日期               "20240101"
        minute             分钟时间               "0930"
        last_px            最新价                 11.50
        business_balance   成交额                 123456.0
        business_amount    成交量                 12345
        open_px            开盘价                 11.45
        preclose_px        昨收价                 11.46
        av_px              均价                   11.48
        ================= ====================== ====================

    Raises:
        ValueError: 股票代码格式不正确时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 传纯代码，自动识别市场
        >>> data = lk.stock_timeline_cls(stock_code="002664")
        >>> print(len(data))
        >>> print(data[0])
        >>>
        >>> # 传带前缀的代码
        >>> data = lk.stock_timeline_cls(stock_code="sz002664")
        >>> print(data[0])
    """
    secu_code = _build_secu_code(stock_code)

    params = {
        "app":    "CailianpressWeb",
        "os":     "web",
        "sv":     "8.4.6",
        "secu_code": secu_code,
        "fields": "date,minute,last_px,business_balance,business_amount,open_px,preclose_px,av_px",
        "sign":   "afad7ec0475a1b9854313502389f3346",
    }

    resp = requests.get(_TIMELINE_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(
            f"接口返回异常，code={data.get('code')}，msg={data.get('msg')}"
        )

    body = data.get("data", {})
    if body is None:
        return []

    items = body.get("line", [])
    return items if items else []


def stock_kline_cls(stock_code: str, kline_type: str = "daily",
                    limit: int = 50, offset: int = 0) -> list:
    """
    获取个股K线数据（财联社）

    数据源: 财联社
    接口地址: https://x-quote.cls.cn/quote/stock/kline
    更新频率: 交易日实时更新

    Args:
        stock_code (str): 股票代码，支持以下格式：
                          - 纯代码: "002664"、"605178"、"920045"
                          - 带前缀: "sz002664"、"sh605178"、"bj920045"
                          SDK 会自动识别市场并添加前缀

        kline_type (str): K线类型，默认 "daily"（日K），支持以下类型：
                          - "daily":   日K
                          - "weekly":  周K
                          - "monthly": 月K
                          - "yearly":  年K

        limit  (int): 返回条数，默认 50
        offset (int): 偏移量，默认 0（从最新数据开始）

    Returns:
        list[dict]: K线数据列表，按时间从旧到新排列，每条数据包含以下字段：

        ================= ====================== ====================
        字段名             说明                    示例
        ================= ====================== ====================
        date               交易日期               "20240101"
        open               开盘价                 11.45
        close              收盘价                 11.50
        high               最高价                 11.60
        low                最低价                 11.40
        volume             成交量                 1234567
        amount             成交额                 12345678.0
        change             涨跌额                 0.04
        change_rate        涨跌幅                 0.35
        ================= ====================== ====================

    Raises:
        ValueError: 股票代码或K线类型不正确时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 获取日K线（默认）
        >>> data = lk.stock_kline_cls(stock_code="002664")
        >>> print(len(data))
        >>> print(data[0])
        >>>
        >>> # 获取周K线
        >>> data = lk.stock_kline_cls(stock_code="002664", kline_type="weekly")
        >>> print(data[0])
        >>>
        >>> # 获取月K线，返回100条
        >>> data = lk.stock_kline_cls(stock_code="002664", kline_type="monthly", limit=100)
        >>> print(data[0])
    """
    if kline_type not in _KLINE_TYPE_MAP:
        raise ValueError(
            f"不支持的K线类型：{kline_type}，"
            f"支持的类型：{list(_KLINE_TYPE_MAP.keys())}"
        )

    secu_code = _build_secu_code(stock_code)
    api_type = _KLINE_TYPE_MAP[kline_type]

    params = {
        "app":       "CailianpressWeb",
        "os":        "web",
        "sv":        "8.4.6",
        "secu_code": secu_code,
        "type":      api_type,
        "limit":     limit,
        "offset":    offset,
        "sign":      "d2656d0d3fdc1d489f6f316ea820cc17",
    }

    resp = requests.get(_KLINE_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(
            f"接口返回异常，code={data.get('code')}，msg={data.get('msg')}"
        )

    items = data.get("data", [])
    return items if items else []
