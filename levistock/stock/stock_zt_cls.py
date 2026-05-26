"""
财联社 - 涨停板模块

数据源: 财联社 (cls.cn)
模块说明: 提供A股涨停池数据接口，含涨停原因，仅支持当天数据
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.cls.cn/",
}

_ZT_URL = (
    "https://x-quote.cls.cn/quote/index/up_down_analysis"
)


def stock_zt_pool_cls() -> list:
    """
    获取当日涨停池（财联社）

    与东财涨停池 stock_zt_pool_em() 的区别：
        - 财联社涨停池包含涨停原因字段
        - 仅支持当天数据，不支持历史查询
        - 东财涨停池字段更全，支持历史日期查询

    数据源: 财联社
    接口地址: https://x-quote.cls.cn/quote/index/up_down_analysis
    更新频率: 交易日实时更新

    Returns:
        list[dict]: 涨停股票列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        secu_code      股票代码（含市场前缀）   "sh603929"
        secu_name      股票名称               "亚翔集成"
        last_px        现价(元)               11.50
        change         涨跌幅                 0.10
        up_reason      涨停原因               "新能源汽车概念"
        ============= ====================== ====================

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 获取今日涨停池（含涨停原因）
        >>> data = lk.stock_zt_pool_cls()
        >>> print(f"今日涨停数: {len(data)}")
        >>> print(data[0])
        >>>
        >>> # 查看涨停原因
        >>> for item in data[:5]:
        ...     print(f"{item['secu_name']}: {item['up_reason']}")
    """
    params = {
        "app":   "CailianpressWeb",
        "os":    "web",
        "rever": 1,
        "sv":    "8.4.6",
        "type":  "up_pool",
        "way":   "last_px",
        "sign":  "a6ab28604a6dbe891cdbd7764799eda1",
    }

    resp = requests.get(_ZT_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(
            f"接口返回异常，code={data.get('code')}，msg={data.get('msg')}"
        )

    items = data.get("data", [])
    result = []

    for item in items:
        result.append({
            "secu_code":  item.get("secu_code", ""),
            "secu_name":  item.get("secu_name", ""),
            "last_px":    item.get("last_px", "-"),
            "change":     item.get("change", "-"),
            "up_reason":  item.get("up_reason", ""),
        })

    return result
