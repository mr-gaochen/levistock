from levistock.sector.sector_cls import sector_industry_cls

data = sector_industry_cls()
print(f"共 {len(data)} 个行业板块")
print(f"涨幅最大: {data[0]['secu_name']} {data[0]['change']*100:.2f}%")
print(f"第一条: {data[0]}")

# 按主力净流入排序
sorted_data = sorted(data, key=lambda x: x["main_fund_diff"], reverse=True)
print(f"\n主力流入最多: {sorted_data[0]['secu_name']}")