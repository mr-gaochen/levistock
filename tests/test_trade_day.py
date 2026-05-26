from levistock.utils.trade_day import is_trade_day, get_trade_days

if is_trade_day():
    print("今天是交易日")
else:
    print("今天不是交易日")

days = get_trade_days()
print(f"近10个交易日: {days}")

days5 = get_trade_days(n=5)
print(f"近5个交易日: {days5}")

try:
    get_trade_days(n=100)
except ValueError as e:
    print(f"参数错误: {e}")