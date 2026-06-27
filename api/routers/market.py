from typing import Optional

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


@router.get("/index", summary="主要指数行情（东方财富）")
def get_market_index():
    try:
        return lk.market_index_em()
    except Exception as e:
        raise _err(e)


@router.get("/index/all", summary="全部指数行情（东方财富）")
def get_market_index_all():
    try:
        return lk.market_index_all_em()
    except Exception as e:
        raise _err(e)


@router.get("/emotion", summary="市场情绪数据（财联社）")
def get_market_emotion():
    try:
        return lk.market_emotion_cls()
    except Exception as e:
        raise _err(e)


@router.get("/emotion/kph", summary="市场情绪数据（开盘红）")
def get_market_emotion_kph(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
):
    try:
        return lk.market_emotion_kph(date=date)
    except Exception as e:
        raise _err(e)


@router.get("/wind", summary="今日风口板块（财联社）")
def get_market_wind():
    try:
        return lk.market_wind_cls()
    except Exception as e:
        raise _err(e)


@router.get("/wind/stocks", summary="风口板块龙头股（财联社）")
def get_market_wind_stocks(
    plate_code: str = Query(..., description="板块代码，如 cls80198，可由 /api/market/wind 获取"),
):
    try:
        return lk.market_wind_stocks_cls(plate_code)
    except Exception as e:
        raise _err(e)


@router.get("/mainline", summary="今日主线机会（财联社）")
def get_market_mainline():
    try:
        return lk.market_mainline_cls()
    except Exception as e:
        raise _err(e)
