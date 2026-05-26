from levistock.stock.stock_zt_cls import stock_zt_pool_cls

data = stock_zt_pool_cls()
print(f"今日涨停数: {len(data)}")
for item in data[:5]:
    print(f"{item['secu_name']}: {item['up_reason']}")