from levistock.stock.stock_em import stocks_all_em
from levistock.utils.db import save_stocks_spot

DSN = "postgresql://user:password@localhost:5432/dbname"

# data = stocks_em(["000001", "600519", "300750"])
# print(data)
# for item in data:
#     print(f"{item['stock_name']}: {item['price']} ({item['change_pct']}%)")


data = stocks_all_em(filter_st=False)
print(data[0])
print(len(data))

count = save_stocks_spot(data, dsn=DSN)
print(f"UPSERT {count} 条记录")