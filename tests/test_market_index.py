from levistock.market.market_index_em import market_index_em, market_index_all_em

# 常用6个
data = market_index_em()
print(f"常用指数: {len(data)} 条")
for item in data:
    print(f"  {item['name']}: {item['price']} ({item['change_pct']}%)")

# 全部
data_all = market_index_all_em()
print(f"\n全部指数: {len(data_all)} 条")