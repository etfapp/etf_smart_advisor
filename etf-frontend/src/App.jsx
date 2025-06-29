import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { TrendingUp, TrendingDown, DollarSign, Target, AlertTriangle, BarChart3, Zap, Brain, Settings, Search, Plus, X, Star } from 'lucide-react'
import './App.css'

// API 基礎 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV ? 'http://localhost:5000/api' : 'https://etf-smart-advisor.onrender.com/api');

function App() {
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userProfile, setUserProfile] = useState({
    available_cash: 100000,
    selected_etfs: [],
    num_etfs_to_invest: 0
  })
  
  // ETF 相關狀態
  const [allEtfs, setAllEtfs] = useState([])
  const [etfSearchTerm, setEtfSearchTerm] = useState('')
  const [loadingEtfs, setLoadingEtfs] = useState(false)

  // 獲取所有 ETF 清單
  const fetchAllEtfs = async () => {
    setLoadingEtfs(true)
    try {
      const response = await fetch(`${API_BASE_URL}/etf-list`)
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setAllEtfs(data.data)
        }
      }
    } catch (error) {
      console.error('獲取 ETF 清單失敗:', error)
    } finally {
      setLoadingEtfs(false)
    }
  }

  // 獲取每日投資建議
  const fetchDailyRecommendation = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/daily-recommendation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userProfile)
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('API Response:', data) // 添加調試日誌
        console.log('Positions:', data.positions) // 檢查 positions 數據
        console.log('Risk Alerts:', data.risk_alerts) // 檢查風險警示數據
        setRecommendation(data)
      } else {
        setError('API 請求失敗，請稍後再試')
      }
    } catch (error) {
      console.error('獲取投資建議失敗:', error)
      setError('無法連接到服務器，請檢查網路連接')
    } finally {
      setLoading(false)
    }
  }

  // 頁面載入時自動獲取建議和 ETF 清單
  useEffect(() => {
    fetchDailyRecommendation()
    fetchAllEtfs()
  }, [])

  // 新增 ETF 到選擇清單
  const addEtf = (etf) => {
    if (!userProfile.selected_etfs.includes(etf.symbol)) {
      setUserProfile(prev => ({
        ...prev,
        selected_etfs: [...prev.selected_etfs, etf.symbol]
      }))
    }
  }

  // 從選擇清單移除 ETF
  const removeEtf = (symbol) => {
    setUserProfile(prev => ({
      ...prev,
      selected_etfs: prev.selected_etfs.filter(s => s !== symbol)
    }))
  }

  // 過濾 ETF 清單
  const filteredEtfs = allEtfs.filter(etf => 
    etf.name.toLowerCase().includes(etfSearchTerm.toLowerCase()) ||
    etf.symbol.toLowerCase().includes(etfSearchTerm.toLowerCase())
  )

  // 獲取已選擇的 ETF 詳細資訊
  const selectedEtfDetails = allEtfs.filter(etf => 
    userProfile.selected_etfs.includes(etf.symbol)
  )

  // 格式化金額
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  // 獲取燈號顏色
  const getSignalColor = (signal) => {
    switch (signal) {
      case '綠燈': return 'bg-green-500'
      case '黃燈': return 'bg-yellow-500'
      case '紅燈': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  // 獲取推薦的ETF（評分>=60的ETF）
  const getRecommendedEtfs = () => {
    if (!recommendation?.positions) return []
    
    // 從positions中提取推薦的ETF信息
    return recommendation.positions.map(position => ({
      symbol: position.symbol,
      name: position.name,
      rating: position.rating,
      recommendation: position.recommendation,
      price: position.price,
      final_score: 75 // 預設評分，實際應從後端獲取
    }))
  }

  // 計算自訂清單的投資配置
  const calculateCustomPositions = () => {
    if (selectedEtfDetails.length === 0) return []
    
    const investmentRatio = recommendation?.strategy?.investment_ratio || 0.6
    const totalInvestment = userProfile.available_cash * investmentRatio
    const numEtfs = userProfile.num_etfs_to_invest > 0 ? 
      Math.min(userProfile.num_etfs_to_invest, selectedEtfDetails.length) : 
      selectedEtfDetails.length
    
    const selectedForInvestment = selectedEtfDetails.slice(0, numEtfs)
    const allocationPerEtf = totalInvestment / selectedForInvestment.length
    
    return selectedForInvestment.map(etf => {
      const shares = Math.floor(allocationPerEtf / (etf.current_price || 50))
      const actualAmount = shares * (etf.current_price || 50)
      
      return {
        symbol: etf.symbol,
        name: etf.name,
        shares: shares,
        price: etf.current_price || 50,
        amount: actualAmount,
        weight: (actualAmount / totalInvestment) * 100
      }
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* 標題區域 */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-800">台股 ETF 智能投資助手</h1>
          </div>
          <p className="text-lg text-gray-600">專為忙碌投資者設計，一鍵獲得專業投資建議</p>
        </div>

        {/* 一鍵獲取建議按鈕 */}
        <div className="text-center mb-8">
          <Button 
            onClick={fetchDailyRecommendation}
            disabled={loading}
            size="lg"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                分析中...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                一鍵獲取今日投資建議
              </div>
            )}
          </Button>
        </div>

        {/* 錯誤狀態 */}
        {error && (
          <Card className="bg-red-50 border-red-200 mb-6">
            <CardContent className="pt-6">
              <div className="text-center">
                <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-red-800 mb-2">無法獲取投資建議</h3>
                <p className="text-red-600">{error}</p>
                <Button 
                  onClick={fetchDailyRecommendation}
                  className="mt-4 bg-red-600 hover:bg-red-700"
                >
                  重新嘗試
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 主要內容 */}
        {recommendation && recommendation.success && (
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 bg-white rounded-xl shadow-sm">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                今日概覽
              </TabsTrigger>
              <TabsTrigger value="recommended" className="flex items-center gap-2">
                <Star className="w-4 h-4" />
                App推薦股票
              </TabsTrigger>
              <TabsTrigger value="custom" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                自訂清單
              </TabsTrigger>
              <TabsTrigger value="risks" className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                風險提醒
              </TabsTrigger>
            </TabsList>

            {/* 今日概覽 */}
            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* 市場狀態 */}
                <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-gray-800">市場狀態</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">台股指數</span>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{recommendation.market_data?.taiex_price || '17,850'}</span>
                          {(recommendation.market_data?.taiex_change || 125) > 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-500" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-500" />
                          )}
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">VIX 指數</span>
                        <span className="font-semibold">{recommendation.market_data?.vix || '18.2'}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">經濟燈號</span>
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          {recommendation.market_data?.economic_indicator || '綠燈'}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 投資策略 */}
                <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-gray-800">建議策略</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600 mb-2">
                        {recommendation.strategy?.strategy || '平衡策略'}
                      </div>
                      <div className="text-sm text-gray-600 mb-3">
                        建議投入比例
                      </div>
                      <div className="text-3xl font-bold text-green-600">
                        {Math.round((recommendation.strategy?.investment_ratio || 0.6) * 100)}%
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 風險警示 */}
                <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-gray-800">風險警示</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <div className="text-2xl font-bold mb-2">
                        {recommendation.risk_alerts?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600 mb-3">
                        項風險提醒
                      </div>
                      {(recommendation.risk_alerts?.length || 0) > 0 ? (
                        <Badge variant="destructive">需要注意</Badge>
                      ) : (
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          風險可控
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 市場觀點與投資策略整合 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">市場觀點</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {recommendation.advice?.market_outlook || '當前市場處於相對穩定狀態，台股指數表現平穩，VIX 指數維持在低位，顯示市場情緒較為樂觀。建議採取平衡策略，適度配置優質 ETF，同時保持風險控制。'}
                    </p>
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <h4 className="font-semibold text-blue-800 mb-2">操作建議</h4>
                      <p className="text-blue-700 text-sm">
                        {recommendation.advice?.action_advice || '建議分批進場，優先選擇基本面良好的大型 ETF，並適度配置高股息標的以獲得穩定收益。'}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">ETF 分布狀況</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span className="font-medium">綠燈 ETF</span>
                        </div>
                        <span className="font-bold text-green-700">{recommendation.advice?.etf_distribution?.green_lights || 2} 檔</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                          <span className="font-medium">黃燈 ETF</span>
                        </div>
                        <span className="font-bold text-yellow-700">{recommendation.advice?.etf_distribution?.yellow_lights || 2} 檔</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span className="font-medium">紅燈 ETF</span>
                        </div>
                        <span className="font-bold text-red-700">{recommendation.advice?.etf_distribution?.red_lights || 1} 檔</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* App推薦股票 */}
            <TabsContent value="recommended" className="space-y-6">
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">App 推薦股票</CardTitle>
                  <CardDescription>
                    基於當前市場分析，以下是系統推薦的優質 ETF
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {getRecommendedEtfs().length > 0 ? (
                    <div className="space-y-4">
                      {getRecommendedEtfs().map((etf, index) => (
                        <div key={index} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className={`w-3 h-3 rounded-full ${getSignalColor(etf.rating)}`}></div>
                              <div>
                                <span className="font-semibold text-lg">{etf.symbol}</span>
                                <p className="text-sm text-gray-600">{etf.name}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <Badge variant="outline">{etf.rating}</Badge>
                              <span className="text-sm text-gray-600">價格: {formatCurrency(etf.price)}</span>
                              <Button
                                size="sm"
                                onClick={() => addEtf(etf)}
                                disabled={userProfile.selected_etfs.includes(etf.symbol)}
                                className="bg-blue-600 hover:bg-blue-700"
                              >
                                {userProfile.selected_etfs.includes(etf.symbol) ? (
                                  '已加入'
                                ) : (
                                  <>
                                    <Plus className="w-4 h-4 mr-1" />
                                    加入清單
                                  </>
                                )}
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Star className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>暫無推薦股票，請先獲取投資建議</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* 自訂清單 */}
            <TabsContent value="custom" className="space-y-6">
              {/* 投資設定 */}
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">投資設定</CardTitle>
                  <CardDescription>設定您的投資參數</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="cash">可用資金 (TWD)</Label>
                      <Input
                        id="cash"
                        type="number"
                        value={userProfile.available_cash}
                        onChange={(e) => setUserProfile(prev => ({
                          ...prev,
                          available_cash: Number(e.target.value)
                        }))}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="num_etfs">佈局檔數 (0=不限制)</Label>
                      <Input
                        id="num_etfs"
                        type="number"
                        min="0"
                        value={userProfile.num_etfs_to_invest}
                        onChange={(e) => setUserProfile(prev => ({
                          ...prev,
                          num_etfs_to_invest: Number(e.target.value)
                        }))}
                        className="mt-1"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* ETF 搜尋與選擇 */}
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">選擇 ETF</CardTitle>
                  <CardDescription>搜尋並選擇您感興趣的 ETF</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="搜尋 ETF 代號或名稱..."
                      value={etfSearchTerm}
                      onChange={(e) => setEtfSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* 搜尋結果 */}
                  {etfSearchTerm && (
                    <div className="max-h-60 overflow-y-auto border rounded-lg">
                      {filteredEtfs.slice(0, 10).map((etf) => (
                        <div key={etf.symbol} className="p-3 border-b last:border-b-0 hover:bg-gray-50 flex items-center justify-between">
                          <div>
                            <span className="font-semibold">{etf.symbol}</span>
                            <p className="text-sm text-gray-600">{etf.name}</p>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => addEtf(etf)}
                            disabled={userProfile.selected_etfs.includes(etf.symbol)}
                            variant="outline"
                          >
                            {userProfile.selected_etfs.includes(etf.symbol) ? '已選擇' : '新增'}
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* 已選擇的 ETF 清單 */}
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">已選擇的 ETF</CardTitle>
                  <CardDescription>
                    已選擇 {selectedEtfDetails.length} 檔 ETF，投資配置如下
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {selectedEtfDetails.length > 0 ? (
                    <div className="space-y-4">
                      {calculateCustomPositions().map((position, index) => (
                        <div key={index} className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <div>
                                <span className="font-semibold text-lg">{position.symbol}</span>
                                <p className="text-sm text-gray-600">{position.name}</p>
                              </div>
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeEtf(position.symbol)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">建議股數:</span>
                              <span className="font-semibold ml-1">{position.shares} 股</span>
                            </div>
                            <div>
                              <span className="text-gray-600">價格:</span>
                              <span className="font-semibold ml-1">{formatCurrency(position.price)}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">投入金額:</span>
                              <span className="font-semibold ml-1">{formatCurrency(position.amount)}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">權重:</span>
                              <span className="font-semibold ml-1">{position.weight.toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Settings className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>尚未選擇任何 ETF</p>
                      <p className="text-sm">請使用上方搜尋功能或從「App推薦股票」頁面加入</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* 風險提醒 */}
            <TabsContent value="risks" className="space-y-6">
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">風險提醒</CardTitle>
                  <CardDescription>
                    當前市場風險警示與注意事項
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {recommendation.risk_alerts && recommendation.risk_alerts.length > 0 ? (
                    <div className="space-y-4">
                      {recommendation.risk_alerts.map((alert, index) => {
                        const isInCustomList = userProfile.selected_etfs.includes(alert.symbol)
                        return (
                          <div key={index} className={`p-4 border rounded-lg ${
                            alert.level === '高風險' ? 'border-red-200 bg-red-50' :
                            alert.level === '中風險' ? 'border-yellow-200 bg-yellow-50' :
                            'border-blue-200 bg-blue-50'
                          }`}>
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="font-semibold">{alert.symbol}</span>
                                  <Badge variant={
                                    alert.level === '高風險' ? 'destructive' :
                                    alert.level === '中風險' ? 'default' : 'secondary'
                                  }>
                                    {alert.level}
                                  </Badge>
                                  {isInCustomList && (
                                    <Badge variant="outline" className="bg-blue-100 text-blue-700">
                                      在自選清單中
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
                                <p className="text-xs text-gray-600">建議行動: {alert.action}</p>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>目前無風險警示</p>
                      <p className="text-sm">市場狀況良好，請持續關注</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  )
}

export default App
