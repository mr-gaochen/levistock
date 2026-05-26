"""
开盘红复盘接口封装 (kaipanhong)
- 涨停天梯: get_zttt(date)
- 盘面梳理: get_pmsl(date)
- 历史涨停复盘: get_his_limit_resumption(date)

历史数据用 apphis，当天实时用 apphwshhq
"""

import requests
from datetime import date as _date

_HOST_REALTIME = "https://apphwshhq.kaipanhong.com/w1/api/index.php"
_HOST_HISTORY  = "https://apphis.kaipanhong.com/w1/api/index.php"

_BASE_PARAMS = {
    "PhoneOSNew": "1",
    "DeviceID":   "1a609dd6-b2b8-3bf9-ac40-a77581551454",
    "VerSion":    "6.0.6",
    "Token":      "0",
    "Red":        "1",
    "apiv":       "w45",
    "UserID":     "0",
}

_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent":   "Dalvik/2.1.0 (Linux; U; Android 12; 2206123SC Build/c069a49.2)",
    "Accept-Encoding": "gzip",
}


def _today_str() -> str:
    return _date.today().strftime("%Y-%m-%d")


def _post(host: str, params: dict) -> dict:
    data = {**_BASE_PARAMS, **params}
    r = requests.post(host, data=data, headers=_HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def _is_today(date_str: str) -> bool:
    return date_str == _today_str()


def get_zttt(date: str = None) -> dict:
    """
    涨停天梯
    :param date: 日期字符串 'YYYY-MM-DD'，默认今天
    :return: {
        "StockList": [
            [
                [0]  str   股票代码
                [1]  str   股票名称
                [2]  int   连板数
                [3]  int   涨停时间戳(秒)
                [4]  str   所属板块代码 (如 '801001')
                [5]  str   所属板块名称 (如 '芯片')
                [6]  int   是否大单一字 (1=是, 0=否)
                [7]  int   是否有人气 (1=是, 0=否)
                [8]  int   板块涨停股数量
                [9]  int   个股成交额(元)
                [10] int   板块成交额(元)
            ],
            ...
        ]
    }
    """
    d = date or _today_str()
    host = _HOST_REALTIME if _is_today(d) else _HOST_HISTORY
    params = {
        "a": "GetZhangTingTianTi",
        "c": "FuPanLa",
        "Date": d,
    }
    return _post(host, params)


def get_pmsl(date: str = None, st: int = 30, index: int = 0) -> dict:
    """
    盘面梳理（板块事件流）
    :param date:  日期字符串 'YYYY-MM-DD'，默认今天
    :param st:    返回条数，默认30
    :param index: 分页起始，默认0
    :return: {
        "List": [
            {
                "TimeMin":    int   事件时间戳(秒)
                "TagID":      int   事件类型ID
                "TagName":    str   事件类型名称
                                    ('大单一字'/'直线拉升'/'权重拉升'/'趋势新高'/'人气股杀跌'/...)
                "TagShuXing": int   事件属性 (2=正面, 0=负面, 1=中性)
                "ZSCode":     str   板块代码 (如 '801001')
                "ZSName":     str   板块名称 (如 '芯片')
                "Detail":     str   事件描述文字
                "StockList":  list  [[股票代码, 股票名称], ...]
            },
            ...
        ]
    }
    """
    d = date or _today_str()
    host = _HOST_REALTIME if _is_today(d) else _HOST_HISTORY
    params = {
        "a":     "GetPMSL_PMLD",
        "c":     "FuPanLa",
        "st":    str(st),
        "Index": str(index),
        "Date":  d,
    }
    return _post(host, params)


def get_his_limit_resumption(date: str = None, st: int = 100, index: int = 0) -> dict:
    """
    历史涨停复盘（含涨停原因详细文字）
    :param date:  日期字符串 'YYYY-MM-DD'，默认今天
    :param st:    返回条数，默认100
    :param index: 分页起始，默认0
    :return: {
        "nums": {"ZT", "DT", "ZBL", ...},
        "list": [{"ZSCode", "ZSName", "StockList": [[code, name, ..., reason_short, reason_detail], ...]}, ...]
    }
    StockList 字段索引:
        [0]  股票代码
        [1]  股票名称
        [9]  连板描述 ('首板'/'2连板'/...)
        [10] 连板数
        [11] 所属概念
        [16] 涨停原因简短标签
        [17] 涨停原因详细文字
    """
    d = date or _today_str()
    params = {
        "a":     "GetPlateInfo_w38",
        "c":     "HisLimitResumption",
        "st":    str(st),
        "Index": str(index),
        "Date":  d,
    }
    return _post(_HOST_HISTORY, params)