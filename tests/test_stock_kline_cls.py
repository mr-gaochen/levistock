from levistock.stock.stock_kline_cls import stock_timeline_cls, stock_kline_cls

# 测试分时
timeline = stock_timeline_cls("002664")
print(f"分时数据: {len(timeline)} 条")
# print(f"第一条: {timeline[0]}")

# 测试日K
kline = stock_kline_cls("002664")
print(f"\n日K数据: {len(kline)} 条")
print(f"第一条: {kline[0]}")

# 测试周K
kline_w = stock_kline_cls("002664", kline_type="weekly")
print(f"\n周K数据: {len(kline_w)} 条")

# 测试错误类型
try:
    stock_kline_cls("002664", kline_type="xxx")
except ValueError as e:
    print(f"\n错误类型: {e}")