"""
东方财富 - 涨跌停板模块

数据源: 东方财富 (eastmoney.com)
模块说明: 提供A股涨停板、跌停板、昨日涨停数据接口
"""

import requests
from datetime import datetime

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

_ZT_URL        = "https://push2ex.eastmoney.com/getTopicZTPool"
_DT_URL        = "https://push2ex.eastmoney.com/getTopicDTPool"
_YESTERDAY_URL = "https://push2ex.eastmoney.com/getYesterdayZTPool"


def _validate_date(date: str) -> str:
    """校验日期格式，返回合法日期字符串"""
    if date is not None:
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValueError(f"日期格式错误，应为 YYYYMMDD，如 '20240101'，实际传入：{date}")
        return date
    return datetime.now().strftime("%Y%m%d")


def stock_zt_pool_em(date: str = None) -> list:
    """
    获取涨停板股票池（东方财富）

    数据源: 东方财富
    接口地址: https://push2ex.eastmoney.com/getTopicZTPool
    更新频率: 交易日实时更新

    Args:
        date (str): 交易日期，格式 YYYYMMDD，如 "20240101"
                    默认为 None，自动取当天日期

    Returns:
        list[dict]: 涨停股票列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        date           交易日期               "20260514"
        stock_code     股票代码               "000001"
        stock_name     股票名称               "平安银行"
        market         市场                   "0"(深) "1"(沪)
        price          现价(元)               11.50
        change_pct     涨跌幅(%)              10.01
        amount         成交额(元)             123456789.0
        circ_market    流通市值(元)            223000000000.0
        circ_share     流通股本(股)            100000000.0
        turnover_rate  换手率(%)              5.21
        continuous     连板次数               2
        first_zt_time  首次涨停时间           "093000"
        last_zt_time   最后涨停时间           "150000"
        main_inflow    主力净流入(元)          12345678.0
        open_times     炸板次数               0
        sector         所属行业板块            "银行"
        ============= ====================== ====================

    Raises:
        ValueError: 日期格式不正确时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.stock_zt_pool_em()
        >>> data = lk.stock_zt_pool_em(date="20260513")
        >>> print(f"涨停数: {len(data)}")
    """
    date = _validate_date(date)

    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 3000,
        "sort": "fbt:asc",
        "date": date,
    }

    resp = requests.get(_ZT_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    body = data.get("data")
    if body is None:
        return []

    result = []
    for item in body.get("pool", []):
        price = item.get("p", 0)
        try:
            price = round(float(price) / 1000, 2)
        except (ValueError, TypeError):
            price = "-"

        result.append({
            "date":          date,
            "stock_code":    str(item.get("c", "")),
            "stock_name":    str(item.get("n", "")),
            "market":        str(item.get("m", "")),
            "price":         price,
            "change_pct":    item.get("zdp", "-"),
            "amount":        item.get("amount", "-"),
            "circ_market":   item.get("ltsz", "-"),
            "circ_share":    item.get("tshare", "-"),
            "turnover_rate": item.get("hs", "-"),
            "continuous":    item.get("lbc", "-"),
            "first_zt_time": str(item.get("fbt", "")),
            "last_zt_time":  str(item.get("lbt", "")),
            "main_inflow":   item.get("fund", "-"),
            "open_times":    item.get("zbc", "-"),
            "sector":        str(item.get("hybk", "")),
            "zt_days":       item.get("zttj", {}).get("days", "-"),
            "zt_count":      item.get("zttj", {}).get("ct", "-"),
        })

    return result


def stock_dt_pool_em(date: str = None) -> list:
    """
    获取跌停板股票池（东方财富）

    数据源: 东方财富
    接口地址: https://push2ex.eastmoney.com/getTopicDTPool
    更新频率: 交易日实时更新

    Args:
        date (str): 交易日期，格式 YYYYMMDD，如 "20260514"
                    默认为 None，自动取当天日期

    Returns:
        list[dict]: 跌停股票列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        date           交易日期               "20260514"
        stock_code     股票代码               "603126"
        stock_name     股票名称               "中材节能"
        market         市场                   "0"(深) "1"(沪)
        price          现价(元)               8.92
        change_pct     涨跌幅(%)              -9.99
        amount         成交额(元)             677814608.0
        circ_market    流通市值(元)            5445660000.0
        circ_share     流通股本(股)            5445660000.0
        turnover_rate  换手率(%)              12.01
        days           连续跌停天数            1
        last_dt_time   最后跌停时间           "145209"
        seal_amount    封单金额(元)            36950208.0
        main_inflow    主力净流入(元)          331824.0
        sector         所属行业板块            "环保设备"
        ============= ====================== ====================

    Raises:
        ValueError: 日期格式不正确时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.stock_dt_pool_em()
        >>> data = lk.stock_dt_pool_em(date="20260513")
        >>> print(f"跌停数: {len(data)}")
    """
    date = _validate_date(date)

    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 3000,
        "sort": "fund:asc",
        "date": date,
    }

    resp = requests.get(_DT_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    body = data.get("data")
    if body is None:
        return []

    result = []
    for item in body.get("pool", []):
        price = item.get("p", 0)
        try:
            price = round(float(price) / 1000, 2)
        except (ValueError, TypeError):
            price = "-"

        result.append({
            "date":          date,
            "stock_code":    str(item.get("c", "")),
            "stock_name":    str(item.get("n", "")),
            "market":        str(item.get("m", "")),
            "price":         price,
            "change_pct":    item.get("zdp", "-"),
            "amount":        item.get("amount", "-"),
            "circ_market":   item.get("ltsz", "-"),
            "circ_share":    item.get("tshare", "-"),
            "turnover_rate": item.get("hs", "-"),
            "days":          item.get("days", "-"),
            "last_dt_time":  str(item.get("lbt", "")),
            "seal_amount":   item.get("fba", "-"),
            "main_inflow":   item.get("fund", "-"),
            "sector":        str(item.get("hybk", "")),
        })

    return result


def stock_yesterday_zt_em(date: str = None) -> list:
    """
    获取昨日涨停今日表现（东方财富）

    数据源: 东方财富
    接口地址: https://push2ex.eastmoney.com/getYesterdayZTPool
    更新频率: 交易日实时更新

    Args:
        date (str): 交易日期，格式 YYYYMMDD，如 "20260514"
                    默认为 None，自动取当天日期

    Returns:
        list[dict]: 昨日涨停股票列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        date           交易日期               "20260514"
        stock_code     股票代码               "600172"
        stock_name     股票名称               "黄河旋风"
        market         市场                   "0"(深) "1"(沪)
        price          现价(元)               11.83
        zt_price       涨停价(元)             13.02
        change_pct     今日涨跌幅(%)          -0.08
        amount         成交额(元)             4527867648.0
        circ_market    流通市值(元)            15098105522.5
        turnover_rate  换手率(%)              29.34
        amplitude      振幅(%)                7.85
        open_ratio     高开比(%)              0.94
        yesterday_time 昨日涨停时间           "133733"
        yesterday_cont 昨日连板数             3
        sector         所属行业板块            "通用设备"
        zt_days        近期涨停天数            4
        zt_count       近期涨停次数            3
        ============= ====================== ====================

    Raises:
        ValueError: 日期格式不正确时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.stock_yesterday_zt_em()
        >>> data = lk.stock_yesterday_zt_em(date="20260514")
        >>> print(f"昨日涨停数: {len(data)}")
        >>> for item in data[:3]:
        ...     print(f"{item['stock_name']} 今日:{item['change_pct']}% 高开:{item['open_ratio']}%")
    """
    date = _validate_date(date)

    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 3000,
        "sort": "zs:desc",
        "date": date,
    }

    resp = requests.get(_YESTERDAY_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    body = data.get("data")
    if body is None:
        return []

    result = []
    for item in body.get("pool", []):
        price = item.get("p", 0)
        zt_price = item.get("ztp", 0)
        try:
            price    = round(float(price) / 1000, 2)
            zt_price = round(float(zt_price) / 1000, 2)
        except (ValueError, TypeError):
            price = zt_price = "-"

        zttj = item.get("zttj", {})
        result.append({
            "date":           date,
            "stock_code":     str(item.get("c", "")),
            "stock_name":     str(item.get("n", "")),
            "market":         str(item.get("m", "")),
            "price":          price,
            "zt_price":       zt_price,
            "change_pct":     item.get("zdp", "-"),
            "amount":         item.get("amount", "-"),
            "circ_market":    item.get("ltsz", "-"),
            "turnover_rate":  item.get("hs", "-"),
            "amplitude":      item.get("zf", "-"),
            "open_ratio":     item.get("zs", "-"),
            "yesterday_time": str(item.get("yfbt", "")),
            "yesterday_cont": item.get("ylbc", "-"),
            "sector":         str(item.get("hybk", "")),
            "zt_days":        zttj.get("days", "-"),
            "zt_count":       zttj.get("ct", "-"),
        })

    return result