"""
测试: 开盘红市场情绪模块
"""

from levistock.market.market_emotion_kph import market_emotion_kph


def test_market_emotion_kph():
    # 不传日期，查今天
    data = market_emotion_kph()
    print("=== 今天 ===")
    print(f"涨停: {data['zt']}只（实际{data['sjzt']}，ST{data['stzt']}）")
    print(f"跌停: {data['dt']}只（实际{data['sjdt']}，ST{data['stdt']}）")
    print(f"平盘: {data['flat']}只")
    print(f"上涨: {data['rise_num']}只，下跌: {data['fall_num']}只")
    print(f"市场人气: {data['sign']}")
    print(f"全市成交额: {data['qscln'] / 1e8:.2f}亿")
    print(f"昨日全市成交额: {data['q_zrcs'] / 1e8:.2f}亿")
    print(f"涨幅分布: {data['rise_dist']}")
    print(f"跌幅分布: {data['fall_dist']}")

    # 传日期，查历史
    data2 = market_emotion_kph(date="2026-05-25")
    print("\n=== 2026-05-25 ===")
    print(f"涨停: {data2['zt']}只（实际{data2['sjzt']}，ST{data2['stzt']}）")
    print(f"跌停: {data2['dt']}只（实际{data2['sjdt']}，ST{data2['stdt']}）")
    print(f"平盘: {data2['flat']}只")
    print(f"上涨: {data2['rise_num']}只，下跌: {data2['fall_num']}只")
    print(f"市场人气: {data2['sign']}")
    print(f"全市成交额: {data2['qscln'] / 1e8:.2f}亿")
    print(f"昨日全市成交额: {data2['q_zrcs'] / 1e8:.2f}亿")
    print(f"涨幅分布: {data2['rise_dist']}")
    print(f"跌幅分布: {data2['fall_dist']}")


if __name__ == "__main__":
    test_market_emotion_kph()