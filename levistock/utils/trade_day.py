"""
交易日工具模块

数据源: api.levizhang.com
模块说明: 提供A股交易日查询接口，数据实时准确，无需手动维护节假日
"""

import requests

_TRADE_DAY_URL = "https://api.levizhang.com/isTradeDay"


def is_trade_day() -> bool:
    """
    判断今天是否为A股交易日

    数据源: api.levizhang.com
    接口地址: https://api.levizhang.com/isTradeDay
    更新频率: 实时

    与本地维护节假日数据相比，此接口数据更准确，
    可正确处理调休、补班等特殊情况。

    Returns:
        bool: True 表示今天是交易日，False 表示今天不是交易日

    Raises:
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> if lk.is_trade_day():
        ...     print("今天是交易日，开始获取数据")
        ... else:
        ...     print("今天不是交易日")
    """
    resp = requests.get(_TRADE_DAY_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("code") == "000000"

_TRADE_DAYS_URL = "https://api.levizhang.com/getTradeDays"

def get_trade_days(n: int = 10) -> list:
    """
    获取近N个交易日（包含今天）

    数据源: api.levizhang.com
    接口地址: https://api.levizhang.com/getTradeDays

    Args:
        n (int): 查询数量，默认10，范围1-30

    Returns:
        list[str]: 交易日列表，格式 "YYYYMMDD"，按时间从近到远排列

    Raises:
        ValueError: n 不在1-30范围内时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> days = lk.get_trade_days()
        >>> print(days)  # ['20260514', '20260513', ...]
        >>>
        >>> days = lk.get_trade_days(n=5)
        >>> print(days)
    """
    if n < 1 or n > 30:
        raise ValueError(f"n 需在1-30之间，实际传入：{n}")

    resp = requests.get(_TRADE_DAYS_URL, params={"n": n}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])