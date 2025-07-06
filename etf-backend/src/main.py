# src/main.py

import os
from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from data_fetcher import get_twse_etf_list, fetch_with_fallback

app = Flask(__name__)

# 允許前端跨域呼叫
# FRONTEND_ORIGIN 需在 Render 環境變數裡設定，例如 "https://你的-frontend.vercel.app"
CORS(app, origins=[os.getenv("FRONTEND_ORIGIN", "*")])

@app.route("/api/etf_list", methods=["GET"])
def etf_list():
    """
    動態回傳當天可交易的所有台股 ETF 代碼 (含 .TW 後綴)
    """
    codes = get_twse_etf_list()
    return jsonify({"etfs": codes}), 200

@app.route("/api/history/<string:ticker>", methods=["GET"])
def etf_history(ticker):
    """
    回傳指定 ETF 的歷史資料 (period 可用 URL 參數 ?period=1mo,6mo,1y)
    若找不到資料，回 404
    """
    period = request.args.get("period", "1mo")
    df = fetch_with_fallback(ticker, period)
    if df is None or df.empty:
        abort(404, description=f"No data found for {ticker}")
    # DataFrame -> list of dict
    records = df.reset_index().to_dict(orient="records")
    return jsonify({"history": records}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
