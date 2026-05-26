"""
问财 - 股票策略查询模块

数据源: i问财 (iwencai.com)
模块说明: 提供A股自然语言策略查询接口
依赖说明: cookie 由 api.levizhang.com 提供，如服务不可用则接口失效
"""

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",
    "Referer": "https://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=3"
               "&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter="
               "&tid=stockpick&w=macd&queryarea=",
    "Host": "www.iwencai.com",
    "X-Requested-With": "XMLHttpRequest",
}

_COOKIE_URL = "https://api.levizhang.com/getCookie"
_WENCAI_URL = "https://www.iwencai.com/stockpick/load-data"


def _get_cookie() -> str:
    """
    从 api.levizhang.com 获取问财所需的 cookie
    注意：依赖外部服务，如服务不可用则抛出异常
    """
    resp = requests.get(_COOKIE_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") == "000000":
        return data.get("data", "")
    raise RuntimeError(f"获取 cookie 失败：{data.get('message')}")


def stock_strategy_wencai(query: str, page: int = 1, limit: int = 50) -> dict:
    """
    i问财自然语言股票策略查询

    数据源: i问财
    接口地址: https://www.iwencai.com/stockpick/load-data
    依赖说明: cookie 由 api.levizhang.com 自动获取，无需用户手动传入

    Args:
        query (str): 自然语言查询条件，如：
                     - "连板3板以上"
                     - "macd金叉 量比大于2"
                     - "近5日涨幅大于10%"
        page  (int): 页码，默认 1
        limit (int): 每页返回条数，默认 50

    Returns:
        dict: 查询结果，包含以下字段：

        ============= ====================== ====================
        字段名         说明                    示例
        ============= ====================== ====================
        title          表头列表               ["股票代码", "股票简称", ...]
        result         数据列表               [[...], [...], ...]
        ============= ====================== ====================

    Raises:
        ValueError: query 为空时抛出
        RuntimeError: 接口返回异常或 cookie 获取失败时抛出
        requests.exceptions.RequestException: 网络请求异常时抛出

    Example:
        >>> import levistock as lk
        >>> # 查询连板3板以上的股票
        >>> data = lk.stock_strategy_wencai(query="连板3板以上")
        >>> print(data["title"])    # 表头
        >>> print(data["result"][0])  # 第一条数据
        >>>
        >>> # 查询 MACD 金叉且量比大于2的股票
        >>> data = lk.stock_strategy_wencai(query="macd金叉 量比大于2")
        >>> print(len(data["result"]))
    """
    if not query:
        raise ValueError("query 不能为空")

    # 自动获取 cookie
    cookie = _get_cookie()

    params = {
        "typed":      1,
        "ts":         1,
        "f":          3,
        "qs":         "result_rewrite",
        "querytype":  "stock",
        "tid":        "stockpick",
        "page":       page,
        "perpage":    limit,
        "w":          query,
    }

    # cookie 需同时放在 Cookie 头和 hexin-v 头
    headers = dict(_HEADERS)
    headers["Cookie"]   = f"v={cookie}"
    headers["hexin-v"]  = cookie

    resp = requests.get(_WENCAI_URL, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        raise RuntimeError(f"接口返回异常：{data.get('message')}")

    result_map = data.get("data", {}).get("result", {})
    if not result_map:
        return {"title": [], "result": []}

    return {
        "title":  result_map.get("title", []),
        "result": result_map.get("result", []),
    }
