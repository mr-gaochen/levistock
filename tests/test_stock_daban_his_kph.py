"""
测试: 开盘红历史打板数据模块
"""

from levistock.stock.stock_daban_his_kph import (
    limit_up_his_kph,
    limit_down_his_kph,
    wind_vane_his_kph,
)

DATE = "2026-05-13"

def test_limit_up_his_kph():
    data = limit_up_his_kph(date=DATE)
    print(f"\n=== 涨停 ({len(data)}只) ===")
    for s in data[:5]:
        print(f"{s['code']} {s['name']} 换手:{s['turnover_rate']}% "
              f"原因:{s['reason']} 题材:{s['themes']} 连板:{s['limit_count']}")


def test_limit_down_his_kph():
    data = limit_down_his_kph(date=DATE)
    print(f"\n=== 跌停 ({len(data)}只) ===")
    for s in data[:5]:
        print(f"{s['code']} {s['name']} 换手:{s['turnover_rate']}% 题材:{s['themes']}")


def test_wind_vane_his_kph():
    data = wind_vane_his_kph(date=DATE)
    print(f"\n=== 风向标 ({len(data)}只) ===")
    for s in data[:5]:
        print(f"{s['code']} {s['name']} 换手:{s['turnover_rate']}% 题材:{s['themes']}")


if __name__ == "__main__":
    test_limit_up_his_kph()
    test_limit_down_his_kph()
    test_wind_vane_his_kph()