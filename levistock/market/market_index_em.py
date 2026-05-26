"""
东方财富 - 大盘指数模块

数据源: 东方财富 (eastmoney.com)
模块说明: 提供A股大盘指数实时行情数据接口
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

_BASE_URL = "https://push2delay.eastmoney.com/api/qt/clist/get"

# 常用6个指数
_DEFAULT_INDICES = [
    "上证指数",
    "深证成指",
    "创业板指",
    "科创50",
    "沪深300",
    "中证500",
]


def _fetch_indices(target: list = None) -> list:
    """
    内部通用请求方法

    Args:
        target: 指定返回的指数名称列表，None 表示返回全部
    """
    params = {
        "np": 1,
        "fltt": 1,
        "invt": 2,
        "fs": "b:MK0010",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18",
        "fid": "",
        "pn": 1,
        "pz": 100,
        "po": 1,
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "dect": 1,
    }

    resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    items = data.get("data", {}).get("diff", [])

    def parse(val):
        """价格字段除以100"""
        try:
            return round(float(val) / 100, 2)
        except (ValueError, TypeError):
            return "-"

    result = []
    for item in items:
        name = item.get("f14", "")
        # 如果指定了目标列表，只返回目标中的指数
        if target is not None and name not in target:
            continue
        result.append({
            "name":       name,
            "code":       str(item.get("f12", "")),
            "price":      parse(item.get("f2")),
            "change_pct": parse(item.get("f3")),
            "change_amt": parse(item.get("f4")),
            "volume":     item.get("f5", "-"),
            "amount":     item.get("f6", "-"),
            "high":       parse(item.get("f15")),
            "low":        parse(item.get("f16")),
            "open":       parse(item.get("f17")),
            "pre_close":  parse(item.get("f18")),
        })

    # 如果指定了目标列表，按目标顺序排列
    if target is not None:
        index_map = {r["name"]: r for r in result}
        result = [index_map[n] for n in target if n in index_map]

    return result


def market_index_em() -> list:
    """
    获取A股常用大盘指数实时行情（东方财富）

    返回以下6个常用指数：
        上证指数、深证成指、创业板指、科创50、沪深300、中证500

    数据源: 东方财富
    接口地址: https://push2delay.eastmoney.com/api/qt/clist/get
    更新频率: 交易日实时更新

    Returns:
        list[dict]: 指数行情列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        name           指数名称               "上证指数"
        code           指数代码               "000001"
        price          最新价/收盘价           3200.50
        change_pct     涨跌幅(%)              0.35
        change_amt     涨跌额                 11.20
        volume         成交量                 123456789
        amount         成交额(元)             1234567890.0
        high           最高价                 3210.00
        low            最低价                 3190.00
        open           开盘价                 3195.00
        pre_close      昨收价                 3189.30
        ============= ====================== ====================

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.market_index_em()
        >>> for item in data:
        ...     print(f"{item['name']}: {item['price']} ({item['change_pct']}%)")
    """
    return _fetch_indices(target=_DEFAULT_INDICES)


def market_index_all_em() -> list:
    """
    获取A股全部大盘指数实时行情（东方财富）

    返回东财 MK0010 板块下的所有指数数据。

    数据源: 东方财富
    接口地址: https://push2delay.eastmoney.com/api/qt/clist/get
    更新频率: 交易日实时更新

    Returns:
        list[dict]: 指数行情列表，字段同 market_index_em()

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        name           指数名称               "上证指数"
        code           指数代码               "000001"
        price          最新价/收盘价           3200.50
        change_pct     涨跌幅(%)              0.35
        change_amt     涨跌额                 11.20
        volume         成交量                 123456789
        amount         成交额(元)             1234567890.0
        high           最高价                 3210.00
        low            最低价                 3190.00
        open           开盘价                 3195.00
        pre_close      昨收价                 3189.30
        ============= ====================== ====================

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.market_index_all_em()
        >>> print(f"共 {len(data)} 个指数")
        >>> print(data[0])
    """
    return _fetch_indices(target=None)