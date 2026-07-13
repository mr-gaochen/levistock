"""
PostgreSQL 存储工具

用法:
    from levistock.utils.db import save_stocks_spot, save_sector_industry

    data = stocks_all_em()
    save_stocks_spot(data, dsn="postgresql://user:password@localhost:5432/dbname")

    sector = sector_industry_cls()
    save_sector_industry(sector, dsn="postgresql://user:password@localhost:5432/dbname")
"""

import datetime

import psycopg2
import psycopg2.extras

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS t_stock_spot (
    stock_code      VARCHAR(10)     NOT NULL,
    stock_name      VARCHAR(50),
    price           NUMERIC(12, 4),
    change_pct      NUMERIC(8, 4),
    change_amt      NUMERIC(12, 4),
    volume          BIGINT,
    amount          NUMERIC(20, 4),
    amplitude       NUMERIC(8, 4),
    turnover_rate   NUMERIC(8, 4),
    pe_ttm          NUMERIC(12, 4),
    volume_ratio    NUMERIC(8, 4),
    high            NUMERIC(12, 4),
    low             NUMERIC(12, 4),
    open            NUMERIC(12, 4),
    pre_close       NUMERIC(12, 4),
    total_market    BIGINT,
    circ_market     BIGINT,
    pb              NUMERIC(12, 4),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (stock_code)
);
COMMENT ON TABLE  t_stock_spot                    IS 'A股实时行情快照';
COMMENT ON COLUMN t_stock_spot.stock_code         IS '股票代码';
COMMENT ON COLUMN t_stock_spot.stock_name         IS '股票名称';
COMMENT ON COLUMN t_stock_spot.price              IS '现价/收盘价(元)';
COMMENT ON COLUMN t_stock_spot.change_pct         IS '涨跌幅(%)';
COMMENT ON COLUMN t_stock_spot.change_amt         IS '涨跌额(元)';
COMMENT ON COLUMN t_stock_spot.volume             IS '成交量(手)';
COMMENT ON COLUMN t_stock_spot.amount             IS '成交额(元)';
COMMENT ON COLUMN t_stock_spot.amplitude          IS '振幅(%)';
COMMENT ON COLUMN t_stock_spot.turnover_rate      IS '换手率(%)';
COMMENT ON COLUMN t_stock_spot.pe_ttm             IS '市盈率TTM';
COMMENT ON COLUMN t_stock_spot.volume_ratio       IS '量比';
COMMENT ON COLUMN t_stock_spot.high               IS '最高价(元)';
COMMENT ON COLUMN t_stock_spot.low                IS '最低价(元)';
COMMENT ON COLUMN t_stock_spot.open               IS '开盘价(元)';
COMMENT ON COLUMN t_stock_spot.pre_close          IS '昨收价(元)';
COMMENT ON COLUMN t_stock_spot.total_market       IS '总市值(元)';
COMMENT ON COLUMN t_stock_spot.circ_market        IS '流通市值(元)';
COMMENT ON COLUMN t_stock_spot.pb                 IS '市净率PB';
COMMENT ON COLUMN t_stock_spot.updated_at         IS '最后更新时间';
"""

_UPSERT_SQL = """
INSERT INTO t_stock_spot (
    stock_code, stock_name, price, change_pct, change_amt,
    volume, amount, amplitude, turnover_rate, pe_ttm,
    volume_ratio, high, low, open, pre_close,
    total_market, circ_market, pb, updated_at
) VALUES (
    %(stock_code)s, %(stock_name)s, %(price)s, %(change_pct)s, %(change_amt)s,
    %(volume)s, %(amount)s, %(amplitude)s, %(turnover_rate)s, %(pe_ttm)s,
    %(volume_ratio)s, %(high)s, %(low)s, %(open)s, %(pre_close)s,
    %(total_market)s, %(circ_market)s, %(pb)s, NOW()
)
ON CONFLICT (stock_code) DO UPDATE SET
    stock_name    = EXCLUDED.stock_name,
    price         = EXCLUDED.price,
    change_pct    = EXCLUDED.change_pct,
    change_amt    = EXCLUDED.change_amt,
    volume        = EXCLUDED.volume,
    amount        = EXCLUDED.amount,
    amplitude     = EXCLUDED.amplitude,
    turnover_rate = EXCLUDED.turnover_rate,
    pe_ttm        = EXCLUDED.pe_ttm,
    volume_ratio  = EXCLUDED.volume_ratio,
    high          = EXCLUDED.high,
    low           = EXCLUDED.low,
    open          = EXCLUDED.open,
    pre_close     = EXCLUDED.pre_close,
    total_market  = EXCLUDED.total_market,
    circ_market   = EXCLUDED.circ_market,
    pb            = EXCLUDED.pb,
    updated_at    = NOW();
