"""
PostgreSQL 存储工具

用法:
    from levistock.utils.db import save_stocks_spot

    data = stocks_all_em()
    save_stocks_spot(data, dsn="postgresql://user:password@localhost:5432/dbname")
"""

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
