"""
测试财联社板块热度接口 sector_heat_cls.py
"""

from levistock.sector.sector_heat_cls import get_sector_heat, get_sector_popular_stocks

print("=" * 50)
print("[1] 板块热度 get_sector_heat")
print("=" * 50)
heat = get_sector_heat()
print(f"共 {len(heat)} 个板块")
for item in heat[:10]:
    new_tag = " [新上榜]" if item["is_new"] else ""
    change = item["rank_change"]
    change_str = f"↑{change}" if change > 0 else (f"↓{abs(change)}" if change < 0 else "-")
    print(f"  {item['rank']:>3}. {item['plate_name']:<12} 热度:{item['cur_heat']:.1f}  排名变化:{change_str}{new_tag}")

print()
print("=" * 50)
print("[2] 板块热门股 get_sector_popular_stocks")
print("=" * 50)
if heat:
    top_plate = heat[0]
    print(f"板块：{top_plate['plate_name']}({top_plate['plate_code']})")
    stocks = get_sector_popular_stocks(top_plate["plate_code"])
    print(f"共 {len(stocks)} 只热门股")
    for s in stocks:
        head_str = f" 龙{s['head_num']}" if s["head_num"] > 0 else ""
        print(f"  {s['secu_name']}({s['secu_code']})  {s['change']}  {s['tbm']}{head_str}")