"""


_NUMERIC_FIELDS = {
    "price", "change_pct", "change_amt", "volume", "amount",
    "amplitude", "turnover_rate", "pe_ttm", "volume_ratio",
    "high", "low", "open", "pre_close", "total_market", "circ_market", "pb",
}


def _clean(row: dict) -> dict:
    """将数值字段中的 '-' / 非数字值替换为 None，避免退市股票写库报错。"""
    out = dict(row)
    for field in _NUMERIC_FIELDS:
        val = out.get(field)
        if not isinstance(val, (int, float)):
            out[field] = None
    return out


def save_stocks_spot(data: list[dict], dsn: str, batch_size: int = 500) -> int:
    """
    将 stocks_all_em / stocks_em 返回的行情列表批量写入 t_stock_spot 表。

    Args:
        data:       行情字典列表
        dsn:        PostgreSQL 连接串，如 "postgresql://user:pass@host:5432/db"
        batch_size: 每批写入的记录数，默认 500

    Returns:
        实际写入（UPSERT）的记录数
    """
    if not data:
        return 0

    cleaned = [_clean(row) for row in data]

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_TABLE_SQL)

        total = 0
        for i in range(0, len(cleaned), batch_size):
            batch = cleaned[i: i + batch_size]
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, _UPSERT_SQL, batch, page_size=batch_size)
            conn.commit()
            total += len(batch)

    return total


# ── 行业板块（财联社） ────────────────────────────────────────────────────────────

_CREATE_SECTOR_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS t_sector_daily_with_leading (
    id                      SERIAL PRIMARY KEY,
    data_date               DATE            NOT NULL,
    secu_code               VARCHAR(20)     NOT NULL,
    secu_name               VARCHAR(50)     NOT NULL,
    change                  DECIMAL(10,4)   NOT NULL,
    main_fund_diff          BIGINT          NOT NULL,
    limit_up                INT             NOT NULL,
    limit_down              INT             NOT NULL,
    limit_up_num            INT             NOT NULL,
    limit_down_num          INT             NOT NULL,
    trade_status            VARCHAR(10)     NOT NULL,
    first_stock_code        VARCHAR(20)     NOT NULL,
    first_stock_name        VARCHAR(50)     NOT NULL,
    first_stock_last_px     DECIMAL(10,2)   NOT NULL,
    first_stock_change      DECIMAL(10,4)   NOT NULL,
    first_stock_tr          DECIMAL(10,4)   NOT NULL,
    first_stock_trade_status VARCHAR(10)    NOT NULL,
    created_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_sector_date UNIQUE (secu_code, data_date)
);
"""

_UPSERT_SECTOR_SQL = """
INSERT INTO t_sector_daily_with_leading (
    data_date, secu_code, secu_name, change, main_fund_diff,
    limit_up, limit_down, limit_up_num, limit_down_num, trade_status,
    first_stock_code, first_stock_name, first_stock_last_px,
    first_stock_change, first_stock_tr, first_stock_trade_status
) VALUES (
    %(data_date)s, %(secu_code)s, %(secu_name)s, %(change)s, %(main_fund_diff)s,
    %(limit_up)s, %(limit_down)s, %(limit_up_num)s, %(limit_down_num)s, %(trade_status)s,
    %(first_stock_code)s, %(first_stock_name)s, %(first_stock_last_px)s,
    %(first_stock_change)s, %(first_stock_tr)s, %(first_stock_trade_status)s
)
ON CONFLICT (secu_code, data_date) DO UPDATE SET
    secu_name                = EXCLUDED.secu_name,
    change                   = EXCLUDED.change,
    main_fund_diff           = EXCLUDED.main_fund_diff,
    limit_up                 = EXCLUDED.limit_up,
    limit_down               = EXCLUDED.limit_down,
    limit_up_num             = EXCLUDED.limit_up_num,
    limit_down_num           = EXCLUDED.limit_down_num,
    trade_status             = EXCLUDED.trade_status,
    first_stock_code         = EXCLUDED.first_stock_code,
    first_stock_name         = EXCLUDED.first_stock_name,
    first_stock_last_px      = EXCLUDED.first_stock_last_px,
    first_stock_change       = EXCLUDED.first_stock_change,
    first_stock_tr           = EXCLUDED.first_stock_tr,
    first_stock_trade_status = EXCLUDED.first_stock_trade_status;
"""


