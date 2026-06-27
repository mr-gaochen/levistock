from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import market, sector, stock, news, utils

app = FastAPI(
    title="Levistock API",
    description="A股市场数据 REST API — 数据源：东方财富 / 财联社 / 同花顺 / 开盘红 / i问财",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router, prefix="/api/market", tags=["大盘"])
app.include_router(sector.router, prefix="/api/sector", tags=["板块"])
app.include_router(stock.router,  prefix="/api/stock",  tags=["股票"])
app.include_router(news.router,   prefix="/api/news",   tags=["资讯"])
app.include_router(utils.router,  prefix="/api/utils",  tags=["工具"])


@app.get("/", tags=["根"])
def root():
    return {"message": "Levistock API 运行中", "docs": "/docs", "redoc": "/redoc"}
