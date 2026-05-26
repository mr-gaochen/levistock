"""
财联社板块热度接口封装 (CLS)
- get_sector_heat(): 板块热度排行
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


def get_sector_heat() -> list:
    """
    板块热度排行（实时）
    :return: [
        {
            "plate_code":   str   板块代码 (如 'cls80195')
            "plate_name":   str   板块名称 (如 '半导体芯片')
            "rank":         int   当前热度排名
            "cur_heat":     float 当前热度值
            "rank_change":  int   排名变化 (正数=上升, 负数=下降)
            "is_new":       int   是否新上榜 (1=是, 0=否)
        },
        ...
    ]
    """
    params = {**_BASE_PARAMS}
    params["sign"] = _make_sign(params)
    r = requests.get(
        f"{_HOST}/v2/quote/a/plate/plate_heat_list",
        params=params,
        headers=_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("data", [])

def get_sector_popular_stocks(plate_code: str) -> list:
    """
    获取板块近期热门股（财联社）

    接口地址: https://x-quote.cls.cn/v2/quote/a/plate/popular_stocks
    更新频率: 交易日实时更新

    Args:
        plate_code (str): 板块代码，如 "cls80025"
                          可通过 market_wind_cls() 或 get_sector_heat() 获取

    Returns:
        list[dict]:
            secu_code  str   股票代码（含市场前缀），如 "sz002552"
            secu_name  str   股票名称
            change     str   涨跌幅，如 "+10.00%"
            change_px  float 涨跌额
            tbm        str   连板描述，如 "12天7板"
            head_num   int   龙头排名（0表示非龙头）

    Raises:
        ValueError: plate_code 为空时抛出
        RuntimeError: 接口返回异常时抛出
    """
    if not plate_code:
        raise ValueError("plate_code 不能为空")

    params = {**_BASE_PARAMS, "plate_code": plate_code}
    params["sign"] = _make_sign(params)
    r = requests.get(
        f"{_HOST}/v2/quote/a/plate/popular_stocks",
        params=params,
        headers=_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        raise RuntimeError(f"接口返回异常：{data}")

    result = []
    for item in data.get("data", []):
        result.append({
            "secu_code": item.get("secu_code", ""),
            "secu_name": item.get("secu_name", ""),
            "change":    item.get("change", ""),
            "change_px": item.get("change_px", 0),
            "tbm":       item.get("tbm", ""),
            "head_num":  item.get("head_num", 0),
        })
    return result
