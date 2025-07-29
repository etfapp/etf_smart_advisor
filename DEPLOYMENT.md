# 🚀 ETF智能投資顧問 - 部署指南

## 📋 部署概述

本指南將幫助您將ETF智能投資顧問部署到Vercel (前端) 和 Render (後端)，實現完全免費的雲端部署。

## 🎯 部署架構

```
用戶 → Vercel (前端) → Render (後端) → yfinance API
```

## 📦 準備工作

### 1. 代碼準備
確保您有完整的專案代碼：
```
etf_app_upgraded/
├── frontend/     # React 前端
├── backend/      # Flask 後端
└── README.md
```

### 2. GitHub 倉庫
1. 在 GitHub 創建新倉庫
2. 上傳專案代碼
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/etf-advisor.git
git push -u origin main
```

## 🔧 Render 後端部署

### 步驟 1: 創建 Render 帳號
1. 訪問 https://render.com
2. 點擊 "Get Started for Free"
3. 使用 GitHub 帳號註冊/登入

### 步驟 2: 創建 Web Service
1. 在 Render Dashboard 點擊 "New +"
2. 選擇 "Web Service"
3. 連接您的 GitHub 帳號
4. 選擇包含專案的倉庫

### 步驟 3: 配置服務設定
```
Name: etf-advisor-backend
Environment: Python 3
Region: Oregon (US West) 或最近的區域
Branch: main
Root Directory: backend
```

### 步驟 4: 建置和啟動命令
```
Build Command: pip install -r requirements.txt
Start Command: python app.py
```

### 步驟 5: 環境變數設定
在 "Environment" 區域添加：
```
PORT = 10000
RENDER = true
```

### 步驟 6: 選擇方案
- 選擇 "Free" 方案
- 注意：免費方案有以下限制
  - 15分鐘無活動後會休眠
  - 每月750小時運行時間
  - 512MB RAM

### 步驟 7: 部署
1. 點擊 "Create Web Service"
2. 等待部署完成（通常需要5-10分鐘）
3. 部署成功後，記錄您的後端URL
   - 格式：`https://etf-advisor-backend.onrender.com`

### 步驟 8: 測試後端
```bash
curl https://your-backend-url.onrender.com/api/health
```
應該返回：
```json
{
  "service": "ETF智能投資顧問",
  "status": "healthy",
  "timestamp": "2025-07-29T..."
}
```

## 🌐 Vercel 前端部署

### 步驟 1: 創建 Vercel 帳號
1. 訪問 https://vercel.com
2. 點擊 "Start Deploying"
3. 使用 GitHub 帳號註冊/登入

### 步驟 2: 導入專案
1. 在 Vercel Dashboard 點擊 "New Project"
2. 從 GitHub 選擇您的倉庫
3. 點擊 "Import"

### 步驟 3: 配置專案設定
```
Project Name: etf-advisor
Framework Preset: Vite
Root Directory: frontend
```

### 步驟 4: 建置設定
Vercel 會自動檢測 Vite 專案，但您可以確認：
```
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 步驟 5: 環境變數設定
在 "Environment Variables" 區域添加：
```
Name: VITE_API_BASE
Value: https://your-backend-url.onrender.com
Environment: Production
```

### 步驟 6: 部署
1. 點擊 "Deploy"
2. 等待部署完成（通常需要2-5分鐘）
3. 部署成功後，獲得您的前端URL
   - 格式：`https://etf-advisor.vercel.app`

### 步驟 7: 測試前端
1. 訪問您的前端URL
2. 檢查是否能正常載入
3. 測試市場數據和投資建議功能

## 🔄 自動部署設定

### GitHub Actions (可選)
創建 `.github/workflows/deploy.yml`：
```yaml
name: Deploy to Vercel and Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        working-directory: ./frontend
```

## 📊 監控和維護

### Render 監控
1. 在 Render Dashboard 查看服務狀態
2. 檢查日誌：Services → Your Service → Logs
3. 監控資源使用：Services → Your Service → Metrics

### Vercel 監控
1. 在 Vercel Dashboard 查看部署狀態
2. 檢查函數日誌：Project → Functions
3. 監控性能：Project → Analytics

### 免費方案限制

