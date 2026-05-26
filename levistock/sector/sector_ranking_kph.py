"""
开盘红 - 板块排行模块

数据源: 开盘红 (kaipanhong.com)
模块说明: 提供A股精选/行业/地区板块排行数据
今天 → 实时接口（apphwshhq）
历史 → 历史接口（apphis）
"""

import requests
from datetime import datetime, date as date_type
from tqdm import tqdm

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

# 板块类型
SECTOR_SELECTED  = "7"   # 精选
SECTOR_INDUSTRY  = "4"   # 行业
SECTOR_REGION    = "6"   # 地区

# 板块字段映射
_PLATE_FIELDS = {
    0:  "plate_id",       # 板块ID
    1:  "plate_name",     # 板块名称
    2:  "amount",         # 成交额（元）
    3:  "change_pct",     # 涨跌幅%
    4:  "amplitude",      # 振幅%
    5:  "net_inflow",     # 净流入（元）
    6:  "net_inflow_5d",  # 5日净流入
    7:  "buy_amount",     # 主买金额
    8:  "sell_amount",    # 主卖金额
    9:  "turnover_rate",  # 换手率%
    10: "market_cap",     # 总市值
    11: "avg_change",     # 平均涨幅
    17: "stock_count",    # 成分股数量
    18: "change_pct2",    # 涨跌幅%（同3）
}


def _parse_plate(row: list) -> dict:
    return {_PLATE_FIELDS.get(i, f"f{i}"): v for i, v in enumerate(row)
            if i in _PLATE_FIELDS}


def sector_ranking_kph(date: str, zs_type: str, fetch_all: bool = False) -> list:
    """
    获取板块排行（开盘红）

    数据源: 开盘红
    今天 → 实时接口（apphwshhq）
    历史 → 历史接口（apphis）

    Args:
        date      (str):  交易日期，格式 "YYYY-MM-DD"，必填
        zs_type   (str):  板块类型，必填
                          SECTOR_SELECTED="7" 精选
                          SECTOR_INDUSTRY="4" 行业
                          SECTOR_REGION="6"   地区
        fetch_all (bool): False=只取前50条（默认），True=分页获取全部

    Returns:
        list[dict]: 板块列表，每条数据包含以下字段：

        =============== ====================== ====================
        字段名           说明                    示例
        =============== ====================== ====================
        plate_id         板块ID                 "801807"
        plate_name       板块名称               "算力"
        change_pct       涨跌幅(%)              2.88
        amount           成交额(元)             123456789.0
        amplitude        振幅(%)                3.50
        net_inflow       净流入(元)              12345678.0
        net_inflow_5d    5日净流入(元)           56789012.0
        buy_amount       主买金额(元)            98765432.0
        sell_amount      主卖金额(元)            87654321.0
        turnover_rate    换手率(%)              5.21
        market_cap       总市值(元)             1234567890000.0
        avg_change       平均涨幅(%)            1.50
        stock_count      成分股数量             50
        =============== ====================== ====================

    Raises:
        ValueError: 日期格式错误或zs_type不合法时抛出
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 今天精选板块
        >>> data = lk.sector_ranking_kph(date="2026-05-14", zs_type=lk.SECTOR_SELECTED)
        >>> # 历史行业排行全量
        >>> data = lk.sector_ranking_kph(date="2026-05-13", zs_type=lk.SECTOR_INDUSTRY, fetch_all=True)
        >>> # 地区排行
        >>> data = lk.sector_ranking_kph(date="2026-05-14", zs_type=lk.SECTOR_REGION)
        >>> print(f"板块数: {len(data)}")
    """
    if not date:
        raise ValueError("date 不能为空")
    if not zs_type:
        raise ValueError("zs_type 不能为空")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，实际传入：{date}")

    if zs_type not in (SECTOR_SELECTED, SECTOR_INDUSTRY, SECTOR_REGION):
        raise ValueError(f"zs_type 不合法，应为 7/4/6，实际传入：{zs_type}")

    today = date_type.today().strftime("%Y-%m-%d")
    host = _HOST_REALTIME if date == today else _HOST_HISTORY
    type_param = "1" if zs_type == SECTOR_SELECTED else "2"

    page_size = 50
    index = 0
    all_data = []
    pbar = None

    while True:
        params = {
            **_BASE_PARAMS,
            "a":      "RealRankingInfo",
            "c":      "ZhiShuRanking",
            "Order":  "1",
            "st":     str(page_size),
            "Index":  str(index),
            "Date":   date,
            "Type":   type_param,
            "ZSType": zs_type,
        }
        resp = requests.post(host, headers=_HEADERS, data=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()

        if result.get("errcode") not in ("0", 0):
            raise RuntimeError(f"接口返回异常，errcode={result.get('errcode')}")

        batch = result.get("list", [])
        all_data.extend([_parse_plate(row) for row in batch])

        if fetch_all and len(batch) == page_size:
            if pbar is None:
                pbar = tqdm(desc="获取板块数据", unit="条", colour="black")
            pbar.update(len(batch))
            index += page_size
        else:
            if pbar is not None:
                pbar.update(len(batch))
                pbar.close()
            break

    return all_data