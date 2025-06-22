import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { TrendingUp, TrendingDown, DollarSign, Target, AlertTriangle, BarChart3, Zap, Brain } from 'lucide-react'
import './App.css'

// API 基礎 URL
const API_BASE_URL = 'https://etf-smart-advisor.onrender.com'

function App() {
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userProfile, setUserProfile] = useState({
    available_cash: 100000
  })

  // 獲取每日投資建議
  const fetchDailyRecommendation = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/api/daily-recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userProfile)
      })
      
      if (response.ok) {
        const data = await response.json()
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

  // 頁面載入時自動獲取建議
  useEffect(() => {
    fetchDailyRecommendation()
  }, [])

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
              <TabsTrigger value="strategy" className="flex items-center gap-2">
                <Target className="w-4 h-4" />
                投資策略
              </TabsTrigger>
              <TabsTrigger value="positions" className="flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                建議配置
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

              {/* 市場觀點 */}
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">市場觀點</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {recommendation.advice?.market_outlook || '當前市場處於相對穩定狀態，台股指數表現平穩，VIX 指數維持在低位，顯示市場情緒較為樂觀。建議採取平衡策略，適度配置優質 ETF，同時保持風險控制。'}
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* 投資策略 */}
            <TabsContent value="strategy" className="space-y-6">
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">策略說明</CardTitle>
                  <CardDescription>
                    {recommendation.strategy?.description || '基於當前市場環境，建議採取平衡投資策略，兼顧成長與穩定收益。'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-semibold text-blue-800 mb-2">操作建議</h4>
                      <p className="text-blue-700 text-sm">
                        {recommendation.advice?.action_advice || '建議分批進場，優先選擇基本面良好的大型 ETF，並適度配置高股息標的以獲得穩定收益。'}
                      </p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-2">ETF 分布</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span>綠燈 ETF:</span>
                          <span className="font-semibold">{recommendation.advice?.etf_distribution?.green_lights || 2} 檔</span>
                        </div>
                        <div className="flex justify-between">
                          <span>黃燈 ETF:</span>
                          <span className="font-semibold">{recommendation.advice?.etf_distribution?.yellow_lights || 2} 檔</span>
                        </div>
                        <div className="flex justify-between">
                          <span>紅燈 ETF:</span>
                          <span className="font-semibold">{recommendation.advice?.etf_distribution?.red_lights || 1} 檔</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* 建議配置 */}
            <TabsContent value="positions" className="space-y-6">
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">建議投資配置</CardTitle>
                  <CardDescription>
                    基於您的資金 {formatCurrency(userProfile.available_cash)} 的最佳配置建議
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {recommendation.positions && recommendation.positions.length > 0 ? (
                    <div className="space-y-4">
                      {recommendation.positions.map((position, index) => (
                        <div key={index} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <div className={`w-3 h-3 rounded-full ${getSignalColor(position.rating)}`}></div>
                              <div>
                                <span className="font-semibold text-lg">{position.symbol}</span>
                                <p className="text-sm text-gray-600">{position.name}</p>
                              </div>
                            </div>
                            <Badge variant="outline">{position.rating}</Badge>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">股數:</span>
                              <span className="font-semibold ml-1">{position.shares} 股</span>
                            </div>
                            <div>
                              <span className="text-gray-600">價格:</span>
                              <span className="font-semibold ml-1">{formatCurrency(position.price)}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">金額:</span>
                              <span className="font-semibold ml-1">{formatCurrency(position.amount)}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">權重:</span>
                              <span className="font-semibold ml-1">{position.weight}%</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      目前沒有合適的投資建議，建議等待更好的進場時機
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
                    {recommendation.advice?.risk_reminder || '投資有風險，請根據個人風險承受能力謹慎投資。'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {recommendation.risk_alerts && recommendation.risk_alerts.length > 0 ? (
                    <div className="space-y-4">
                      {recommendation.risk_alerts.map((alert, index) => (
                        <div key={index} className="p-4 border-l-4 border-yellow-400 bg-yellow-50 rounded-r-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-yellow-600" />
                            <span className="font-semibold text-yellow-800">{alert.symbol}</span>
                            <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-300">
                              {alert.level}
                            </Badge>
                          </div>
                          <p className="text-yellow-700 text-sm mb-2">{alert.message}</p>
                          <p className="text-yellow-600 text-xs font-medium">建議行動: {alert.action}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Target className="w-8 h-8 text-green-600" />
                      </div>
                      <p className="text-green-700 font-medium">目前無特別風險警示</p>
                      <p className="text-green-600 text-sm mt-1">請持續關注市場變化</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}

        {/* 載入狀態 */}
        {loading && !recommendation && (
          <div className="text-center py-12">
            <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">正在分析市場數據，請稍候...</p>
          </div>
        )}

        {/* 頁腳 */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>© 2024 台股 ETF 智能投資助手 - 投資有風險，請謹慎評估</p>
        </div>
      </div>
    </div>
  )
}

export default App

