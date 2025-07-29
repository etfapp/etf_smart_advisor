#!/bin/bash

# Render建置腳本
echo "開始建置ETF智能投資顧問後端..."

# 升級pip和基礎工具
echo "升級pip和基礎工具..."
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel

# 安裝依賴
echo "安裝Python依賴..."
pip install -r requirements.txt

echo "建置完成！"

