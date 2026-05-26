"""
东方财富 - 个股异动模块

数据源: 东方财富 (eastmoney.com)
模块说明: 提供A股个股盘口异动数据接口，包括异动股列表及个股异动明细查询
"""

import requests
from datetime import datetime

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

_CHANGES_URL = "https://push2ex.eastmoney.com/getAllStockChanges"
_DETAIL_URL = "http://push2ex.eastmoney.com/getStockChanges"

# 异动类型映射表（东财内部编码 → 类型名称）
# 对应东财盘口异动页面的22种类型，编号1-22
CHANGE_TYPE_MAP = {
    "8201": "火箭发射",
    "8202": "快速反弹",
    "8203": "加速下跌",
    "8204": "高台跳水",
    "8193": "大笔买入",
    "8194": "大笔卖出",
    "8205": "封涨停板",
    "8206": "封跌停板",
    "8207": "打开跌停板",
    "8208": "打开涨停板",
    "64":   "有大买盘",
    "128":  "有大卖盘",
    "8209": "竞价上涨",
    "8210": "竞价下跌",
    "8211": "高开5日线",
    "8212": "低开5日线",
    "8213": "向上缺口",
    "8214": "向下缺口",
    "8215": "60日新高",
    "8216": "60日新低",
    "8217": "60日大幅上涨",
    "8218": "60日大幅下跌",
}


