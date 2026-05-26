"""
财联社板块轮动接口封装 (CLS)
- get_sector_rotation(days): 板块轮动（近N日top10板块涨跌幅）
"""

import hashlib
import requests

_HOST = "https://x-quote.cls.cn"

_BASE_PARAMS = {
    "app":           "cailianpress",
    "sv":            "8.7.4",
    "os":            "android",
    "mb":            "Xiaomi-2206123SC",
    "ov":            "32",
    "channel":       "8",
    "motif":         "0",
    "net":           "",
    "province_code": "3205",
    "token":         "",
    "uid":           "",
}

_HEADERS = {
    "User-Agent": "okhttp/4.9.0",
    "Cls-Uuid":   "3728ab7e99d850a0",
}


def _make_sign(params: dict) -> str:
    sorted_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sha1 = hashlib.sha1(sorted_str.encode()).hexdigest()
    return hashlib.md5(sha1.encode()).hexdigest()


def get_sector_rotation(days: int = 4) -> list:
    """
    板块轮动（近N个交易日每日top10板块涨跌幅）
    :param days: 查询天数，默认4
    :return: [
        {
            "trade_date": str   交易日期 (如 '2026-05-22')
            "plates": [
                {
                    "plate_code": str   板块代码 (如 'cls80424')
                    "plate_name": str   板块名称 (如 'MLCC')
                    "change":     float 当日涨跌幅(%) (正=涨, 负=跌)
                },
                ...   # 每天最多10个板块，按涨跌幅降序
            ]
        },
        ...   # 按日期降序，第一条为最新交易日
    ]
    """
    params = {**_BASE_PARAMS, "days": str(days)}
    params["sign"] = _make_sign(params)
    r = requests.get(
        f"{_HOST}/v2/quote/a/plate/rotation",
        params=params,
        headers=_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("data", [])
