from levistock.news.news_cls import news_telegraph_cls

# 今日全部
data = news_telegraph_cls()
print(f"今日全部: {len(data)} 条")
print(data)

# 今日重要消息
important = news_telegraph_cls(category="important")
print(f"\n今日重要: {len(important)} 条")
print(important)

# 今日公司公告
company = news_telegraph_cls(category="company")
print(f"\n今日公司: {len(company)} 条")

print(company)

# # 历史查询
# history = news_telegraph_cls(date="2026-05-25", category="company")
# print(f"\n历史公司公告: {len(history)} 条")