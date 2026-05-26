"""
财联社 - 行业板块模块

数据源: 财联社 (cls.cn)
模块说明: 提供A股行业板块实时行情数据接口，按涨跌幅排序
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.cls.cn/",
}

_SECTOR_URL = "https://x-quote.cls.cn/web_quote/plate/plate_list"


def sector_industry_cls() -> list:
    """
    获取A股行业板块实时行情（财联社）

    数据源: 财联社
    接口地址: https://x-quote.cls.cn/web_quote/plate/plate_list
    更新频率: 交易日实时更新
    排序方式: 按涨跌幅从高到低排序

    Returns:
        list[dict]: 行业板块列表，每条数据包含以下字段：

        =============== ====================== ====================
        字段名           说明                    示例
        =============== ====================== ====================
        secu_name        板块名称               "通信"
        secu_code        板块代码               "cls82074"
        change           涨跌幅                 0.0321
        main_fund_diff   主力净流入(元)          9579774954
        limit_up         上涨家数               102
        limit_down       下跌家数               14
        limit_up_num     涨停家数               7
        limit_down_num   跌停家数               0
        trade_status     交易状态               "ENDTR"
        first_stock      领涨股信息(dict):
                           - secu_name: 股票名称
                           - secu_code: 股票代码
                           - last_px:   现价
                           - change:    涨跌幅
                           - tr:        换手率
        =============== ====================== ====================

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.sector_industry_cls()
        >>> print(f"共 {len(data)} 个行业板块")
        >>> print(data[0])
        >>>
        >>> # 按主力净流入排序
        >>> sorted_data = sorted(data, key=lambda x: x["main_fund_diff"], reverse=True)
        >>> print(f"主力流入最多: {sorted_data[0]['secu_name']}")
        >>>
        >>> # 按涨跌幅排序（接口默认已排序）
        >>> print(f"涨幅最大: {data[0]['secu_name']} {data[0]['change']*100:.2f}%")
    """
    params = {
        "app": "CailianpressWeb",
        "os": "web",
        "page": 5,
        "rever": 1,
        "sv": "8.4.6",
        "type": "industry",
        "way": "change",
        "sign": "ef1ec7886be706a0b722d7e7bf3c0054",
    }

    resp = requests.get(_SECTOR_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(
            f"接口返回异常，code={data.get('code')}，msg={data.get('msg')}"
        )

    plate_list = data.get("data", {}).get("plate_data", [])

    result = []
    for item in plate_list:
        result.append({
            "secu_name":      item.get("secu_name", ""),
            "secu_code":      item.get("secu_code", ""),
            "change":         item.get("change", 0),
            "main_fund_diff": item.get("main_fund_diff", 0),
            "limit_up":       item.get("limit_up", 0),
            "limit_down":     item.get("limit_down", 0),
            "limit_up_num":   item.get("limit_up_num", 0),
            "limit_down_num": item.get("limit_down_num", 0),
            "trade_status":   item.get("trade_status", ""),
            "first_stock":    item.get("first_stock", {}),
        })

    return result
