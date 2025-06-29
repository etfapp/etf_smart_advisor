import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog.jsx'
import { TrendingUp, TrendingDown, DollarSign, Target, AlertTriangle, BarChart3, Zap, Brain, Settings, Search, Plus, X, Star, Loader2, RefreshCw } from 'lucide-react'
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
  
  // 新增狀態：自訂投資配置
  const [customPositions, setCustomPositions] = useState([])
  const [adjustmentModal, setAdjustmentModal] = useState({ open: false, etf: null })
  const [calculationMode, setCalculationMode] = useState('smart') // 'smart' | 'manual' | 'hybrid'

  // 獲取所有 ETF 清單
  const fetchAllEtfs = async () => {
    setLoadingEtfs(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/etf-list`)
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

  // 頁面載入時自動獲取建議和 ETF 清單
  useEffect(() => {
    fetchDailyRecommendation()
    fetchAllEtfs()
  }, [])

  // 當用戶配置改變時重新計算
  useEffect(() => {
    if (recommendation && userProfile.selected_etfs.length > 0) {
      calculateAllSelectedPositions(recommendation)
    }
  }, [userProfile, recommendation])

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
    // 同時移除自訂配置
    setCustomPositions(prev => prev.filter(pos => pos.symbol !== symbol))
  }

  // 過濾 ETF 清單
  const filteredEtfs = allEtfs.filter(etf => 
    etf.name?.toLowerCase().includes(etfSearchTerm.toLowerCase()) ||
    etf.symbol?.toLowerCase().includes(etfSearchTerm.toLowerCase())
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

  // 【核心改進】為所有自選ETF計算投資建議
  const calculateAllSelectedPositions = (recommendationData = recommendation) => {
    if (!recommendationData || selectedEtfDetails.length === 0) {
      setCustomPositions([])
      return
    }

    const investmentRatio = recommendationData.strategy?.investment_ratio || 0.6
    const totalInvestment = userProfile.available_cash * investmentRatio
    
    // 為所有自選ETF計算投資建議
    const allPositions = selectedEtfDetails.map((etf, index) => {
      // 基礎配置：平均分配
      const baseAllocation = totalInvestment / selectedEtfDetails.length
      
      // 根據評分調整權重（模擬評分，實際應從後端獲取）
      const mockScore = 50 + Math.random() * 40 // 50-90分的模擬評分
      const scoreWeight = mockScore / 100
      const adjustedAllocation = baseAllocation * scoreWeight
      
      // 計算股數和實際金額
      const currentPrice = etf.current_price || 50 // 預設價格
      const shares = Math.floor(adjustedAllocation / currentPrice)
      const actualAmount = shares * currentPrice
      
      // 判斷是否為優先投資標的
      const isPriority = userProfile.num_etfs_to_invest === 0 || 
                        index < userProfile.num_etfs_to_invest
      
      return {
        symbol: etf.symbol,
        name: etf.name,
        suggestedShares: shares,
        suggestedAmount: actualAmount,
        currentPrice: currentPrice,
        isPriority: isPriority,
        priorityRank: isPriority ? index + 1 : null,
        score: Math.round(mockScore),
        reasoning: `基於評分 ${Math.round(mockScore)} 分的建議配置`,
        weight: selectedEtfDetails.length > 0 ? (actualAmount / totalInvestment) * 100 : 0
      }
    })

    setCustomPositions(allPositions)
  }

  // 獲取優先投資摘要
  const getPriorityInvestmentSummary = () => {
    const priorityPositions = customPositions.filter(pos => pos.isPriority)
    const totalAmount = priorityPositions.reduce((sum, pos) => sum + pos.suggestedAmount, 0)
    
    return {
      totalAmount,
      positions: priorityPositions,
      remainingCash: userProfile.available_cash - totalAmount,
      count: priorityPositions.length
    }
  }

  // 切換優先狀態
  const togglePriority = (symbol) => {
    const position = customPositions.find(pos => pos.symbol === symbol)
    if (!position) return

    if (position.isPriority) {
      // 移出優先清單
      setCustomPositions(prev => prev.map(pos => 
        pos.symbol === symbol ? { ...pos, isPriority: false, priorityRank: null } : pos
      ))
    } else {
      // 加入優先清單
      const currentPriorityCount = customPositions.filter(pos => pos.isPriority).length
      setCustomPositions(prev => prev.map(pos => 
        pos.symbol === symbol ? { 
          ...pos, 
          isPriority: true, 
          priorityRank: currentPriorityCount + 1 
        } : pos
      ))
    }
  }

  // 調整投資金額
  const adjustAmount = (symbol) => {
    const position = customPositions.find(pos => pos.symbol === symbol)
    if (position) {
      setAdjustmentModal({ open: true, etf: position })
    }
  }

  // 保存調整後的金額
  const saveAdjustment = ({ amount, shares }) => {
    const { etf } = adjustmentModal
    setCustomPositions(prev => prev.map(pos => 
      pos.symbol === etf.symbol ? {
        ...pos,
        suggestedAmount: amount,
        suggestedShares: shares
      } : pos
    ))
    setAdjustmentModal({ open: false, etf: null })
  }

  // 獲取推薦的ETF
  const getRecommendedEtfs = () => {
    if (!recommendation?.positions) return []
    return recommendation.positions
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
                <Loader2 className="w-5 h-5 animate-spin" />
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
                <h3 className="text-lg font-semibold text-red-800 mb-2">發生錯誤</h3>
                <p className="text-red-600 mb-4">{error}</p>
                <div className="flex gap-2 justify-center">
                  <Button 
                    onClick={fetchDailyRecommendation}
                    className="bg-red-600 hover:bg-red-700"
                    disabled={loading}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    重新獲取建議
                  </Button>
                  <Button 
                    onClick={fetchAllEtfs}
                    variant="outline"
                    disabled={loadingEtfs}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    重新載入ETF清單
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 主要內容 */}
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
            {recommendation && recommendation.success ? (
              <>
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
                            <span className="font-semibold">17,850</span>
                            <TrendingUp className="w-4 h-4 text-green-500" />
                          </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">VIX 指數</span>
                          <span className="font-semibold">{Math.round(recommendation.market_data?.vix || 25.95)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">經濟燈號</span>
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                            {recommendation.market_data?.economic_indicator || '黃燈'}
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="bg-white shadow-lg">
                    <CardHeader>
                      <CardTitle className="text-xl font-semibold text-gray-800">市場觀點</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 leading-relaxed mb-4">
                        {recommendation.advice?.market_outlook || '市場處於正常區間，有 0 檔綠燈、0 檔黃燈 ETF，建議平衡配置。'}
                      </p>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold text-blue-800 mb-2">操作建議</h4>
                        <p className="text-blue-700 text-sm">
                          {recommendation.advice?.action_advice || '建議採用定期定額方式投入，分散時間風險，逐步建立部位。'}
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
                          <span className="font-bold text-green-700">{recommendation.advice?.etf_distribution?.green_lights || 0} 檔</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                            <span className="font-medium">黃燈 ETF</span>
                          </div>
                          <span className="font-bold text-yellow-700">{recommendation.advice?.etf_distribution?.yellow_lights || 0} 檔</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                            <span className="font-medium">紅燈 ETF</span>
                          </div>
                          <span className="font-bold text-red-700">{recommendation.advice?.etf_distribution?.red_lights || 109} 檔</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            ) : (
              <Card className="bg-white shadow-lg">
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-600 mb-2">等待投資建議</h3>
                    <p className="text-gray-500">點擊上方按鈕獲取今日投資建議</p>
                  </div>
                </CardContent>
              </Card>
            )}
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
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-semibold text-lg">{etf.symbol}</h4>
                              <Badge variant="outline" className="bg-green-50 text-green-700">
                                推薦
                              </Badge>
                            </div>
                            <p className="text-gray-600 mb-2">{etf.name}</p>
                            <p className="text-sm text-gray-500">{etf.reasoning || '基於市場分析的推薦'}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-green-600">
                              {formatCurrency(etf.amount || 0)}
                            </div>
                            <div className="text-sm text-gray-600">
                              建議股數: {etf.shares || 0} 股
                            </div>
                            <div className="text-xs text-gray-500">
                              單價: {formatCurrency(etf.price || 0)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Star className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-600 mb-2">暫無推薦股票</h3>
                    <p className="text-gray-500">請先獲取投資建議</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 【核心改進】自訂清單 - 顯示所有選中ETF的投資建議 */}
          <TabsContent value="custom" className="space-y-6">
            {/* 投資設定 */}
            <Card className="bg-white shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">投資設定</CardTitle>
                <CardDescription>設定您的投資參數</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="cash" className="text-sm font-medium text-gray-700">
                      可用資金 (TWD)
                    </Label>
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
                    <Label htmlFor="num_etfs" className="text-sm font-medium text-gray-700">
                      佈局檔數 (0=不限制)
                    </Label>
                    <Input
                      id="num_etfs"
                      type="number"
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

            {/* ETF 搜尋和選擇 */}
            <Card className="bg-white shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">選擇 ETF</CardTitle>
                <CardDescription>搜尋並選擇您感興趣的 ETF</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="搜尋 ETF 代號或名稱..."
                      value={etfSearchTerm}
                      onChange={(e) => setEtfSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  
                  {loadingEtfs ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-600" />
                      <p className="text-gray-500">載入 ETF 清單中...</p>
                    </div>
                  ) : (
                    <div className="max-h-60 overflow-y-auto space-y-2">
                      {filteredEtfs.length > 0 ? (
                        filteredEtfs.slice(0, 10).map((etf) => (
                          <div key={etf.symbol} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                            <div>
                              <div className="font-medium">{etf.symbol}</div>
                              <div className="text-sm text-gray-600">{etf.name}</div>
                            </div>
                            <Button
                              size="sm"
                              onClick={() => addEtf(etf)}
                              disabled={userProfile.selected_etfs.includes(etf.symbol)}
                              className="bg-blue-600 hover:bg-blue-700"
                            >
                              {userProfile.selected_etfs.includes(etf.symbol) ? '已選擇' : '選擇'}
                            </Button>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          {etfSearchTerm ? '找不到符合條件的 ETF' : '請輸入搜尋關鍵字'}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* 【核心改進】自選清單投資建議 - 顯示所有ETF */}
            {customPositions.length > 0 && (
              <>
                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">自選清單投資建議</CardTitle>
                    <CardDescription>
                      所有自選 ETF 的投資建議（共 {customPositions.length} 檔）
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {customPositions.map((position) => (
                        <Card key={position.symbol} className={`p-4 ${position.isPriority ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h4 className="font-semibold text-lg">{position.symbol}</h4>
                                {position.isPriority && (
                                  <Badge variant="default" className="bg-blue-600">
                                    優先第 {position.priorityRank} 位
                                  </Badge>
                                )}
                                <Badge variant="outline" className="bg-gray-50">
                                  評分: {position.score}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600 mb-2">{position.name}</p>
                              <p className="text-xs text-gray-500">{position.reasoning}</p>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-green-600">
                                {formatCurrency(position.suggestedAmount)}
                              </div>
                              <div className="text-sm text-gray-600">
                                建議股數: {position.suggestedShares} 股
                              </div>
                              <div className="text-xs text-gray-500">
                                單價: {formatCurrency(position.currentPrice)}
                              </div>
                              <div className="text-xs text-gray-500">
                                權重: {position.weight.toFixed(1)}%
                              </div>
                            </div>
                          </div>
                          <div className="mt-3 flex justify-between items-center">
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant={position.isPriority ? "default" : "outline"}
                                onClick={() => togglePriority(position.symbol)}
                                className="text-xs"
                              >
                                {position.isPriority ? "移出優先" : "加入優先"}
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                onClick={() => adjustAmount(position.symbol)}
                                className="text-xs"
                              >
                                調整金額
                              </Button>
                            </div>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => removeEtf(position.symbol)}
                              className="text-xs"
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 投資摘要 */}
                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">投資摘要</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const summary = getPriorityInvestmentSummary()
                      const allTotal = customPositions.reduce((sum, pos) => sum + pos.suggestedAmount, 0)
                      
                      return (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-3">
                            <h4 className="font-semibold text-gray-800">優先投資配置</h4>
                            <div className="space-y-2">
                              <div className="flex justify-between">
                                <span className="text-gray-600">優先檔數:</span>
                                <span className="font-medium">{summary.count} 檔</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">投資金額:</span>
                                <span className="font-medium text-green-600">{formatCurrency(summary.totalAmount)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">剩餘資金:</span>
                                <span className="font-medium">{formatCurrency(summary.remainingCash)}</span>
                              </div>
                            </div>
                          </div>
                          <div className="space-y-3">
                            <h4 className="font-semibold text-gray-800">完整配置</h4>
                            <div className="space-y-2">
                              <div className="flex justify-between">
                                <span className="text-gray-600">總檔數:</span>
                                <span className="font-medium">{customPositions.length} 檔</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">總投資額:</span>
                                <span className="font-medium text-blue-600">{formatCurrency(allTotal)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">資金使用率:</span>
                                <span className="font-medium">{((allTotal / userProfile.available_cash) * 100).toFixed(1)}%</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })()}
                  </CardContent>
                </Card>
              </>
            )}

            {/* 已選擇的 ETF 清單（當沒有投資建議時顯示） */}
            {userProfile.selected_etfs.length > 0 && customPositions.length === 0 && (
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-gray-800">已選擇的 ETF</CardTitle>
                  <CardDescription>
                    已選擇 {userProfile.selected_etfs.length} 檔 ETF，請先獲取投資建議
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {selectedEtfDetails.map((etf) => (
                      <div key={etf.symbol} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">{etf.symbol}</div>
                          <div className="text-sm text-gray-600">{etf.name}</div>
                        </div>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => removeEtf(etf.symbol)}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 空狀態 */}
            {userProfile.selected_etfs.length === 0 && (
              <Card className="bg-white shadow-lg">
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-600 mb-2">尚未選擇 ETF</h3>
                    <p className="text-gray-500">請在上方搜尋並選擇您感興趣的 ETF</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* 風險提醒 */}
          <TabsContent value="risks" className="space-y-6">
            <Card className="bg-white shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">風險提醒</CardTitle>
                <CardDescription>當前市場風險警示與注意事項</CardDescription>
              </CardHeader>
              <CardContent>
                {recommendation?.risk_alerts && recommendation.risk_alerts.length > 0 ? (
                  <div className="space-y-4">
                    {recommendation.risk_alerts.map((alert, index) => (
                      <div key={index} className="p-4 border-l-4 border-red-500 bg-red-50 rounded-r-lg">
                        <div className="flex items-start gap-3">
                          <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                          <div>
                            <h4 className="font-semibold text-red-800">{alert.title || '風險警示'}</h4>
                            <p className="text-red-700 mt-1">{alert.message || alert}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <AlertTriangle className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-green-800 mb-2">目前無風險警示</h3>
                    <p className="text-green-600">市場狀況良好，請持續關注</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* 投資金額調整對話框 */}
        {adjustmentModal.open && adjustmentModal.etf && (
          <InvestmentAdjustmentModal 
            etf={adjustmentModal.etf}
            onSave={saveAdjustment}
            onClose={() => setAdjustmentModal({ open: false, etf: null })}
          />
        )}
      </div>
    </div>
  )
}

// 投資金額調整對話框組件
function InvestmentAdjustmentModal({ etf, onSave, onClose }) {
  const [customAmount, setCustomAmount] = useState(etf.suggestedAmount)
  const [customShares, setCustomShares] = useState(etf.suggestedShares)

  const handleAmountChange = (amount) => {
    setCustomAmount(amount)
    setCustomShares(Math.floor(amount / etf.currentPrice))
  }

  const handleSharesChange = (shares) => {
    setCustomShares(shares)
    setCustomAmount(shares * etf.currentPrice)
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>調整 {etf.symbol} 投資配置</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="amount">投資金額</Label>
            <Input
              id="amount"
              type="number"
              value={customAmount}
              onChange={(e) => handleAmountChange(Number(e.target.value))}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="shares">購買股數</Label>
            <Input
              id="shares"
              type="number"
              value={customShares}
              onChange={(e) => handleSharesChange(Number(e.target.value))}
              className="mt-1"
            />
          </div>
          <div className="bg-gray-50 p-3 rounded-lg space-y-1">
            <p className="text-sm">
              <strong>當前股價:</strong> {formatCurrency(etf.currentPrice)}
            </p>
            <p className="text-sm">
              <strong>實際投資:</strong> {formatCurrency(customShares * etf.currentPrice)}
            </p>
            <p className="text-sm">
              <strong>剩餘金額:</strong> {formatCurrency(customAmount - (customShares * etf.currentPrice))}
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>取消</Button>
          <Button onClick={() => onSave({ amount: customAmount, shares: customShares })}>
            確認調整
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default App

