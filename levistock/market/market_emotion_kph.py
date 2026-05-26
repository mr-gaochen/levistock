"""
开盘红 - 市场情绪模块

数据源: 开盘红 (kaipanhong.com)
模块说明: 提供A股市场情绪数据，不传日期查今天实时，传历史日期查历史
"""

import requests
from datetime import date as date_type

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

_HOST_REALTIME = "https://apphwshhq.kaipanhong.com/w1/api/index.php"
_HOST_HISTORY  = "https://apphis.kaipanhong.com/w1/api/index.php"


def market_emotion_kph(date: str = None) -> dict:
    """
    获取A股市场情绪数据（开盘红）

    数据源: 开盘红
    不传日期或传今天日期 → 实时接口（apphwshhq）
    传历史日期 → 历史接口（apphis）

    Args:
        date (str): 交易日期，格式 "YYYY-MM-DD"，不传默认今天

    Returns:
        dict: 市场情绪数据，包含以下字段：

        涨跌停统计:
            zt              涨停总数                        112
            dt              跌停总数                        2
            sjzt            实际涨停（非ST）                 95
            sjdt            实际跌停（非ST）                 2
            stzt            ST涨停                         17
            stdt            ST跌停                         0

        市场概况:
            rise_num        上涨家数                        3036
            fall_num        下跌家数                        2008
            sign            市场人气判断                    "题材炒作热度高"
            flat            平盘股票数                      139

        涨跌分布:
            rise_dist       各涨幅区间股票数 {1:xx, 2:xx ... 10:xx}
            fall_dist       各跌幅区间股票数 {-1:xx, -2:xx ... -10:xx}

        成交额:
            szln            沪市成交额（元）
            qscln           全市成交额（元）
            s_zrcs          昨日沪市成交额（元）
            q_zrcs          昨日全市成交额（元）

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.market_emotion_kph()                   # 今天实时
        >>> data = lk.market_emotion_kph(date="2026-05-13")  # 历史
        >>> print(f"涨停: {data['zt']}只")
        >>> print(f"市场人气: {data['sign']}")
    """
    today = date_type.today().strftime("%Y-%m-%d")
    is_today = (date is None) or (date == today)

    if is_today:
        host   = _HOST_REALTIME
        params = {**_BASE_PARAMS, "a": "ZhangFuDetail", "c": "HomeDingPan"}
    else:
        host   = _HOST_HISTORY
        params = {**_BASE_PARAMS, "a": "HisZhangFuDetail", "c": "HisHomeDingPan", "Day": date}

    resp = requests.post(host, headers=_HEADERS, data=params, timeout=10)
    resp.raise_for_status()
    result = resp.json()

    if result.get("errcode") != "0":
        raise RuntimeError(f"接口返回异常，errcode={result.get('errcode')}")

    info = result.get("info", {})

    return {
        "zt":        info.get("ZT", 0),
        "dt":        info.get("DT", 0),
        "sjzt":      int(info.get("SJZT", 0)),
        "sjdt":      int(info.get("SJDT", 0)),
        "stzt":      int(info.get("STZT", 0)),
        "stdt":      int(info.get("STDT", 0)),
        "rise_num":   info.get("SZJS", 0),
        "fall_num":   info.get("XDJS", 0),
        "sign":      info.get("sign", ""),
        "flat":      int(info.get("0", 0)),
        "rise_dist": {i: int(info.get(str(i), 0)) for i in range(1, 11)},
        "fall_dist": {i: int(info.get(str(i), 0)) for i in range(-1, -11, -1)},
        "szln":      info.get("szln", 0),
        "qscln":     info.get("qscln", 0),
        "s_zrcs":    info.get("s_zrcs", 0),
        "q_zrcs":    info.get("q_zrcs", 0),
    }