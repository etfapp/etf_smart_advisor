import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { TrendingUp, TrendingDown, DollarSign, Target, AlertTriangle, BarChart3, Zap, Brain, Settings, Search, Plus, X, Star, Loader2, RefreshCw, CheckCircle, XCircle, Info } from 'lucide-react'
import './App.css'

// API 基礎 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV ? 'http://localhost:5000/api' : '/api');

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
  
  // 新增狀態：自訂投資配置
  const [customPositions, setCustomPositions] = useState([])
  const [adjustmentModal, setAdjustmentModal] = useState({ open: false, etf: null })
  const [calculationMode, setCalculationMode] = useState('smart') // 'smart' | 'manual' | 'hybrid'

  // 獲取所有 ETF 清單
  const fetchAllEtfs = async () => {
    setLoadingEtfs(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/etf-list`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        // 修復API響應格式問題
        if (Array.isArray(data)) {
          setAllEtfs(data)
        } else if (data.success && Array.isArray(data.data)) {
          setAllEtfs(data.data)
        } else if (Array.isArray(data.etfs)) {
          setAllEtfs(data.etfs)
        } else {
          console.warn('ETF清單格式異常:', data)
          setAllEtfs([])
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      console.error('獲取 ETF 清單失敗:', error)
      setError(`無法獲取ETF清單: ${error.message}`)
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
        if (data.success) {
          setRecommendation(data)
          // 自動計算自訂清單的投資配置
          if (userProfile.selected_etfs.length > 0) {
            calculateAllSelectedPositions(data)
          }
        } else {
          throw new Error(data.error || '獲取投資建議失敗')
        }
      } else {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      console.error('獲取投資建議失敗:', error)
      setError(`無法獲取投資建議: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  // 計算所有自選ETF的投資配置
  const calculateAllSelectedPositions = (recommendationData) => {
    if (!recommendationData || !userProfile.selected_etfs.length) return

    const positions = []
    const totalCash = userProfile.available_cash
    const investmentRatio = recommendationData.strategy?.investment_ratio || 0.6
    const totalInvestment = totalCash * investmentRatio
    const perEtfAmount = totalInvestment / userProfile.selected_etfs.length

    userProfile.selected_etfs.forEach(symbol => {
      // 從推薦數據中找到對應的ETF信息
      const etfInfo = allEtfs.find(etf => etf.symbol === symbol)
      if (etfInfo) {
        const price = 50 // 預設價格，實際應從API獲取
        const shares = Math.floor(perEtfAmount / price)
        const actualAmount = shares * price

        positions.push({
          symbol,
          name: etfInfo.name || symbol,
          shares,
          price,
          amount: actualAmount,
          weight: (actualAmount / totalInvestment) * 100
        })
      }
    })

    setCustomPositions(positions)
  }

  // 添加ETF到自選清單
  const addToSelectedEtfs = (symbol) => {
    if (!userProfile.selected_etfs.includes(symbol)) {
      setUserProfile(prev => ({
        ...prev,
        selected_etfs: [...prev.selected_etfs, symbol]
      }))
    }
  }

  // 從自選清單移除ETF
  const removeFromSelectedEtfs = (symbol) => {
    setUserProfile(prev => ({
      ...prev,
      selected_etfs: prev.selected_etfs.filter(s => s !== symbol)
    }))
  }

  // 格式化數字
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toLocaleString()
  }

  // 格式化貨幣
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  // 獲取評級顏色
  const getRatingColor = (rating) => {
    switch (rating) {
      case '綠燈': return 'bg-green-500'
      case '黃燈': return 'bg-yellow-500'
      case '橙燈': return 'bg-orange-500'
      case '紅燈': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  // 獲取評級圖標
  const getRatingIcon = (rating) => {
    switch (rating) {
      case '綠燈': return <CheckCircle className="w-4 h-4" />
      case '黃燈': return <Info className="w-4 h-4" />
      case '橙燈': return <AlertTriangle className="w-4 h-4" />
      case '紅燈': return <XCircle className="w-4 h-4" />
      default: return <Info className="w-4 h-4" />
    }
  }

  // 過濾ETF清單
  const filteredEtfs = allEtfs.filter(etf =>
    etf.symbol.toLowerCase().includes(etfSearchTerm.toLowerCase()) ||
    etf.name.toLowerCase().includes(etfSearchTerm.toLowerCase())
  )

  // 初始化時獲取ETF清單
  useEffect(() => {
    fetchAllEtfs()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* 標題區域 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center justify-center gap-3">
            <Brain className="w-10 h-10 text-blue-600" />
            ETF智能投資顧問
          </h1>
          <p className="text-gray-600 text-lg">
            基於真實技術指標的智能投資建議系統
          </p>
        </div>

        {/* 錯誤提示 */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="recommendation" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="recommendation" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              投資建議
            </TabsTrigger>
            <TabsTrigger value="etf-selection" className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              ETF選擇
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              設定
            </TabsTrigger>
          </TabsList>

          {/* 投資建議頁面 */}
          <TabsContent value="recommendation" className="space-y-6">
            {/* 用戶配置卡片 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5" />
                  投資配置
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="available_cash">可用資金 (TWD)</Label>
                    <Input
                      id="available_cash"
                      type="number"
                      value={userProfile.available_cash}
                      onChange={(e) => setUserProfile(prev => ({
                        ...prev,
                        available_cash: parseInt(e.target.value) || 0
                      }))}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="num_etfs">投資檔數 (0=自動)</Label>
                    <Input
                      id="num_etfs"
                      type="number"
                      value={userProfile.num_etfs_to_invest}
                      onChange={(e) => setUserProfile(prev => ({
                        ...prev,
                        num_etfs_to_invest: parseInt(e.target.value) || 0
                      }))}
                      className="mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button 
                      onClick={fetchDailyRecommendation} 
                      disabled={loading}
                      className="w-full"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          分析中...
                        </>
                      ) : (
                        <>
                          <Zap className="w-4 h-4 mr-2" />
                          獲取建議
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                {/* 自選ETF顯示 */}
                {userProfile.selected_etfs.length > 0 && (
                  <div>
                    <Label>自選ETF清單</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {userProfile.selected_etfs.map(symbol => (
                        <Badge key={symbol} variant="secondary" className="flex items-center gap-1">
                          {symbol}
                          <X 
                            className="w-3 h-3 cursor-pointer hover:text-red-500" 
                            onClick={() => removeFromSelectedEtfs(symbol)}
                          />
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 投資建議結果 */}
            {recommendation && (
              <div className="space-y-6">
                {/* 市場策略 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      市場分析與策略
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="font-semibold text-lg mb-2">{recommendation.strategy?.strategy}</h3>
                        <p className="text-gray-600 mb-4">{recommendation.strategy?.description}</p>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>建議投資比例:</span>
                            <span className="font-semibold">
                              {((recommendation.strategy?.investment_ratio || 0) * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>建議投資金額:</span>
                            <span className="font-semibold text-green-600">
                              {formatCurrency(userProfile.available_cash * (recommendation.strategy?.investment_ratio || 0))}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">市場指標</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>VIX恐慌指數:</span>
                            <span>{recommendation.market_data?.vix?.toFixed(1) || 'N/A'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>台股RSI:</span>
                            <span>{recommendation.market_data?.taiex_rsi?.toFixed(1) || 'N/A'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>經濟指標:</span>
                            <span>{recommendation.market_data?.economic_indicator || 'N/A'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>綜合評分:</span>
                            <span className="font-semibold">
                              {recommendation.strategy?.scores?.total_score?.toFixed(1) || 'N/A'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 投資建議 */}
                {recommendation.positions && recommendation.positions.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        推薦投資配置
                      </CardTitle>
                      <CardDescription>
                        基於當前市場環境和技術分析的最佳投資組合
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {recommendation.positions.map((position, index) => (
                          <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full ${getRatingColor(position.rating)}`}></div>
                                <div>
                                  <h3 className="font-semibold">{position.symbol}</h3>
                                  <p className="text-sm text-gray-600">{position.name}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="font-semibold text-lg">{formatCurrency(position.amount)}</div>
                                <div className="text-sm text-gray-600">{position.shares} 股</div>
                              </div>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-600">股價:</span>
                                <span className="ml-1 font-medium">{formatCurrency(position.price)}</span>
                              </div>
                              <div>
                                <span className="text-gray-600">權重:</span>
                                <span className="ml-1 font-medium">{position.weight.toFixed(1)}%</span>
                              </div>
                              <div>
                                <span className="text-gray-600">評級:</span>
                                <span className="ml-1 font-medium flex items-center gap-1">
                                  {getRatingIcon(position.rating)}
                                  {position.rating}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-600">建議:</span>
                                <span className="ml-1 font-medium">{position.recommendation}</span>
                              </div>
                            </div>
                            {position.reasoning && (
                              <div className="mt-2 text-sm text-gray-600 bg-gray-100 p-2 rounded">
                                <strong>投資理由:</strong> {position.reasoning}
                              </div>
                            )}
                            {position.price_level && (
                              <div className="mt-2 text-sm">
                                <div className="flex items-center gap-2">
                                  <span className="text-gray-600">價格水位:</span>
                                  <Badge variant={position.price_level.signal === '綠燈' ? 'default' : 'secondary'}>
                                    {position.price_level.level} ({position.price_level.percentile}%)
                                  </Badge>
                                </div>
                                <div className="text-xs text-gray-500 mt-1">
                                  {position.price_level.description}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* 風險警示 */}
                {recommendation.risk_alerts && recommendation.risk_alerts.length > 0 && (
                  <Card className="border-orange-200 bg-orange-50">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-orange-800">
                        <AlertTriangle className="w-5 h-5" />
                        風險警示
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {recommendation.risk_alerts.map((alert, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-white rounded border-l-4 border-orange-400">
                            <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5" />
                            <div>
                              <h4 className="font-semibold text-orange-800">{alert.title}</h4>
                              <p className="text-orange-700 text-sm">{alert.message}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* 投資建議總結 */}
                {recommendation.advice && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Brain className="w-5 h-5" />
                        投資建議總結
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-semibold mb-2">市場觀點</h4>
                          <p className="text-gray-700">{recommendation.advice.market_outlook}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold mb-2">操作建議</h4>
                          <p className="text-gray-700">{recommendation.advice.action_advice}</p>
                        </div>
                        {recommendation.advice.specific_advice && recommendation.advice.specific_advice.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-2">具體建議</h4>
                            <ul className="list-disc list-inside space-y-1 text-gray-700">
                              {recommendation.advice.specific_advice.map((advice, index) => (
                                <li key={index}>{advice}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {recommendation.advice.investment_tips && recommendation.advice.investment_tips.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-2">投資小貼士</h4>
                            <ul className="list-disc list-inside space-y-1 text-gray-700">
                              {recommendation.advice.investment_tips.map((tip, index) => (
                                <li key={index}>{tip}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 p-4 bg-gray-50 rounded">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {recommendation.advice.etf_distribution?.green_lights || 0}
                            </div>
                            <div className="text-sm text-gray-600">綠燈ETF</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-yellow-600">
                              {recommendation.advice.etf_distribution?.yellow_lights || 0}
                            </div>
                            <div className="text-sm text-gray-600">黃燈ETF</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-orange-600">
                              {recommendation.advice.etf_distribution?.orange_lights || 0}
                            </div>
                            <div className="text-sm text-gray-600">橙燈ETF</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-red-600">
                              {recommendation.advice.etf_distribution?.red_lights || 0}
                            </div>
                            <div className="text-sm text-gray-600">紅燈ETF</div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* 無建議時的提示 */}
            {!recommendation && !loading && (
              <Card>
                <CardContent className="text-center py-12">
                  <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">
                    準備獲取投資建議
                  </h3>
                  <p className="text-gray-500 mb-4">
                    設定您的投資金額和偏好，點擊「獲取建議」開始分析
                  </p>
                  <Button onClick={fetchDailyRecommendation} disabled={loading}>
                    <Zap className="w-4 h-4 mr-2" />
                    開始分析
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* ETF選擇頁面 */}
          <TabsContent value="etf-selection" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  ETF搜尋與選擇
                </CardTitle>
                <CardDescription>
                  搜尋並選擇您感興趣的ETF加入自選清單
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <Input
                        placeholder="搜尋ETF代碼或名稱..."
                        value={etfSearchTerm}
                        onChange={(e) => setEtfSearchTerm(e.target.value)}
                        className="w-full"
                      />
                    </div>
                    <Button onClick={fetchAllEtfs} disabled={loadingEtfs} variant="outline">
                      {loadingEtfs ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4" />
                      )}
                    </Button>
                  </div>

                  {loadingEtfs && (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                      <p className="text-gray-600">載入ETF清單中...</p>
                    </div>
                  )}

                  {!loadingEtfs && filteredEtfs.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
                      {filteredEtfs.slice(0, 50).map((etf) => (
                        <div key={etf.symbol} className="border rounded-lg p-3 hover:bg-gray-50 transition-colors">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="font-semibold">{etf.symbol}</h3>
                              <p className="text-sm text-gray-600 truncate">{etf.name}</p>
                              {etf.category && (
                                <Badge variant="outline" className="text-xs mt-1">
                                  {etf.category}
                                </Badge>
                              )}
                            </div>
                            <Button
                              size="sm"
                              variant={userProfile.selected_etfs.includes(etf.symbol) ? "default" : "outline"}
                              onClick={() => {
                                if (userProfile.selected_etfs.includes(etf.symbol)) {
                                  removeFromSelectedEtfs(etf.symbol)
                                } else {
                                  addToSelectedEtfs(etf.symbol)
                                }
                              }}
                            >
                              {userProfile.selected_etfs.includes(etf.symbol) ? (
                                <Star className="w-4 h-4 fill-current" />
                              ) : (
                                <Plus className="w-4 h-4" />
                              )}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {!loadingEtfs && filteredEtfs.length === 0 && etfSearchTerm && (
                    <div className="text-center py-8 text-gray-500">
                      找不到符合條件的ETF
                    </div>
                  )}

                  {!loadingEtfs && allEtfs.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      暫無ETF數據，請點擊重新整理
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 設定頁面 */}
          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  系統設定
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h3 className="font-semibold mb-2">關於系統</h3>
                    <p className="text-gray-600 text-sm mb-2">
                      ETF智能投資顧問 v2.0 - 基於真實技術指標的投資建議系統
                    </p>
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>• 支援 {allEtfs.length} 檔台股ETF</div>
                      <div>• 整合RSI、MACD、移動平均線等技術指標</div>
                      <div>• 智能價格水位分析</div>
                      <div>• 多維度風險監控</div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">免責聲明</h3>
                    <div className="text-xs text-gray-500 space-y-1 bg-gray-50 p-3 rounded">
                      <div>• 本系統提供的投資建議僅供參考，不構成投資建議</div>
                      <div>• 投資有風險，請根據自身風險承受能力謹慎決策</div>
                      <div>• 過往績效不代表未來表現</div>
                      <div>• 建議諮詢專業投資顧問</div>
                    </div>
                  </div>

                  {recommendation && (
                    <div>
                      <h3 className="font-semibold mb-2">系統狀態</h3>
                      <div className="text-sm space-y-2">
                        <div className="flex justify-between">
                          <span>最後更新:</span>
                          <span>{new Date(recommendation.updated_at).toLocaleString('zh-TW')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>分析ETF數量:</span>
                          <span>{recommendation.etf_analysis?.total_analyzed || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>合格ETF數量:</span>
                          <span>{recommendation.etf_analysis?.qualified_etfs || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>推薦ETF數量:</span>
                          <span>{recommendation.etf_analysis?.recommended_etfs || 0}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

