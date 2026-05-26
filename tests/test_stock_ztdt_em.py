"""
测试: 东方财富涨跌停模块
"""

from levistock.stock.stock_ztdt_em import (
    stock_zt_pool_em,
    stock_dt_pool_em,
    stock_yesterday_zt_em,
)

DATE_TODAY   = None         # 今天
DATE_HISTORY = "20260513"   # 历史


def test_stock_zt_pool_em():
    data = stock_zt_pool_em()
    print(f"\n=== 今日涨停 ({len(data)}只) ===")
    for item in data[:3]:
        print(f"{item['stock_code']} {item['stock_name']} 连板:{item['continuous']} 换手:{item['turnover_rate']}%")

    data_history = stock_zt_pool_em(date=DATE_HISTORY)
    print(f"\n=== 历史涨停 {DATE_HISTORY} ({len(data_history)}只) ===")
    if data_history:
        print(f"第一条: {data_history[0]}")
    else:
        print("当日无涨停数据或非交易日")

    try:
        stock_zt_pool_em(date="2026-05-13")
    except ValueError as e:
        print(f"\n日期格式错误: {e}")


def test_stock_dt_pool_em():
    data = stock_dt_pool_em()
    print(f"\n=== 今日跌停 ({len(data)}只) ===")
    for item in data[:3]:
        print(f"{item['stock_code']} {item['stock_name']} 连续跌停:{item['days']}天 换手:{item['turnover_rate']}%")

    data_history = stock_dt_pool_em(date=DATE_HISTORY)
    print(f"\n=== 历史跌停 {DATE_HISTORY} ({len(data_history)}只) ===")
    if data_history:
        print(f"第一条: {data_history[0]}")
    else:
        print("当日无跌停数据或非交易日")

def test_stock_yesterday_zt_em():
    data = stock_yesterday_zt_em()
    print(f"\n=== 昨日涨停今日表现 ({len(data)}只) ===")
    for item in data[:3]:
        print(f"{item['stock_code']} {item['stock_name']} 今日:{item['change_pct']}% 高开:{item['open_ratio']}% 昨连板:{item['yesterday_cont']}")

if __name__ == "__main__":
    test_stock_zt_pool_em()
    test_stock_dt_pool_em()
    test_stock_yesterday_zt_em()