def _flatten_sector(row: dict, data_date: datetime.date) -> dict:
    fs = row.get("first_stock") or {}
    return {
        "data_date":               data_date,
        "secu_code":               row.get("secu_code", ""),
        "secu_name":               row.get("secu_name", ""),
        "change":                  row.get("change", 0),
        "main_fund_diff":          row.get("main_fund_diff", 0),
        "limit_up":                row.get("limit_up", 0),
        "limit_down":              row.get("limit_down", 0),
        "limit_up_num":            row.get("limit_up_num", 0),
        "limit_down_num":          row.get("limit_down_num", 0),
        "trade_status":            row.get("trade_status", ""),
        "first_stock_code":        fs.get("secu_code", ""),
        "first_stock_name":        fs.get("secu_name", ""),
        "first_stock_last_px":     fs.get("last_px", 0),
        "first_stock_change":      fs.get("change", 0),
        "first_stock_tr":          fs.get("tr", 0),
        "first_stock_trade_status": fs.get("trade_status", ""),
    }


def save_sector_industry(data: list[dict], dsn: str, batch_size: int = 500) -> int:
    """
    将 sector_industry_cls() 返回的行业板块列表写入 t_sector_daily_with_leading 表。
    同一板块同一交易日重复调用时执行 UPSERT（更新最新行情）。
    """
    if not data:
        return 0

    today = datetime.date.today()
    rows = [_flatten_sector(r, today) for r in data]

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_SECTOR_TABLE_SQL)

        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i: i + batch_size]
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, _UPSERT_SECTOR_SQL, batch, page_size=batch_size)
            conn.commit()
            total += len(batch)

    return total


# ── 行业板块 5 分钟轨迹表 ──────────────────────────────────────────────────────

_CREATE_SECTOR_INTRADAY_SQL = """
CREATE TABLE IF NOT EXISTS t_sector_intraday_5min (
    id                      BIGSERIAL PRIMARY KEY,
    snapshot_time           TIMESTAMPTZ     NOT NULL,
    secu_code               VARCHAR(20)     NOT NULL,
    secu_name               VARCHAR(50)     NOT NULL,
    change                  DECIMAL(10,4)   NOT NULL,
    main_fund_diff          BIGINT          NOT NULL,
    limit_up                INT             NOT NULL,
    limit_down              INT             NOT NULL,
    limit_up_num            INT             NOT NULL,
    limit_down_num          INT             NOT NULL,
    trade_status            VARCHAR(10)     NOT NULL,
    first_stock_code        VARCHAR(20)     NOT NULL,
    first_stock_name        VARCHAR(50)     NOT NULL,
    first_stock_last_px     DECIMAL(10,2)   NOT NULL,
    first_stock_change      DECIMAL(10,4)   NOT NULL,
    first_stock_tr          DECIMAL(10,4)   NOT NULL,
    first_stock_trade_status VARCHAR(10)    NOT NULL,
    CONSTRAINT uk_sector_snapshot UNIQUE (secu_code, snapshot_time)
);
"""

_INSERT_SECTOR_INTRADAY_SQL = """
INSERT INTO t_sector_intraday_5min (
    snapshot_time, secu_code, secu_name, change, main_fund_diff,
    limit_up, limit_down, limit_up_num, limit_down_num, trade_status,
    first_stock_code, first_stock_name, first_stock_last_px,
    first_stock_change, first_stock_tr, first_stock_trade_status
) VALUES (
    %(snapshot_time)s, %(secu_code)s, %(secu_name)s, %(change)s, %(main_fund_diff)s,
    %(limit_up)s, %(limit_down)s, %(limit_up_num)s, %(limit_down_num)s, %(trade_status)s,
    %(first_stock_code)s, %(first_stock_name)s, %(first_stock_last_px)s,
    %(first_stock_change)s, %(first_stock_tr)s, %(first_stock_trade_status)s
)
ON CONFLICT (secu_code, snapshot_time) DO NOTHING;
"""


