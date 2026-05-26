"""
levistock - A股市场数据 SDK

数据源：东方财富 / 财联社 / 同花顺 / 开盘红 / i问财
作者：levizhang
"""

# ── 大盘 market ──────────────────────────────────────────
from levistock.market.market_index_em import (
    market_index_em,
    market_index_all_em,
)
from levistock.market.market_emotion_cls import (
    market_emotion_cls,
)
from levistock.market.market_wind_cls import (
    market_wind_cls,
    market_wind_stocks_cls,
    market_mainline_cls,
)
from levistock.market.market_emotion_kph import (
    market_emotion_kph,
)

# ── 板块 sector ──────────────────────────────────────────
from levistock.sector.sector_em import (
    sector_em,
    sector_stocks_em,
    sector_stock_belong_em,
)
from levistock.sector.sector_cls import (
    sector_industry_cls,
)
from levistock.sector.sector_heat_cls import (
    get_sector_heat,
    get_sector_popular_stocks,
)
from levistock.sector.sector_rotation_cls import (
    get_sector_rotation,
)
from levistock.sector.sector_ranking_kph import (
    sector_ranking_kph,
    SECTOR_SELECTED,
    SECTOR_INDUSTRY,
    SECTOR_REGION,
)
from levistock.sector.sector_stocks_his_kph import (
    sector_stocks_his_kph,
)

# ── 股票 stock ───────────────────────────────────────────
from levistock.stock.stock_em import (
    stocks_all_em,
    stocks_em,
)
from levistock.stock.stock_ztdt_em import (
    stock_zt_pool_em,
    stock_dt_pool_em,
    stock_yesterday_zt_em,
)
from levistock.stock.stock_zt_cls import (
    stock_zt_pool_cls,
)
from levistock.stock.stock_changes_em import (
    stock_changes_em,
    stock_changes_detail_em,
)
from levistock.stock.stock_hot_ths import (
    stock_hot_rank_ths,
)
from levistock.stock.stock_kline_cls import (
    stock_timeline_cls,
    stock_kline_cls,
)
from levistock.stock.stock_strategy_wencai import (
    stock_strategy_wencai,
)
from levistock.stock.stock_daban_his_kph import (
    limit_up_his_kph,
    limit_down_his_kph,
    wind_vane_his_kph,
)

# ── 复盘 fupanla ─────────────────────────────────────────
from levistock.stock.stock_fupanla_kph import (
    get_zttt,
    get_pmsl,
    get_his_limit_resumption,
)

# ── 资讯 news ────────────────────────────────────────────
from levistock.news.news_cls import (
    news_telegraph_cls,
)

# ── 工具 utils ───────────────────────────────────────────
from levistock.utils.trade_day import (
    is_trade_day,
    get_trade_days,
)

__version__ = "0.1.0"
__author__  = "levizhang"

__all__ = [
    # 大盘
    "market_index_em",
    "market_index_all_em",
    "market_emotion_cls",
    "market_wind_cls",
    "market_wind_stocks_cls",
    "market_mainline_cls",
    "market_emotion_kph",
    # 板块
    "sector_em",
    "sector_stocks_em",
    "sector_stock_belong_em",
    "sector_industry_cls",
    "get_sector_heat",
    "get_sector_popular_stocks",
    "get_sector_rotation",
    "sector_ranking_kph",
    "sector_stocks_his_kph",
    "SECTOR_SELECTED",
    "SECTOR_INDUSTRY",
    "SECTOR_REGION",
    # 股票
    "stocks_all_em",
    "stocks_em",
    "stock_zt_pool_em",
    "stock_dt_pool_em",
    "stock_yesterday_zt_em",
    "stock_zt_pool_cls",
    "stock_changes_em",
    "stock_changes_detail_em",
    "stock_hot_rank_ths",
    "stock_timeline_cls",
    "stock_kline_cls",
    "stock_strategy_wencai",
    "limit_up_his_kph",
    "limit_down_his_kph",
    "wind_vane_his_kph",
    # 复盘
    "get_zttt",
    "get_pmsl",
    "get_his_limit_resumption",
    # 资讯
    "news_telegraph_cls",
    # 工具
    "is_trade_day",
    "get_trade_days",
]