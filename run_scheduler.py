"""
定时数据采集入口

启动方式:
    python run_scheduler.py

说明:
- 非交易日自动退出
- 每个任务只在 9:30-11:30 / 13:00-15:00 期间执行
- 新增任务：仿照 job_stocks_spot 写一个 job_xxx(dsn) 函数，然后 .register(...) 即可
"""

import logging
import os

from dotenv import load_dotenv
load_dotenv()

from levistock.stock.stock_em import stocks_all_em
from levistock.utils.db import save_stocks_spot
from levistock.utils.scheduler import Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── 数据库连接串 ────────────────────────────────────────────────────────────────
DSN = os.environ["PG_DSN"]


# ── 任务定义（每个任务签名固定为 func(dsn: str)） ──────────────────────────────

def job_stocks_spot(dsn: str):
    data = stocks_all_em(filter_st=False)
    count = save_stocks_spot(data, dsn=dsn)
    logging.getLogger(__name__).info("stock_spot  UPSERT %d 条", count)


# 新增任务示例（取消注释并实现即可）:
#
# from levistock.market.market_emotion_cls import market_emotion_cls
# from levistock.utils.db import save_market_emotion   # 需自行在 db.py 中实现
#
# def job_market_emotion(dsn: str):
#     data = market_emotion_cls()
#     save_market_emotion(data, dsn=dsn)


# ── 启动调度器 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    (
        Scheduler(dsn=DSN)
        .register(job_stocks_spot, interval_seconds=20, name="stock_spot", trading_only=True)
        # .register(job_market_emotion, interval_seconds=300, name="market_emotion")
        .start()
    )