#### Render 免費方案
- ✅ 750小時/月運行時間
- ✅ 512MB RAM
- ⚠️ 15分鐘無活動後休眠
- ⚠️ 冷啟動時間較長

#### Vercel 免費方案
- ✅ 100GB 頻寬/月
- ✅ 無限靜態部署
- ✅ 自動 HTTPS
- ⚠️ 函數執行時間限制

## 🛠️ 故障排除

### 常見問題

#### 1. 後端部署失敗
**問題**: Build 失敗
**解決方案**:
```bash
# 檢查 requirements.txt
pip freeze > requirements.txt

# 確認 Python 版本
echo "python-3.11.0" > runtime.txt
```

#### 2. 前端無法連接後端
**問題**: CORS 錯誤或連接失敗
**解決方案**:
1. 確認環境變數 `VITE_API_BASE` 設定正確
2. 檢查後端 CORS 設定
3. 確認後端服務正在運行

#### 3. Render 服務休眠
**問題**: 15分鐘後服務休眠
**解決方案**:
1. 使用 keep-alive 機制（已內建）
2. 考慮升級到付費方案
3. 使用外部監控服務定期 ping

#### 4. 環境變數未生效
**問題**: 配置未正確載入
**解決方案**:
1. 重新部署服務
2. 檢查變數名稱拼寫
3. 確認變數值格式正確

### 調試技巧

#### 後端調試
```bash
# 檢查日誌
curl https://your-backend.onrender.com/api/health

# 測試特定 API
curl "https://your-backend.onrender.com/api/investment-advice?funds=100000"
```

#### 前端調試
1. 打開瀏覽器開發者工具
2. 檢查 Console 錯誤
3. 查看 Network 標籤的 API 請求
4. 確認環境變數載入

## 🔄 更新部署

### 自動更新
推送到 main 分支會自動觸發重新部署：
```bash
git add .
git commit -m "Update features"
git push origin main
```

### 手動更新
#### Render
1. 在 Dashboard 點擊 "Manual Deploy"
2. 選擇 "Deploy latest commit"

#### Vercel
1. 在 Dashboard 點擊 "Redeploy"
2. 選擇最新的 commit

## 📈 性能優化

### 後端優化
1. **緩存策略**: 已實現市場數據緩存
2. **連接池**: 優化數據庫連接
3. **異步處理**: 使用 async/await

### 前端優化
1. **代碼分割**: 路由級別懶加載
2. **圖片優化**: 使用 WebP 格式
3. **緩存策略**: 設定適當的 Cache-Control

## 🔒 安全設定

### 環境變數安全
- 永遠不要在代碼中硬編碼敏感信息
- 使用平台提供的環境變數功能
- 定期輪換 API 密鑰

### HTTPS 強制
- Vercel 自動提供 HTTPS
- Render 免費方案包含 SSL 證書
- 確保所有 API 調用使用 HTTPS

## 📞 支援資源

### 官方文檔
- [Render 文檔](https://render.com/docs)
- [Vercel 文檔](https://vercel.com/docs)
- [Flask 部署指南](https://flask.palletsprojects.com/en/2.3.x/deploying/)

### 社群支援
- [Render 社群](https://community.render.com/)
- [Vercel Discord](https://vercel.com/discord)
- [Stack Overflow](https://stackoverflow.com/)

## ✅ 部署檢查清單

### 部署前
- [ ] 代碼已推送到 GitHub
- [ ] requirements.txt 包含所有依賴
- [ ] 環境變數已準備
- [ ] 本地測試通過

### 後端部署
- [ ] Render 服務創建成功
- [ ] 環境變數設定完成
- [ ] 健康檢查 API 正常
- [ ] 所有 API 端點測試通過

### 前端部署
- [ ] Vercel 專案創建成功
- [ ] 環境變數設定完成
- [ ] 前端頁面正常載入
- [ ] API 連接正常

### 部署後
- [ ] 完整功能測試
- [ ] 性能監控設定
- [ ] 錯誤監控設定
- [ ] 備份和恢復計劃

---

🎉 **恭喜！您的ETF智能投資顧問現在已經成功部署到雲端！**

記住：
- 定期檢查服務狀態
- 監控使用量避免超出免費額度
- 保持代碼更新和安全性
- 根據用戶反饋持續改進