def _flatten_sector_intraday(row: dict, snapshot_time: datetime.datetime) -> dict:
    fs = row.get("first_stock") or {}
    return {
        "snapshot_time":           snapshot_time,
        "secu_code":               row.get("secu_code", ""),
        "secu_name":               row.get("secu_name", ""),
        "change":                  row.get("change", 0),
        "main_fund_diff":          row.get("main_fund_diff", 0),
        "limit_up":                row.get("limit_up", 0),
        "limit_down":              row.get("limit_down", 0),
        "limit_up_num":            row.get("limit_up_num", 0),
        "limit_down_num":          row.get("limit_down_num", 0),
        "trade_status":            row.get("trade_status", ""),
        "first_stock_code":        fs.get("secu_code", ""),
        "first_stock_name":        fs.get("secu_name", ""),
        "first_stock_last_px":     fs.get("last_px", 0),
        "first_stock_change":      fs.get("change", 0),
        "first_stock_tr":          fs.get("tr", 0),
        "first_stock_trade_status": fs.get("trade_status", ""),
    }


def save_sector_intraday(data: list[dict], dsn: str, batch_size: int = 500) -> int:
    """
    将 sector_industry_cls() 返回的板块数据以 5 分钟快照形式追加到
    t_sector_intraday_5min 表，用于查询全天资金流向轨迹。

    snapshot_time 截断到分钟，重复写入同一时间点时静默忽略（DO NOTHING）。
    """
    if not data:
        return 0

    now = datetime.datetime.now().astimezone().replace(second=0, microsecond=0)
    rows = [_flatten_sector_intraday(r, now) for r in data]

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_SECTOR_INTRADAY_SQL)

        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i: i + batch_size]
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, _INSERT_SECTOR_INTRADAY_SQL, batch, page_size=batch_size)
            conn.commit()
            total += len(batch)

    return total


# ── 涨停板股票池（东方财富） ───────────────────────────────────────────────────────

_CREATE_ZT_POOL_SQL = """
CREATE TABLE IF NOT EXISTS t_stock_zt_pool (
    id              BIGSERIAL PRIMARY KEY,
    date            DATE            NOT NULL,
    stock_code      VARCHAR(10)     NOT NULL,
    stock_name      VARCHAR(50),
    market          VARCHAR(2),
    price           DECIMAL(12,2),
    change_pct      DECIMAL(8,4),
    amount          BIGINT,
    circ_market     DECIMAL(20,2),
    circ_share      DECIMAL(20,2),
    turnover_rate   DECIMAL(8,4),
    continuous      INT,
    first_zt_time   VARCHAR(10),
    last_zt_time    VARCHAR(10),
    main_inflow     BIGINT,
    open_times      INT,
    sector          VARCHAR(50),
    zt_days         INT,
    zt_count        INT,
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_zt_pool_code_date UNIQUE (stock_code, date)
);
"""

_UPSERT_ZT_POOL_SQL = """
INSERT INTO t_stock_zt_pool (
    date, stock_code, stock_name, market, price, change_pct,
    amount, circ_market, circ_share, turnover_rate,
    continuous, first_zt_time, last_zt_time, main_inflow, open_times,
    sector, zt_days, zt_count, updated_at
) VALUES (
    %(date)s, %(stock_code)s, %(stock_name)s, %(market)s, %(price)s, %(change_pct)s,
    %(amount)s, %(circ_market)s, %(circ_share)s, %(turnover_rate)s,
    %(continuous)s, %(first_zt_time)s, %(last_zt_time)s, %(main_inflow)s, %(open_times)s,
    %(sector)s, %(zt_days)s, %(zt_count)s, NOW()
)
ON CONFLICT (stock_code, date) DO UPDATE SET
    stock_name    = EXCLUDED.stock_name,
    price         = EXCLUDED.price,
    change_pct    = EXCLUDED.change_pct,
    amount        = EXCLUDED.amount,
    circ_market   = EXCLUDED.circ_market,
    circ_share    = EXCLUDED.circ_share,
    turnover_rate = EXCLUDED.turnover_rate,
    continuous    = EXCLUDED.continuous,
    first_zt_time = EXCLUDED.first_zt_time,
    last_zt_time  = EXCLUDED.last_zt_time,
    main_inflow   = EXCLUDED.main_inflow,
    open_times    = EXCLUDED.open_times,
    sector        = EXCLUDED.sector,
    zt_days       = EXCLUDED.zt_days,
    zt_count      = EXCLUDED.zt_count,
    updated_at    = NOW();
"""

