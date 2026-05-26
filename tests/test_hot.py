from levistock.stock.stock_hot_ths import stock_hot_rank_ths

data = stock_hot_rank_ths()
print(f"人气股数量: {len(data)}")
for item in data[:5]:
    print(f"{item['rank']}. {item['name']}({item['code']}) 现价:{item['price']} 涨跌幅:{item['change_pct']}%")