from levistock.stock.stock_strategy_wencai import stock_strategy_wencai

data = stock_strategy_wencai(query="连板3板以上")
print(f"表头: {data['title']}")
print(f"结果数量: {len(data['result'])}")