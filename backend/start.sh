#!/bin/bash

# ETF智能投資顧問啟動腳本
echo "啟動ETF智能投資顧問後端服務..."

# 設置環境變數
export FLASK_APP=app.py
export FLASK_ENV=production

# 啟動應用
echo "使用Python直接啟動Flask應用..."
python app.py

echo "服務啟動完成！"

