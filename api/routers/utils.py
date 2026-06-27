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


@router.get("/is_trade_day", summary="判断今日是否为交易日")
def get_is_trade_day():
    try:
        return {"is_trade_day": lk.is_trade_day()}
    except Exception as e:
        raise _err(e)


@router.get("/trade_days", summary="获取最近 N 个交易日列表")
def get_trade_days(
    n: int = Query(10, description="返回交易日数量，默认 10"),
):
    try:
        return lk.get_trade_days(n=n)
    except Exception as e:
        raise _err(e)
