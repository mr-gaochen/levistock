from levistock.stock.stock_changes_em import stock_changes_em

# 测试火箭发射
data = stock_changes_em()
print(f"火箭发射: {len(data)} 条")

# 测试大笔买入
data2 = stock_changes_em(change_type="8193")
print(f"大笔买入: {len(data2)} 条")

# 测试错误类型
try:
    stock_changes_em(change_type="9999")
except ValueError as e:
    print(f"错误类型: {e}")