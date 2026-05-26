from levistock.stock.stock_em import stock_zh_spot_em

# 默认过滤ST
data = stock_zh_spot_em()
print(f"过滤后股票数: {len(data)}")

# 不过滤
data_all = stock_zh_spot_em(filter_st=False)
print(f"全量股票数: {len(data_all)}")