# main.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_fetcher import get_twse_etf_list, fetch_with_fallback

app = FastAPI(title="ETF Smart Advisor API")

# 允許前端跨域呼叫，FRONTEND_ORIGIN 在 Render 環境變數裡設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "https://your-frontend.vercel.app")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/etf_list")
async def etf_list():
    """
    動態回傳當天可交易的所有台股 ETF 代碼 (含 .TW 後綴)
    """
    codes = get_twse_etf_list()
    return {"etfs": codes}

@app.get("/api/history/{ticker}")
async def etf_history(ticker: str, period: str = "1mo"):
    """
    回傳指定 ETF 的歷史資料 (period 可用 "1mo","6mo","1y" 等)
    若找不到資料，回 404
    """
    df = fetch_with_fallback(ticker, period)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
    # DataFrame -> list of dict
    records = df.reset_index().to_dict(orient="records")
    return {"history": records}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