def stock_changes_em(change_type: str = "8201", filter_st: bool = True) -> list:
    """
    获取实时盘口异动股票列表（东方财富）

    数据源: 东方财富
    接口地址: https://push2ex.eastmoney.com/getAllStockChanges
    更新频率: 交易日实时更新

    过滤规则（默认）:
        - 过滤 ST、*ST 股票
        - 过滤三板股票（股票代码4开头）
        - 保留北交所股票（股票代码8开头）

    Args:
        change_type (str): 异动类型编码，默认 "8201"（火箭发射）
                           支持以下类型：
                           - "8201": 火箭发射
                           - "8202": 快速反弹
                           - "8203": 加速下跌
                           - "8204": 高台跳水
                           - "8193": 大笔买入
                           - "8194": 大笔卖出
                           - "8205": 封涨停板
                           - "8206": 封跌停板
                           - "8207": 打开跌停板
                           - "8208": 打开涨停板
                           - "64":   有大买盘
                           - "128":  有大卖盘
                           - "8209": 竞价上涨
                           - "8210": 竞价下跌
                           - "8211": 高开5日线
                           - "8212": 低开5日线
                           - "8213": 向上缺口
                           - "8214": 向下缺口
                           - "8215": 60日新高
                           - "8216": 60日新低
                           - "8217": 60日大幅上涨
                           - "8218": 60日大幅下跌

        filter_st (bool): 是否过滤ST、*ST及三板股票，默认为 True
                          - True:  过滤，只返回正常交易股票（保留北交所）
                          - False: 不过滤，返回全部异动股票

    Returns:
        list[dict]: 异动股票列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        stock_code     股票代码               "000001"
        stock_name     股票名称               "平安银行"
        market         市场                   "0"(深) "1"(沪)
        time           异动时间               "093000"
        change_pct     涨幅                   "0.05"
        change_type    异动类型名称            "火箭发射"
        ============= ====================== ====================

    Raises:
        ValueError: 异动类型编码不支持时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 获取火箭发射异动股（默认）
        >>> data = lk.stock_changes_em()
        >>> print(len(data))
        >>> print(data[0])
        >>>
        >>> # 获取大笔买入异动股
        >>> data = lk.stock_changes_em(change_type="8193")
        >>> print(data[0])
        >>>
        >>> # 获取全部异动股（不过滤）
        >>> data_all = lk.stock_changes_em(filter_st=False)
        >>> print(len(data_all))
    """
    if change_type not in CHANGE_TYPE_MAP:
        raise ValueError(
            f"不支持的异动类型：{change_type}，"
            f"支持的类型：{list(CHANGE_TYPE_MAP.keys())}"
        )

    params = {
        "type": change_type,
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "pageindex": 0,
        "pagesize": 10000,
        "dpt": "wzchanges",
    }

    resp = requests.get(_CHANGES_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    body = data.get("data")
    if body is None:
        return []

    items = body.get("allstock", [])
    result = []

    for item in items:
        code = str(item.get("c", ""))
        name = str(item.get("n", ""))

        if filter_st:
            # 过滤三板（代码4开头）
            if code.startswith("4"):
                continue
            # 过滤 ST、*ST
            if name.startswith("ST") or name.startswith("*ST"):
                continue

        # 异动时间格式化（补零）
        tm = str(item.get("tm", ""))
        if len(tm) == 5:
            tm = "0" + tm

        result.append({
            "stock_code":  code,
            "stock_name":  name,
            "market":      str(item.get("m", "")),
            "time":        tm,
            "change_pct":  item.get("i", "-"),
            "change_type": CHANGE_TYPE_MAP.get(change_type, change_type),
        })

    return result


def stock_changes_detail_em(stock_code: str, market: str, date: str = None) -> list:
    """
    获取个股盘口异动明细（东方财富）

    数据源: 东方财富
    接口地址: http://push2ex.eastmoney.com/getStockChanges
    更新频率: 交易日实时更新

    异动类型说明:
        - 8201: 火箭发射
        - 8193: 大笔买入
        - 64:   有大买盘
        （完整类型见 CHANGE_TYPE_MAP）

    Args:
        stock_code (str): 股票代码，如 "000001"
        market     (str): 市场标识，"0" 深市，"1" 沪市
        date       (str): 交易日期，格式 YYYYMMDD，默认为 None 取当天
                          支持查询历史异动明细
                          注意：非交易日或无数据时返回空列表

    Returns:
        list[dict]: 异动明细列表，每条数据包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        time           异动时间               "093000"
        type           异动类型编码            8201
        type_name      异动类型名称            "火箭发射"
        price          价格(元)               11.50
        change_pct     涨跌幅(%)              4.40
        volume         成交量(手)             1234
        ============= ====================== ====================

    Raises:
        ValueError: 参数为空或日期格式不正确时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 查询今日个股异动明细
        >>> data = lk.stock_changes_detail_em(stock_code="000001", market="0")
        >>> print(len(data))
        >>> print(data[0])
        >>>
        >>> # 查询历史异动明细
        >>> data = lk.stock_changes_detail_em(
        ...     stock_code="000001", market="0", date="20240101"
        ... )
        >>> if data:
        ...     print(data[0])
        ... else:
        ...     print("当日无异动数据")
    """
    if not stock_code:
        raise ValueError("stock_code 不能为空")
    if not market:
        raise ValueError("market 不能为空")

    # 校验日期格式
    if date is not None:
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValueError(
                f"日期格式错误，应为 YYYYMMDD，如 '20240101'，实际传入：{date}"
            )
    else:
        date = datetime.now().strftime("%Y%m%d")

    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "date": date,
        "dpt": "wzchanges",
        "code": stock_code,
        "market": market,
    }

    resp = requests.get(_DETAIL_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("rc") != 0:
        raise RuntimeError(f"接口返回异常，rc={data.get('rc')}")

    body = data.get("data")
    if body is None:
        return []

    items = body.get("data", [])
    result = []

    for item in items:
        # 价格需除以100
        price = item.get("p", 0)
        try:
            price = round(float(price) / 100, 2)
        except (ValueError, TypeError):
            price = "-"

        # 异动时间格式化（补零）
        tm = str(item.get("tm", ""))
        if len(tm) == 5:
            tm = "0" + tm

        # 异动类型编码
        change_type = str(item.get("t", ""))

        result.append({
            "time":        tm,
            "type":        item.get("t", "-"),
            "type_name":   CHANGE_TYPE_MAP.get(change_type, change_type),
            "price":       price,
            "change_pct":  item.get("u", "-"),
            "volume":      item.get("v", "-"),
        })

    return result