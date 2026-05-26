"""
测试: 开盘红历史成分股模块
"""

from levistock.sector.sector_ranking_kph import sector_ranking_kph, SECTOR_SELECTED
from levistock.sector.sector_stocks_his_kph import sector_stocks_his_kph

DATE_HISTORY = "2026-05-13"


def test_sector_stocks_his_kph():
    plates = sector_ranking_kph(date=DATE_HISTORY, zs_type=SECTOR_SELECTED)
    plate_id   = plates[0]['plate_id']
    plate_name = plates[0]['plate_name']
    stocks = sector_stocks_his_kph(plate_id=plate_id, date=DATE_HISTORY)
    print(f"\n=== {plate_name}({plate_id}) 成分股 ({len(stocks)}只) ===")
    for s in stocks[:5]:
        print(f"{s['code']} {s['name']} 涨跌幅:{s['change_pct']}% "
              f"换手:{s['turnover_rate']}% 标签:{s['rank_tag']}")


if __name__ == "__main__":
    test_sector_stocks_his_kph()
