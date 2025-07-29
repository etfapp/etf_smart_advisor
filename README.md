# ETF智能投資顧問 - 升級版

## 🎯 專案概述

這是一個專為忙碌投資者設計的台股ETF智能投資App，基於Vercel + Render免費部署架構，提供「無需設定、快速上手、降低風險」的智慧化投資體驗。

### 核心功能
- 📊 **即時市場分析**: 台股加權指數監控和趨勢分析
- 🎯 **智能投資建議**: 基於多因子模型的ETF推薦
- 💰 **一鍵投資**: 簡化的投資執行流程
- 🛡️ **風險控制**: 智能分散投資和風險監控
- 📱 **響應式設計**: 支援桌面和移動設備

## 🏗️ 系統架構

```
Frontend (React + Vite)     Backend (Flask)
├── Vercel 部署            ├── Render 部署
├── Tailwind CSS           ├── yfinance 數據
├── shadcn/ui 組件         ├── 投資引擎
└── 響應式設計             └── 風險管理
```

## 📁 專案結構

```
etf_app_upgraded/
├── frontend/                 # React 前端應用
│   ├── src/
│   │   ├── App.jsx          # 主應用組件
│   │   └── components/      # UI 組件
│   ├── package.json         # 前端依賴
│   └── .env                 # 環境變數
├── backend/                 # Flask 後端服務
│   ├── app.py              # 主應用
│   ├── data_fetcher.py     # 數據獲取
│   ├── investment_engine.py # 投資引擎
│   ├── risk_manager.py     # 風險管理
│   ├── portfolio_manager.py # 投資組合管理
│   └── requirements.txt    # 後端依賴
└── README.md               # 本文件
```

## 🚀 快速開始

### 前置需求
- Node.js 18+
- Python 3.8+
- Git

### 本地開發

#### 1. 克隆專案
```bash
git clone <your-repo-url>
cd etf_app_upgraded
```

#### 2. 啟動後端服務
```bash
cd backend
pip install -r requirements.txt
python app.py
```
後端將在 http://localhost:5000 啟動

#### 3. 啟動前端服務
```bash
cd frontend
npm install
npm run dev
```
前端將在 http://localhost:5173 啟動

#### 4. 訪問應用
打開瀏覽器訪問 http://localhost:5173

## 🌐 部署指南

### Render 後端部署

1. **創建 Render 帳號**
   - 訪問 https://render.com
   - 使用 GitHub 帳號登入

2. **創建 Web Service**
   - 點擊 "New +" → "Web Service"
   - 連接您的 GitHub 倉庫
   - 選擇 `backend` 目錄

3. **配置設定**
   ```
   Name: etf-advisor-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

4. **環境變數**
   ```
   PORT=10000
   RENDER=true
   ```

5. **部署**
   - 點擊 "Create Web Service"
   - 等待部署完成
   - 記錄後端 URL (例如: https://etf-advisor-backend.onrender.com)

### Vercel 前端部署

1. **創建 Vercel 帳號**
   - 訪問 https://vercel.com
   - 使用 GitHub 帳號登入

2. **導入專案**
   - 點擊 "New Project"
   - 選擇您的 GitHub 倉庫
   - 設定 Root Directory 為 `frontend`

3. **環境變數**
   ```
   VITE_API_BASE=https://your-backend-url.onrender.com
   ```

4. **部署**
   - 點擊 "Deploy"
   - 等待部署完成
   - 獲得前端 URL (例如: https://etf-advisor.vercel.app)

## 🔧 配置說明

### 環境變數

#### 前端 (.env)
```env
VITE_API_BASE=http://localhost:5000  # 開發環境
# VITE_API_BASE=https://your-backend.onrender.com  # 生產環境
```

#### 後端 (環境變數)
```env
PORT=5000          # 本地開發
# PORT=10000       # Render 生產環境
RENDER=true        # Render 部署標識
```

### API 端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康檢查 |
| `/api/market-overview` | GET | 市場概況 |
| `/api/investment-advice` | GET | 投資建議 |
| `/api/execute-investment` | POST | 執行投資 |
| `/api/portfolio/<user_id>` | GET | 投資組合 |
| `/api/risk-assessment/<user_id>` | GET | 風險評估 |

## 📊 核心功能詳解

### 1. 市場分析引擎
- **數據來源**: yfinance API
- **更新頻率**: 實時
- **分析指標**: 
  - 台股加權指數
  - 價格變動百分比
  - 市場波動率
  - 趨勢判斷

### 2. 投資策略引擎
- **多因子模型**:
  - 基本面分析 (50%)
  - 技術面分析 (30%)
  - 市場環境 (20%)
- **評分系統**: 0-100分
- **建議等級**: 強力買入、買入、持有、賣出

### 3. 風險管理系統
- **集中度控制**: 單一持倉≤35%
- **類別分散**: 單一類別≤50%
- **波動率監控**: 投資組合波動率≤25%
- **動態調整**: 基於市場條件自動調整

### 4. 投資組合管理
- **模擬交易**: 完整的交易記錄
- **績效追蹤**: 實時損益計算
- **資產配置**: 智能分散建議
- **再平衡提醒**: 定期優化建議

## 🛠️ 開發指南

### 前端開發

#### 技術棧
- **框架**: React 19 + Vite
- **樣式**: Tailwind CSS
- **組件**: shadcn/ui
- **圖標**: Lucide React
- **圖表**: Recharts

#### 主要組件
```jsx
// 主應用
App.jsx

