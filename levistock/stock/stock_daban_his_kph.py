"""
开盘红 - 历史打板数据模块

数据源: 开盘红 (kaipanhong.com)
模块说明: 提供A股历史涨停、跌停、风向标列表数据
注意: 仅支持历史日期查询，当日数据由 TCP 长连接推送无法获取
"""

import requests

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

_PID_LIMIT_UP   = "4"   # 涨停
_PID_LIMIT_DOWN = "3"   # 跌停
_PID_WIND_VANE  = "6"   # 风向标


def _post(params: dict) -> dict:
    data = {**_BASE_PARAMS, **params}
    resp = requests.post(_HOST, headers=_HEADERS, data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _parse_limit_up(row: list) -> dict:
    """解析涨停/风向标数据行"""
    return {
        "code":          row[0],   # 股票代码
        "name":          row[1],   # 股票名称
        "limit_time":    row[6],   # 最后涨停时间戳
        "open_time":     row[7],   # 开板时间戳（0=未开板）
        "seal_amount":   row[8],   # 封单量
        "limit_tag":     row[9],   # 连板标签（首板/二板...）
        "limit_count":   row[10],  # 连板数
        "themes":        row[11],  # 题材
        "net_inflow":    row[12],  # 净流入（元）
        "turnover":      row[13],  # 成交额（元）
        "turnover_rate": row[14],  # 换手率%
        "market_cap":    row[15],  # 流通市值（元）
        "reason":        row[16],  # 涨停原因
        "seal_money":    row[23],  # 封单金额（元）
        "industry_id":   row[26],  # 行业ID
        "industry_zt":   row[27],  # 同行业涨停数
    }


def _parse_limit_down(row: list) -> dict:
    """解析跌停数据行"""
    return {
        "code":          row[0],   # 股票代码
        "name":          row[1],   # 股票名称
        "limit_time":    row[6],   # 跌停时间戳
        "open_time":     row[7],   # 开板时间戳（0=未开板）
        "seal_amount":   row[8],   # 封单量
        "themes":        row[11],  # 题材
        "net_inflow":    row[12],  # 净流入（元）
        "turnover":      row[13],  # 成交额（元）
        "turnover_rate": row[14],  # 换手率%
        "market_cap":    row[15],  # 流通市值（元）
        "seal_money":    row[23],  # 封单金额（元）
        "industry_id":   row[26],  # 行业ID
    }


def _fetch_daban(pid: str, date: str, parser) -> list:
    from datetime import datetime, date as date_type
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，实际传入：{date}")
    if parsed_date >= date_type.today():
        raise ValueError(f"日期必须小于今天，实际传入：{date}")

    type_map = {"4": "6", "3": "6", "6": "6"}
    page_size = 50
    index = 0
    all_data = []

    while True:
        result = _post({
            "a": "HisDaBanList", "c": "HisHomeDingPan",
            "Order": "1", "st": str(page_size), "Index": str(index), "Is_st": "1",
            "PidType": pid, "Type": type_map[pid],
            "FilterMotherboard": "0", "Filter": "0", "FilterTIB": "0", "FilterGem": "0",
            "Day": date,
        })
        if result.get("errcode") != "0":
            raise RuntimeError(f"接口返回异常，errcode={result.get('errcode')}")
        batch = result.get("list", [])
        all_data.extend([parser(row) for row in batch])
        if len(batch) < page_size:
            break
        index += page_size

    return all_data


def limit_up_his_kph(date: str) -> list:
    """
    获取历史涨停股列表（开盘红）

    数据源: 开盘红
    注意: 仅支持历史日期查询

    Args:
        date (str): 交易日期，格式 "YYYY-MM-DD"，如 "2026-05-13"

    Returns:
        list[dict]: 涨停股列表，每条包含：

        =============== ====================== ====================
        字段名           说明                    示例
        =============== ====================== ====================
        code             股票代码               "601126"
        name             股票名称               "四方股份"
        reason           涨停原因               "智能电网"
        themes           题材                   "固态变压器、智能电网"
        industry_id      行业ID                 "801346"
        industry_zt      同行业涨停数            11
        limit_tag        连板标签               "首板"
        limit_count      连板数                 1
        limit_time       最后涨停时间戳          1778655105
        open_time        开板时间戳（0=未开板）   0
        seal_amount      封单量                 75845056
        seal_money       封单金额（元）          160656208
        turnover         成交额（元）            2581487973
        turnover_rate    换手率%                6.65
        net_inflow       净流入（元）            27697971
        market_cap       流通市值（元）          40196945337
        change_pct       涨幅%                  6.65
        =============== ====================== ====================

    Example:
        >>> import levistock as lk
        >>> data = lk.limit_up_his_kph(date="2026-05-13")
        >>> print(f"涨停数: {len(data)}")
        >>> print(data[0]['name'], data[0]['reason'])
    """
    return _fetch_daban(_PID_LIMIT_UP, date, _parse_limit_up)


def limit_down_his_kph(date: str) -> list:
    """
    获取历史跌停股列表（开盘红）

    Args:
        date (str): 交易日期，格式 "YYYY-MM-DD"

    Returns:
        list[dict]: 跌停股列表，每条包含：

        =============== ====================== ====================
        字段名           说明                    示例
        =============== ====================== ====================
        code             股票代码               "002810"
        name             股票名称               "山东赫达"
        themes           题材                   "化工、锂电池"
        industry_id      行业ID                 ""
        limit_time       跌停时间戳             1778655195
        open_time        开板时间戳（0=未开板）   0
        seal_amount      封单量                 11501579
        seal_money       封单金额（元）          0
        turnover         成交额（元）            653089606
        turnover_rate    换手率%                11.49
        net_inflow       净流入（元）            -73850455
        market_cap       流通市值（元）          5246474299
        =============== ====================== ====================

    Example:
        >>> import levistock as lk
        >>> data = lk.limit_down_his_kph(date="2026-05-13")
        >>> print(f"跌停数: {len(data)}")
    """
    return _fetch_daban(_PID_LIMIT_DOWN, date, _parse_limit_down)


def wind_vane_his_kph(date: str) -> list:
    """
    获取历史风向标列表（开盘红）

    Args:
        date (str): 交易日期，格式 "YYYY-MM-DD"

    Returns:
        list[dict]: 风向标股票列表，字段同 limit_up_his_kph

    Example:
        >>> import levistock as lk
        >>> data = lk.wind_vane_his_kph(date="2026-05-13")
        >>> print(f"风向标数: {len(data)}")
        >>> for s in data[:5]:
        ...     print(s['name'], s['change_pct'], s['themes'])
    """
    return _fetch_daban(_PID_WIND_VANE, date, _parse_limit_up)