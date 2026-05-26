from levistock.market.market_emotion_cls import market_emotion_cls

data = market_emotion_cls()
print(f"市场热度: {data['market_degree']}")
print(f"两市成交额: {data['shsz_balance']}")
print(f"上涨家数: {data['up_down_dis']['rise_num']}")
print(f"下跌家数: {data['up_down_dis']['fall_num']}")
print(f"涨停家数: {data['up_down_dis']['up_num']}")
print(f"封板率: {data['up_ratio']}")
print(f"连板分布: {data['limit_up_board']}")