from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import akshare as ak

app = FastAPI(title="ETF Quant Market API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "ETF行情服务已启动",
        "time": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/etf/{symbol}")
def get_etf(symbol: str):
    if not symbol.isdigit() or len(symbol) != 6:
        return {
            "status": "error",
            "message": "请输入6位ETF代码，例如159513"
        }

    try:
        df = ak.fund_etf_spot_em()

        row = df[df["代码"].astype(str) == symbol]

        if row.empty:
            return {
                "status": "error",
                "message": "未查询到该ETF，请检查代码或稍后重试"
            }

        item = row.iloc[0]

        return {
            "status": "ok",
            "symbol": symbol,
            "name": str(item.get("名称", "")),
            "price": str(item.get("最新价", "")),
            "change_percent": str(item.get("涨跌幅", "")),
            "volume": str(item.get("成交量", "")),
            "amount": str(item.get("成交额", "")),
            "source": "东方财富公开行情接口",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception:
        return {
            "status": "error",
            "message": "行情源暂时不可用，请稍后重试"
        }
