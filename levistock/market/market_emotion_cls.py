"""
财联社 - 市场情绪模块

数据源: 财联社 (cls.cn)
模块说明: 提供A股市场情绪数据接口，包括涨跌分布、市场热度、涨停表现等
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.cls.cn/",
}

_EMOTION_URL = "https://x-quote.cls.cn/v2/quote/a/stock/emotion"


def market_emotion_cls() -> dict:
    """
    获取A股市场情绪数据（财联社）

    数据源: 财联社
    接口地址: https://x-quote.cls.cn/v2/quote/a/stock/emotion
    更新频率: 交易日实时更新

    Returns:
        dict: 市场情绪数据，包含以下字段：

        基础行情:
            market_degree           市场热度(0-100)              "59"
            shsz_balance            两市成交额                   "3.14万亿"
            shsz_balance_change_px  成交额较上日变化              "-829亿"
            preview_balance         今日预测量能                  "3.14万亿"
            preview_balance_change_px 预测量能较上日变化          "-829亿"

        涨停表现:
            up_ratio                封板率                       "76.00%"
            up_ratio_num            封板数量                     "100"
            up_open_num             触及涨停数量                  "31"
            performance             昨涨停今表现                  "3.81%"
            up_open_ratio           高开率                       "73%"
            profit_ratio            获利率                       "82%"

        涨跌分布(up_down_dis):
            rise_num                上涨家数                     3520
            fall_num                下跌家数                     1832
            flat_num                持平家数                     161
            up_num                  涨停家数                     127
            down_num                跌停家数                     54
            suspend_num             停牌家数                     20
            up_2                    涨幅0-2%家数                 1901
            up_4                    涨幅2-4%家数                 922
            up_6                    涨幅4-6%家数                 349
            up_8                    涨幅6-8%家数                 150
            up_10                   涨幅8-10%家数(含涨停)         198
            down_2                  跌幅0-2%家数                 1407
            down_4                  跌幅2-4%家数                 259
            down_6                  跌幅4-6%家数                 119
            down_8                  跌幅6-8%家数                 30
            down_10                 跌幅8-10%家数(含跌停)         17

        连板分布(limit_up_board):
            一板/二板/三板/高度板    各连板数量及连板率

    Raises:
        RuntimeError: 接口返回异常时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> data = lk.market_emotion_cls()
        >>> print(f"市场热度: {data['market_degree']}")
        >>> print(f"上涨家数: {data['up_down_dis']['rise_num']}")
        >>> print(f"下跌家数: {data['up_down_dis']['fall_num']}")
        >>> print(f"涨停家数: {data['up_down_dis']['up_num']}")
        >>> print(f"封板率: {data['up_ratio']}")
    """
    params = {
        "app": "CailianpressWeb",
        "os": "web",
        "sv": "8.4.6",
        "sign": "9f8797a1f4de66c2370f7a03990d2737",
    }

    resp = requests.get(_EMOTION_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 200:
        raise RuntimeError(f"接口返回异常，code={data.get('code')}，msg={data.get('msg')}")

    body = data.get("data", {})

    # 连板分布转换为更易读的格式
    limit_up_board = {}
    raw_board = body.get("limit_up_board", {})
    if raw_board:
        row1 = raw_board.get("row1", [])  # 板块名称
        row2 = raw_board.get("row2", [])  # 数量
        row3 = raw_board.get("row3", [])  # 连板率（第一个是"连板率"文字）
        for i, name in enumerate(row1):
            limit_up_board[name] = {
                "count":      row2[i] if i < len(row2) else "-",
                "continuous_rate": row3[i + 1] if i + 1 < len(row3) else "-",
            }

    return {
        # 基础行情
        "market_degree":              body.get("market_degree", "-"),
        "shsz_balance":               body.get("shsz_balance", "-"),
        "shsz_balance_change_px":     body.get("shsz_balance_change_px", "-"),
        "preview_balance":            body.get("preview_balance", "-"),
        "preview_balance_change_px":  body.get("preview_balance_change_px", "-"),
        # 涨停表现
        "up_ratio":                   body.get("up_ratio", "-"),
        "up_ratio_num":               body.get("up_ratio_num", "-"),
        "up_open_num":                body.get("up_open_num", "-"),
        "performance":                body.get("performance", "-"),
        "up_open_ratio":              body.get("up_open_ratio", "-"),
        "profit_ratio":               body.get("profit_ratio", "-"),
        # 涨跌分布
        "up_down_dis":                body.get("up_down_dis", {}),
        # 连板分布
        "limit_up_board":             limit_up_board,
    }
