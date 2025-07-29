# ETF智能投資顧問 - 源代碼版

## 快速啟動

### 後端
```bash
cd etf-backend
pip install -r requirements.txt
cd src
python main.py
```
後端運行在: http://localhost:5001

### 前端
```bash
cd etf-frontend
npm install
npm run dev
```
前端運行在: http://localhost:5173

## 主要修復
- ✅ 真實技術指標替代模擬數據
- ✅ 清理ETF清單 (107檔有效ETF)
- ✅ 調整評分標準確保實用建議
- ✅ 修復前端依賴衝突
- ✅ 性能優化

## 核心文件
- `etf-backend/src/main.py` - 主程式
- `etf-backend/src/data_fetcher_optimized.py` - 數據獲取
- `etf-backend/src/investment_engine_optimized.py` - 投資引擎
- `etf-backend/src/technical_indicators.py` - 技術指標
- `etf-frontend/src/App.jsx` - 前端主應用

