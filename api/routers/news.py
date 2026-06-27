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


@router.get("/telegraph", summary="财联社电报资讯")
def get_news_telegraph(
    date: Optional[str] = Query(None, description="日期，格式 YYYYMMDD，默认今日"),
    category: str = Query("important", description="资讯分类：important（重要）/ all（全部）"),
):
    try:
        return lk.news_telegraph_cls(date=date, category=category)
    except Exception as e:
        raise _err(e)
