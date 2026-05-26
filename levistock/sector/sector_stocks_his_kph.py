"""
开盘红 - 历史成分股模块

数据源: 开盘红 (kaipanhong.com)
模块说明: 提供A股精选/行业/地区板块历史成分股数据
注意: 仅支持历史日期查询，日期必须小于今天
"""

import requests
from datetime import datetime, date as date_type

_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent":   "Dalvik/2.1.0 (Linux; U; Android 12; 2206123SC Build/c069a49.2)",
    "Accept-Encoding": "gzip",
}

_BASE_PARAMS = {
    "PhoneOSNew": "1",
    "DeviceID":   "1a609dd6-b2b8-3bf9-ac40-a77581551454",
    "VerSion":    "6.0.6",
    "Token":      "0",
    "UserID":     "0",
    "Red":        "1",
    "apiv":       "w45",
}

_HOST = "https://apphis.kaipanhong.com/w1/api/index.php"

# 股票字段映射
_STOCK_FIELDS = {
    0:  "code",           # 股票代码
    1:  "name",           # 股票名称
    4:  "tags",           # 概念标签
    5:  "price",          # 现价
    6:  "change_pct",     # 涨跌幅%
    7:  "amount",         # 成交额（元）
    8:  "turnover_rate",  # 换手率%
    10: "float_amount",   # 流通市值
    11: "main_buy",       # 主力买入
    12: "main_sell",      # 主力卖出
    13: "main_net",       # 主力净额
    14: "buy_ratio",      # 主买占比%
    15: "sell_ratio",     # 主卖占比%
    16: "net_ratio",      # 净额占比%
    23: "limit_tag",      # 连板标签（首板/2连板）
    24: "rank_tag",       # 龙虎榜（龙一/龙二）
    33: "recent_chg",     # 近期涨幅%
    40: "limit_count",    # 近期涨停次数
    62: "chg_1d",         # 1日涨幅%
    63: "chg_5d",         # 5日涨幅%
    64: "chg_20d",        # 20日涨幅%
}


def _parse_stock(row: list) -> dict:
    return {_STOCK_FIELDS.get(i, f"f{i}"): v for i, v in enumerate(row)
            if i in _STOCK_FIELDS}


def sector_stocks_his_kph(plate_id: str, date: str) -> list:
    """
    获取历史板块成分股（开盘红）

    数据源: 开盘红
    接口地址: https://apphis.kaipanhong.com/w1/api/index.php
    注意: 仅支持历史日期查询，日期必须小于今天

    Args:
        plate_id (str): 板块ID，必填，如 "801001"
                        可通过 sector_ranking_kph() 获取各板块ID
        date     (str): 交易日期，必填，格式 "YYYY-MM-DD"，必须小于今天

    Returns:
        list[dict]: 成分股列表，每条数据包含以下字段：

        =============== ====================== ====================
        字段名           说明                    示例
        =============== ====================== ====================
        code             股票代码               "000001"
        name             股票名称               "平安银行"
        price            现价(元)               11.50
        change_pct       涨跌幅(%)              0.35
        amount           成交额(元)             123456789.0
        turnover_rate    换手率(%)              0.21
        float_amount     流通市值(元)            220000000000.0
        main_buy         主力买入(元)            12345678.0
        main_sell        主力卖出(元)            11234567.0
        main_net         主力净额(元)            1111111.0
        buy_ratio        主买占比(%)            45.0
        sell_ratio       主卖占比(%)            43.0
        net_ratio        净额占比(%)            2.0
        tags             概念标签               "银行、沪深300"
        limit_tag        连板标签               "首板"
        rank_tag         龙虎榜标签             "龙一"
        recent_chg       近期涨幅(%)            5.50
        limit_count      近期涨停次数           2
        chg_1d           1日涨幅(%)             0.35
        chg_5d           5日涨幅(%)             2.10
        chg_20d          20日涨幅(%)            8.50
        =============== ====================== ====================

    Raises:
        ValueError: plate_id/date 为空、日期格式错误或日期不小于今天时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> stocks = lk.sector_stocks_his_kph(plate_id="801001", date="2026-05-13")
        >>> print(f"成分股数: {len(stocks)}")
        >>> print(stocks[0]['name'], stocks[0]['change_pct'])
    """
    if not plate_id:
        raise ValueError("plate_id 不能为空")
    if not date:
        raise ValueError("date 不能为空")

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，实际传入：{date}")

    if parsed_date >= date_type.today():
        raise ValueError(f"日期必须小于今天，实际传入：{date}")

    page_size = 1000
    index = 0
    all_data = []

    while True:
        params = {
            **_BASE_PARAMS,
            "a":          "ZhiShuStockList_W8",
            "c":          "ZhiShuRanking",
            "Order":      "1",
            "st":         str(page_size),
            "old":        "1",
            "Index":      str(index),
            "Date":       date,
            "Type":       "6",
            "PlateID":    plate_id,
            "IsZZ":       "0",
            "IsKZZType":  "0",
            "TSZB":       "0",
            "TSZB_Type":  "0",
            "filterType": "0",
        }
        resp = requests.post(_HOST, headers=_HEADERS, data=params, timeout=30)
        resp.raise_for_status()
        result = resp.json()

        if result.get("errcode") not in ("0", 0):
            raise RuntimeError(f"接口返回异常，errcode={result.get('errcode')}")

        batch = result.get("list", [])
        all_data.extend([_parse_stock(row) for row in batch])

        if len(batch) == page_size:
            index += page_size
        else:
            break

    return all_data