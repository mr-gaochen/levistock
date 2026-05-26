"""
测试开盘红复盘接口 fuplan_kph.py
"""

from levistock.stock.stock_fupanla_kph import get_zttt, get_pmsl, get_his_limit_resumption
import json

DATE = "2026-05-21"

print("=" * 50)
print(f"[1] 涨停天梯 {DATE}")
print("=" * 50)
res = get_zttt(DATE)
stock_list = res.get("StockList", [])
print(f"共 {len(stock_list)} 只连板股")
for s in stock_list[:5]:
    print(f"  {s[0]} {s[1]} {s[2]}连板 板块:{s[5]}")

print()
print("=" * 50)
print(f"[2] 盘面梳理 {DATE}")
print("=" * 50)
res = get_pmsl(DATE)
lst = res.get("List", [])
print(f"共 {len(lst)} 条事件")
for item in lst[:5]:
    print(f"  [{item['TagName']}] {item['Detail']}")

print()
print("=" * 50)
print(f"[3] 历史涨停复盘 {DATE}")
print("=" * 50)
res = get_his_limit_resumption(DATE)
nums = res.get("nums", {})
print(f"涨停:{nums.get('ZT')} 跌停:{nums.get('DT')} 占比:{nums.get('ZBL')}%")
plates = res.get("list", [])
print(f"共 {len(plates)} 个板块")
for plate in plates[:3]:
    print(f"\n  板块: {plate['ZSName']}")
    for s in plate.get("StockList", [])[:3]:
        print(f"    {s[0]} {s[1]} {s[9]} 原因:{s[16]} | {s[17][:40]}...")