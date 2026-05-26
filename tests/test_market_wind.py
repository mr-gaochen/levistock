from levistock.market.market_wind_cls import market_wind_cls, market_wind_stocks_cls, market_mainline_cls

# 今日风口板块
wind = market_wind_cls()
print(f"风口板块: {len(wind)} 个")
for item in wind[:3]:
    print(f"  {item['plate_name']}: {item['catalyst'][:30]}...")

# 风口龙头股
if wind:
    stocks = market_wind_stocks_cls(wind[0]["plate_code"])
    print(f"\n{wind[0]['plate_name']} 龙头股: {len(stocks)} 条")
    print(stocks[0] if stocks else "无数据")

# 主线机会
mainline = market_mainline_cls()
print(f"\n主线数据: {mainline}")