_ZT_NUMERIC_FIELDS = {
    "price", "change_pct", "amount", "circ_market", "circ_share",
    "turnover_rate", "continuous", "main_inflow", "open_times", "zt_days", "zt_count",
}


def _clean_zt_row(row: dict) -> dict:
    out = dict(row)
    raw_date = out.pop("date", None)
    try:
        out["date"] = datetime.datetime.strptime(str(raw_date), "%Y%m%d").date()
    except (ValueError, TypeError):
        out["date"] = datetime.date.today()
    for field in _ZT_NUMERIC_FIELDS:
        val = out.get(field)
        if not isinstance(val, (int, float)):
            out[field] = None
    return out


def save_stock_zt_pool(data: list[dict], dsn: str, batch_size: int = 500) -> int:
    """
    将 stock_zt_pool_em() 返回的涨停板股票池写入 t_stock_zt_pool 表。
    同一股票同一交易日重复调用时 UPSERT 更新最新数据。
    """
    if not data:
        return 0

    rows = [_clean_zt_row(r) for r in data]

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_ZT_POOL_SQL)

        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i: i + batch_size]
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, _UPSERT_ZT_POOL_SQL, batch, page_size=batch_size)
            conn.commit()
            total += len(batch)

    return total


# ── 财联社电报资讯 ─────────────────────────────────────────────────────────────

_CREATE_NEWS_TELEGRAPH_SQL = """
CREATE TABLE IF NOT EXISTS t_news_telegraph (
    id              BIGINT          NOT NULL,
    title           TEXT            NOT NULL,
    content         TEXT            NOT NULL DEFAULT '',
    post_time       TIMESTAMP       NOT NULL,
    category        VARCHAR(20)     NOT NULL DEFAULT 'all',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
COMMENT ON TABLE  t_news_telegraph              IS '财联社电报资讯';
COMMENT ON COLUMN t_news_telegraph.id           IS '电报ID';
COMMENT ON COLUMN t_news_telegraph.title        IS '标题';
COMMENT ON COLUMN t_news_telegraph.content      IS '正文内容';
COMMENT ON COLUMN t_news_telegraph.post_time    IS '发布时间';
COMMENT ON COLUMN t_news_telegraph.category     IS '分类：all/important/company';
"""

_UPSERT_NEWS_TELEGRAPH_SQL = """
INSERT INTO t_news_telegraph (id, title, content, post_time, category)
VALUES (%(id)s, %(title)s, %(content)s, %(post_time)s, %(category)s)
ON CONFLICT (id) DO UPDATE SET
    title     = EXCLUDED.title,
    content   = EXCLUDED.content,
    post_time = EXCLUDED.post_time,
    category  = EXCLUDED.category;
"""


def save_news_telegraph(data: list[dict], dsn: str,
                        category: str = "all", batch_size: int = 100) -> int:
    """
    将 news_telegraph_cls() 返回的电报列表写入 t_news_telegraph 表。

    Args:
        data:        电报字典列表
        dsn:         PostgreSQL 连接串
        category:    分类标签，默认 "all"
        batch_size:  每批写入的记录数

    Returns:
        实际写入的记录数
    """
    if not data:
        return 0

    rows = []
    for item in data:
        tid = item.get("id")
        # 跳过没有 id 的脏数据
        if tid is None:
            continue
        try:
            post_time = datetime.datetime.strptime(item.get("time", ""), "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            post_time = None
        # 跳过没有时间的脏数据（表字段 NOT NULL）
        if post_time is None:
            continue
        rows.append({
            "id":        tid,
            "title":     item.get("title", ""),
            "content":   item.get("content", ""),
            "post_time": post_time,
            "category":  category,
        })

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_NEWS_TELEGRAPH_SQL)

        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i: i + batch_size]
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, _UPSERT_NEWS_TELEGRAPH_SQL, batch, page_size=batch_size)
            conn.commit()
            total += len(batch)

    return total
