from typing import List, Optional

import requests
from fastapi import APIRouter, HTTPException, Query

import levistock as lk

router = APIRouter()


def _err(e: Exception) -> HTTPException:
    if isinstance(e, ValueError):
        return HTTPException(status_code=400, detail=str(e))
    if isinstance(e, requests.exceptions.RequestException):
        return HTTPException(status_code=502, detail=f"上游数据源请求失败: {e}")
    return HTTPException(status_code=500, detail=str(e))


# ── 行情快照 ──────────────────────────────────────────────────────────────────

@router.get("/all", summary="全市场A股实时行情（东方财富）")
def get_stocks_all(
    filter_st: bool = Query(True, description="是否过滤 ST 股，默认 True"),
):
    try:
        return lk.stocks_all_em(filter_st=filter_st)
    except Exception as e:
        raise _err(e)


@router.get("", summary="批量查询个股实时行情（东方财富）")
def get_stocks(
    codes: List[str] = Query(..., description="股票代码列表，支持纯代码或带前缀，如 ?codes=600000&codes=sz000001"),
):
    try:
        return lk.stocks_em(codes)
    except Exception as e:
        raise _err(e)


# ── 涨跌停 ────────────────────────────────────────────────────────────────────

@router.get("/zt_pool", summary="涨停板股票池（东方财富）")
def get_stock_zt_pool(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
):
    try:
        return lk.stock_zt_pool_em(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/dt_pool", summary="跌停板股票池（东方财富）")
def get_stock_dt_pool(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
):
    try:
        return lk.stock_dt_pool_em(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/yesterday_zt", summary="昨日涨停今日表现（东方财富）")
def get_stock_yesterday_zt(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
):
    try:
        return lk.stock_yesterday_zt_em(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/zt_pool/cls", summary="涨停板股票池（财联社）")
def get_stock_zt_pool_cls():
    try:
        return lk.stock_zt_pool_cls()
    except Exception as e:
        raise _err(e)


# ── 异动 ──────────────────────────────────────────────────────────────────────

@router.get("/changes", summary="股票异动列表（东方财富）")
def get_stock_changes(
    change_type: str = Query("8201", description="异动类型代码，默认 8201（连续涨停）"),
    filter_st: bool = Query(True, description="是否过滤 ST 股"),
):
    try:
        return lk.stock_changes_em(change_type=change_type, filter_st=filter_st)
    except Exception as e:
        raise _err(e)


@router.get("/changes/detail", summary="个股异动明细（东方财富）")
def get_stock_changes_detail(
    stock_code: str = Query(..., description="股票代码，如 600000"),
    market: str = Query(..., description="市场，sh 或 sz"),
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
):
    try:
        return lk.stock_changes_detail_em(stock_code=stock_code, market=market, date=date)
    except Exception as e:
        raise _err(e)


# ── 热度 / K线 ────────────────────────────────────────────────────────────────

@router.get("/hot_rank", summary="同花顺人气榜")
def get_stock_hot_rank(
    limit: int = Query(100, description="返回条数，默认 100"),
):
    try:
        return lk.stock_hot_rank_ths(limit=limit)
    except Exception as e:
        raise _err(e)


@router.get("/timeline", summary="个股分时数据（财联社）")
def get_stock_timeline(
    stock_code: str = Query(..., description="股票代码，如 600000 或 sh600000"),
):
    try:
        return lk.stock_timeline_cls(stock_code=stock_code)
    except Exception as e:
        raise _err(e)


@router.get("/kline", summary="个股K线数据（财联社）")
def get_stock_kline(
    stock_code: str = Query(..., description="股票代码，如 600000 或 sh600000"),
    kline_type: str = Query("daily", description="K线类型：daily / weekly / monthly / 60 / 30 / 15 / 5 / 1"),
    limit: int = Query(50, description="返回条数，默认 50"),
    offset: int = Query(0, description="偏移量，默认 0"),
):
    try:
        return lk.stock_kline_cls(stock_code=stock_code, kline_type=kline_type, limit=limit, offset=offset)
    except Exception as e:
        raise _err(e)


# ── 选股策略 ──────────────────────────────────────────────────────────────────

@router.get("/strategy", summary="问财智能选股（i问财）")
def get_stock_strategy(
    query: str = Query(..., description="自然语言选股条件，如：涨停两天以上的次新股"),
    page: int = Query(1, description="页码，默认 1"),
    limit: int = Query(50, description="每页条数，默认 50"),
):
    try:
        return lk.stock_strategy_wencai(query=query, page=page, limit=limit)
    except Exception as e:
        raise _err(e)


# ── 打板历史 / 复盘 ───────────────────────────────────────────────────────────

@router.get("/limit_up/history", summary="历史涨停板明细（开盘红）")
def get_limit_up_history(
    date: str = Query(..., description="日期，格式 YYYYMMDD"),
):
    try:
        return lk.limit_up_his_kph(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/limit_down/history", summary="历史跌停板明细（开盘红）")
def get_limit_down_history(
    date: str = Query(..., description="日期，格式 YYYYMMDD"),
):
    try:
        return lk.limit_down_his_kph(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/wind_vane/history", summary="历史风向标股票（开盘红）")
def get_wind_vane_history(
    date: str = Query(..., description="日期，格式 YYYYMMDD"),
):
    try:
        return lk.wind_vane_his_kph(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/review/zttt", summary="涨停梯队复盘（开盘红）")
def get_review_zttt(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
):
    try:
        return lk.get_zttt(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/review/pmsl", summary="票面胜率复盘（开盘红）")
def get_review_pmsl(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
    st: int = Query(30, description="每页条数，默认 30"),
    index: int = Query(0, description="分页偏移，默认 0"),
):
    try:
        return lk.get_pmsl(date=date, st=st, index=index)
    except Exception as e:
        raise _err(e)


@router.get("/review/limit_resumption", summary="历史涨停复盘（开盘红）")
def get_review_limit_resumption(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
    st: int = Query(100, description="每页条数，默认 100"),
    index: int = Query(0, description="分页偏移，默认 0"),
):
    try:
        return lk.get_his_limit_resumption(date=date, st=st, index=index)
    except Exception as e:
        raise _err(e)
