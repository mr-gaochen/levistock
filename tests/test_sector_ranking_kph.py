"""
测试: 开盘红板块排行模块
"""

from levistock.sector.sector_ranking_kph import (
    sector_ranking_kph,
    SECTOR_SELECTED,
    SECTOR_INDUSTRY,
    SECTOR_REGION,
)

DATE_TODAY   = "2026-05-14"
DATE_HISTORY = "2026-05-13"


def test_sector_ranking_selected():
    data = sector_ranking_kph(date=DATE_TODAY, zs_type=SECTOR_SELECTED)
    print(f"\n=== 精选板块 今天 ({len(data)}个) ===")
    for p in data[:5]:
        print(f"{p['plate_id']} {p['plate_name']} 涨跌幅:{p['change_pct']}%")


def test_sector_ranking_industry():
    data = sector_ranking_kph(date=DATE_TODAY, zs_type=SECTOR_INDUSTRY)
    print(f"\n=== 行业排行 今天 ({len(data)}个) ===")
    for p in data[:5]:
        print(f"{p['plate_id']} {p['plate_name']} 涨跌幅:{p['change_pct']}%")


def test_sector_ranking_region():
    data = sector_ranking_kph(date=DATE_TODAY, zs_type=SECTOR_REGION)
    print(f"\n=== 地区排行 今天 ({len(data)}个) ===")
    for p in data[:5]:
        print(f"{p['plate_id']} {p['plate_name']} 涨跌幅:{p['change_pct']}%")


def test_sector_ranking_history():
    data = sector_ranking_kph(date=DATE_HISTORY, zs_type=SECTOR_SELECTED, fetch_all=True)
    print(f"\n=== 精选板块 历史全量 ({len(data)}个) ===")
    for p in data[:5]:
        print(f"{p['plate_id']} {p['plate_name']} 涨跌幅:{p['change_pct']}%")


if __name__ == "__main__":
    test_sector_ranking_selected()
    test_sector_ranking_industry()
    test_sector_ranking_region()
    test_sector_ranking_history()