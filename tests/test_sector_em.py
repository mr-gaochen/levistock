from levistock.sector.sector_em import sector_em, sector_stocks_em, sector_stock_belong_em

# 全部行业板块
industry = sector_em()
print(f"全部行业板块: {len(industry)} 条")
print(f"第一条: {industry[0]}")

# 一级行业
l1 = sector_em(sector_type="industry_l1")
print(f"\n一级行业: {len(l1)} 条")

# 二级行业
l2 = sector_em(sector_type="industry_l2")
print(f"二级行业: {len(l2)} 条")

# 三级行业
l3 = sector_em(sector_type="industry_l3")
print(f"三级行业: {len(l3)} 条")

# 概念板块
concept = sector_em(sector_type="concept")
print(f"\n概念板块: {len(concept)} 条")
print(f"第一条: {concept[0]}")

# 板块成分股
stocks = sector_stocks_em(industry[0]["sector_code"])
print(f"\n成分股: {len(stocks)} 条")

# 股票所属板块
belong = sector_stock_belong_em(["000001", "600001", "300001"])
for item in belong:
    print(f"{item['stock_name']} → {item['sector_name']}")