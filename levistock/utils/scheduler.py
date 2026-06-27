"""
定时任务调度器

设计原则:
- 启动时检查是否为交易日，非交易日直接退出
- 每个任务仅在 A 股交易时段内执行（9:30-11:30 / 13:00-15:00）
- 任务间互不影响，单个任务报错不会中断整个调度器

用法:
    from levistock.utils.scheduler import Scheduler

    def my_job(dsn: str):
        data = stocks_all_em()
        save_stocks_spot(data, dsn=dsn)

    Scheduler(dsn=DSN) \\
        .register(my_job, interval_seconds=30, name="stock_spot") \\
        .start()
"""

import logging
import datetime
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from levistock.utils.trade_day import is_trade_day

logger = logging.getLogger(__name__)

_TRADING_SESSIONS = [
    (datetime.time(9, 25), datetime.time(11, 31)),
    (datetime.time(13, 0), datetime.time(15, 1)),
]


def in_trading_hours() -> bool:
    now = datetime.datetime.now().time()
    return any(s <= now <= e for s, e in _TRADING_SESSIONS)


class Scheduler:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._aps = BlockingScheduler(timezone="Asia/Shanghai")

    def register(
        self,
        func,
        interval_seconds: int,
        name: str = None,
        trading_only: bool = True,
    ) -> "Scheduler":
        """
        注册一个定时任务。

        Args:
            func:             任务函数，签名为 func(dsn: str)
            interval_seconds: 执行间隔（秒）
            name:             任务名称，用于日志，默认取函数名
            trading_only:     True 表示只在交易时段内执行
        """
        job_name = name or func.__name__
        dsn = self._dsn

        def _wrapper():
            if trading_only and not in_trading_hours():
                return
            try:
                func(dsn)
            except Exception as exc:
                logger.error("[%s] 执行失败: %s", job_name, exc, exc_info=True)

        self._aps.add_job(
            _wrapper,
            trigger="interval",
            seconds=interval_seconds,
            id=job_name,
            next_run_time=datetime.datetime.now(),  # 启动后立即执行一次
        )
        logger.info("已注册任务 [%s]，间隔 %d 秒", job_name, interval_seconds)
        return self

    def start(self, check_trade_day: bool = True) -> None:
        """
        启动调度器（阻塞当前线程）。

        Args:
            check_trade_day: True 时在非交易日等待，直到下一个交易日开盘前再启动
        """
        if check_trade_day:
            while not is_trade_day():
                now = datetime.datetime.now()
                next_check = (now + datetime.timedelta(days=1)).replace(
                    hour=9, minute=0, second=0, microsecond=0
                )
                wait = (next_check - now).total_seconds()
                logger.info("今日非交易日，等待 %.0f 秒至明日 09:00 重新检查", wait)
                time.sleep(wait)

        logger.info("调度器启动")
        try:
            self._aps.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("调度器已停止")
