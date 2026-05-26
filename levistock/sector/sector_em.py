"""
东方财富 - 板块模块

数据源: 东方财富 (eastmoney.com)
模块说明: 提供A股行业/概念板块数据接口，包括板块列表、成分股及股票所属板块查询
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

_BASE_URL = "http://push2delay.eastmoney.com/api/qt/clist/get"
_ULIST_URL = "http://push2delay.eastmoney.com/api/qt/ulist.np/get"

# 板块类型映射
_SECTOR_TYPE_MAP = {
    "industry":    "m:90+t:2+f:!50",   # 全部行业板块
    "concept":     "m:90+t:3+f:!50",   # 概念板块
    "industry_l1": "m:90+s:2+f:!50",   # 一级行业
    "industry_l2": "m:90+s:4+f:!50",   # 二级行业
    "industry_l3": "m:90+s:8+f:!50",   # 三级行业
}


def _build_secid(code: str) -> str:
    """根据股票代码生成东财 secid（市场前缀.代码）"""
    if code.startswith("6"):
        return f"1.{code}"
    elif code.startswith("0") or code.startswith("3"):
        return f"0.{code}"
    elif code.startswith("920"):
        return f"0.{code}"
    return ""


def sector_em(sector_type: str = "industry") -> list:
    """
    获取A股板块列表（东方财富）

    支持行业板块和概念板块查询，通过 sector_type 参数区分。

    数据源: 东方财富
    接口地址: http://push2delay.eastmoney.com/api/qt/clist/get
    更新频率: 交易日实时更新

    Args:
        sector_type (str): 板块类型，默认 "industry"（行业板块）
                           - "industry": 行业板块
                           - "concept":  概念板块

    Returns:
        list[dict]: 板块列表，每条数据包含以下字段：

        ============== ====================== ====================
        字段名          说明                    示例
        ============== ====================== ====================
        sector_code     板块代码               "BK1033"
        sector_name     板块名称               "电池"
        price           最新价                 1161.9
        change_pct      涨跌幅(%)              4.98
        change_amt      涨跌额                 55.07
        volume          成交量(手)             7468144
        amount          成交额(元)             37967558656.0
        amplitude       振幅(%)                7.75
        turnover_rate   换手率(%)              2.99
        total_market    总市值(元)             2106511600000
        main_inflow     主力净流入(元)          2673646592.0
        lead_stock_name 领涨股名称             "德赛电池"
        lead_stock_code 领涨股代码             "000049"
        lead_stock_chg  领涨股涨跌幅(%)        10.01
        up_count        上涨家数               40
        down_count      下跌家数               0
        top_drop_name   跌幅最大股名称          "保力新"
        top_drop_code   跌幅最大股代码          "300116"
        ============== ====================== ====================

    Raises:
        ValueError: sector_type 不支持时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 获取行业板块列表（默认）
        >>> data = lk.sector_em()
        >>> print(len(data))
        >>> print(data[0])
        >>>
        >>> # 获取概念板块列表
        >>> data = lk.sector_em(sector_type="concept")
        >>> print(data[0])
    """
    if sector_type not in _SECTOR_TYPE_MAP:
        raise ValueError(
            f"不支持的板块类型：{sector_type}，支持的类型：{list(_SECTOR_TYPE_MAP.keys())}"
        )

    params = {
        "pn": 1,
        "pz": 200,
        "po": 1,
        "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": _SECTOR_TYPE_MAP[sector_type],
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8,f20,f62,f128,f136,f140,f104,f105,f207,f208",
    }

    result = []
    total = None

    while True:
        resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("rc") != 0:
            raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

        body = data["data"]
        if total is None:
            total = body["total"]

        for item in body.get("diff", []):
            result.append({
                "sector_code":      item.get("f12", "-"),
                "sector_name":      item.get("f14", "-"),
                "price":            item.get("f2",  "-"),
                "change_pct":       item.get("f3",  "-"),
                "change_amt":       item.get("f4",  "-"),
                "volume":           item.get("f5",  "-"),
                "amount":           item.get("f6",  "-"),
                "amplitude":        item.get("f7",  "-"),
                "turnover_rate":    item.get("f8",  "-"),
                "total_market":     item.get("f20", "-"),
                "main_inflow":      item.get("f62", "-"),
                "lead_stock_name":  item.get("f128", "-"),
                "lead_stock_code":  item.get("f140", "-"),
                "lead_stock_chg":   item.get("f136", "-"),
                "up_count":         item.get("f104", "-"),
                "down_count":       item.get("f105", "-"),
                "top_drop_name":    item.get("f207", "-"),
                "top_drop_code":    item.get("f208", "-"),
            })

        if len(result) >= total:
            break

        params["pn"] += 1

    return result


def sector_stocks_em(sector_code: str) -> list:
    """
    获取板块成分股列表（东方财富）

    行业板块和概念板块通用，传入对应板块代码即可。

    数据源: 东方财富
    接口地址: http://push2delay.eastmoney.com/api/qt/clist/get
    更新频率: 交易日实时更新

    Args:
        sector_code (str): 板块代码，如 "BK1033"
                           可通过 sector_em() 获取各板块代码
                           行业板块和概念板块均可使用此接口

    Returns:
        list[dict]: 成分股列表，每条数据包含以下字段：

        =========== ============ =========
        字段名       说明          示例
        =========== ============ =========
        stock_code   股票代码     "000049"
        stock_name   股票名称     "德赛电池"
        =========== ============ =========

    Raises:
        ValueError: sector_code 为空时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 查询行业板块成分股
        >>> stocks = lk.sector_stocks_em("BK1033")
        >>> print(len(stocks))
        >>>
        >>> # 查询概念板块成分股（同一接口）
        >>> stocks = lk.sector_stocks_em("BK1000")
        >>> print(stocks[0])
    """
    if not sector_code:
        raise ValueError("sector_code 不能为空")

    params = {
        "pn": 1,
        "pz": 200,
        "po": 1,
        "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": f"b:{sector_code}+f:!50",
        "fields": "f12,f14",
    }

    result = []
    total = None

    while True:
        resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("rc") != 0:
            raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

        body = data["data"]
        if total is None:
            total = body["total"]

        for item in body.get("diff", []):
            result.append({
                "stock_code": item.get("f12", "-"),
                "stock_name": item.get("f14", "-"),
            })

        if len(result) >= total:
            break

        params["pn"] += 1

    return result


def sector_stock_belong_em(stock_codes: list) -> list:
    """
    查询股票所属行业板块（东方财富）

    批量查询多只股票所属的行业板块信息。

    数据源: 东方财富
    接口地址: http://push2delay.eastmoney.com/api/qt/ulist.np/get
    更新频率: 交易日实时更新

    Args:
        stock_codes (list): 股票代码列表，如 ["000001", "600001", "300001"]
                            支持沪深京全市场股票

    Returns:
        list[dict]: 股票所属板块列表，每条数据包含以下字段：

        =========== ============ =========
        字段名       说明          示例
        =========== ============ =========
        stock_code   股票代码     "000001"
        stock_name   股票名称     "平安银行"
        sector_name  所属行业板块  "银行Ⅱ"
        =========== ============ =========

        注意：部分股票可能返回 "-"，表示暂无对应板块信息

    Raises:
        ValueError: stock_codes 为空时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.sector_stock_belong_em(["000001", "600001", "300001"])
        >>> for item in data:
        ...     print(f"{item['stock_name']} → {item['sector_name']}")
    """
    if not stock_codes:
        raise ValueError("stock_codes 不能为空")

    # 拼接 secids
    secids = []
    for code in stock_codes:
        secid = _build_secid(str(code))
        if secid:
            secids.append(secid)

    if not secids:
        return []

    params = {
        "fields": "f12,f14,f100",
        "invt": 2,
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "wbp2u": "|0|0|0|web",
        "secids": ",".join(secids),
    }

    resp = requests.get(_ULIST_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    items = data.get("data", {}).get("diff", [])
    result = []
    for item in items:
        result.append({
            "stock_code":  str(item.get("f12", "")),
            "stock_name":  str(item.get("f14", "")),
            "sector_name": str(item.get("f100", "-")),
        })

    return result
