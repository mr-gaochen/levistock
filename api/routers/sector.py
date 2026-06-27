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


@router.get("", summary="板块列表（东方财富）")
def get_sector(
    sector_type: str = Query("industry", description="板块类型：industry（行业）或 concept（概念）"),
):
    try:
        return lk.sector_em(sector_type=sector_type)
    except Exception as e:
        raise _err(e)


@router.get("/stocks", summary="板块成分股（东方财富）")
def get_sector_stocks(
    sector_code: str = Query(..., description="板块代码，如 BK0477，可由 /api/sector 获取"),
):
    try:
        return lk.sector_stocks_em(sector_code)
    except Exception as e:
        raise _err(e)


@router.get("/stock/belong", summary="股票所属板块（东方财富）")
def get_sector_stock_belong(
    codes: List[str] = Query(..., description="股票代码列表，可传多个，如 ?codes=600000&codes=000001"),
):
    try:
        return lk.sector_stock_belong_em(codes)
    except Exception as e:
        raise _err(e)


@router.get("/industry", summary="行业板块实时行情（财联社）")
def get_sector_industry():
    try:
        return lk.sector_industry_cls()
    except Exception as e:
        raise _err(e)


@router.get("/heat", summary="板块热度排行（财联社）")
def get_sector_heat():
    try:
        return lk.get_sector_heat()
    except Exception as e:
        raise _err(e)


@router.get("/heat/stocks", summary="热门板块龙头股（财联社）")
def get_sector_heat_stocks(
    plate_code: str = Query(..., description="板块代码，可由 /api/sector/heat 获取"),
):
    try:
        return lk.get_sector_popular_stocks(plate_code)
    except Exception as e:
        raise _err(e)


@router.get("/rotation", summary="板块轮动数据（财联社）")
def get_sector_rotation(
    days: int = Query(4, description="查询天数，默认 4 天"),
):
    try:
        return lk.get_sector_rotation(days=days)
    except Exception as e:
        raise _err(e)


@router.get("/ranking", summary="板块涨跌榜（开盘红）")
def get_sector_ranking(
    date: str = Query(..., description="日期，格式 YYYYMMDD"),
    zs_type: str = Query(..., description=f"板块类型：{lk.SECTOR_SELECTED}（精选） / {lk.SECTOR_INDUSTRY}（行业） / {lk.SECTOR_REGION}（地区）"),
    fetch_all: bool = Query(False, description="是否获取全部（默认仅取涨跌前列）"),
):
    try:
        return lk.sector_ranking_kph(date=date, zs_type=zs_type, fetch_all=fetch_all)
    except Exception as e:
        raise _err(e)


@router.get("/stocks/history", summary="板块历史成分股行情（开盘红）")
def get_sector_stocks_history(
    plate_id: str = Query(..., description="板块 ID，可由 /api/sector/ranking 获取"),
    date: str = Query(..., description="日期，格式 YYYYMMDD"),
):
    try:
        return lk.sector_stocks_his_kph(plate_id=plate_id, date=date)
    except Exception as e:
        raise _err(e)