// 核心組件
MarketOverview.jsx      // 市場概況
InvestmentRecommendations.jsx  // 投資建議
QuickStats.jsx          // 快速統計
RecommendationCard.jsx  // 建議卡片
```

#### 開發命令
```bash
npm run dev     # 開發服務器
npm run build   # 生產建置
npm run preview # 預覽建置
```

### 後端開發

#### 技術棧
- **框架**: Flask 2.3
- **數據**: yfinance, pandas
- **CORS**: Flask-CORS
- **部署**: Gunicorn

#### 核心模組
```python
app.py              # 主應用和API路由
data_fetcher.py     # 數據獲取和緩存
investment_engine.py # 投資策略引擎
risk_manager.py     # 風險管理
portfolio_manager.py # 投資組合管理
```

#### 開發命令
```bash
python app.py       # 啟動開發服務器
pip freeze > requirements.txt  # 更新依賴
```

## 🔍 測試指南

### API 測試
```bash
# 健康檢查
curl http://localhost:5000/api/health

# 市場概況
curl http://localhost:5000/api/market-overview

# 投資建議
curl "http://localhost:5000/api/investment-advice?funds=100000"
```

### 前端測試
1. 打開 http://localhost:5173
2. 檢查市場數據載入
3. 調整投資金額
4. 測試一鍵投資功能

## 📈 性能優化

### 前端優化
- **代碼分割**: 路由級別的懶加載
- **圖片優化**: WebP 格式和響應式圖片
- **緩存策略**: API 響應緩存
- **打包優化**: Vite 自動優化

### 後端優化
- **數據緩存**: 市場數據緩存機制
- **連接池**: 數據庫連接優化
- **異步處理**: 非阻塞數據獲取
- **錯誤處理**: 完善的異常處理

## 🔒 安全考量

### 前端安全
- **環境變數**: 敏感配置隔離
- **HTTPS**: 生產環境強制 HTTPS
- **CSP**: 內容安全策略

### 後端安全
- **CORS**: 跨域請求控制
- **輸入驗證**: 參數驗證和清理
- **錯誤處理**: 避免敏感信息洩露
- **日誌記錄**: 完整的操作日誌

## 🐛 常見問題

### Q: 前端無法連接後端？
A: 檢查 `.env` 文件中的 `VITE_API_BASE` 設定是否正確

### Q: 後端 API 返回錯誤？
A: 檢查後端日誌，確認依賴安裝完整

### Q: Render 部署失敗？
A: 確認 `requirements.txt` 包含所有依賴，檢查 Python 版本兼容性

### Q: Vercel 部署失敗？
A: 確認環境變數設定正確，檢查建置命令

## 📝 更新日誌

### v2.0.0 (2025-07-29)
- ✨ 全新的投資策略引擎
- 🛡️ 增強的風險管理系統
- 📱 優化的用戶界面
- 🚀 改進的部署流程
- 📊 真實市場數據整合

### v1.0.0 (原始版本)
- 基礎的ETF分析功能
- 簡單的投資建議
- 基本的前端界面

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

## 📞 支援

如有問題或建議，請：
1. 開啟 GitHub Issue
2. 聯繫開發團隊
3. 查看文檔和 FAQ

---

**注意**: 本系統僅供教育和研究用途，不構成投資建議。投資有風險，請謹慎決策。

