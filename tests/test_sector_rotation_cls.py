"""
测试财联社板块轮动接口 sector_rotation_cls.py
"""

from levistock.sector.sector_rotation_cls import get_sector_rotation

print("=" * 50)
print("[1] 板块轮动 get_sector_rotation(days=4)")
print("=" * 50)
rotation = get_sector_rotation(days=4)
for day in rotation:
    print(f"\n  {day['trade_date']}")
    for p in day.get("plates", []):
        sign = "+" if p["change"] >= 0 else ""
        print(f"    {p['plate_name']:<12} {sign}{p['change']}%")
