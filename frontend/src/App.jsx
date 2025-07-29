import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PieChart, 
  AlertTriangle,
  RefreshCw,
  Target,
  Shield,
  BarChart3,
  Wallet
} from 'lucide-react'
import './App.css'

// API配置
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

function App() {
  const [marketData, setMarketData] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [userFunds, setUserFunds] = useState(100000)
  const [executing, setExecuting] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [userFunds])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // 並行獲取數據
      const [marketResponse, recommendationsResponse] = await Promise.all([
        fetch(`${API_BASE}/api/market-overview`),
        fetch(`${API_BASE}/api/investment-advice?funds=${userFunds}`)
      ])

      if (marketResponse.ok) {
        const market = await marketResponse.json()
        setMarketData(market)
      }

      if (recommendationsResponse.ok) {
        const recs = await recommendationsResponse.json()
        setRecommendations(recs.recommendations || [])
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const executeOneClickInvestment = async () => {
    if (recommendations.length === 0) return
    
    setExecuting(true)
    try {
      const response = await fetch(`${API_BASE}/api/execute-investment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recommendations,
          total_funds: userFunds
        })
      })

      const result = await response.json()
      if (result.success) {
        alert('投資執行成功！這是模擬執行結果。')
      } else {
        alert('投資執行失敗：' + (result.error || '未知錯誤'))
      }
    } catch (error) {
      alert('投資執行失敗，請稍後再試')
    } finally {
      setExecuting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">正在分析市場數據...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">ETF智能投資顧問</h1>
          <p className="text-muted-foreground">專為忙碌投資者設計的智能投資工具</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          重新整理
        </Button>
      </div>

      {/* 市場概況 */}
      <MarketOverview marketData={marketData} />

      {/* 投資建議 */}
      <InvestmentRecommendations 
        recommendations={recommendations}
        userFunds={userFunds}
        setUserFunds={setUserFunds}
        onExecute={executeOneClickInvestment}
        executing={executing}
      />

      {/* 快速統計 */}
      <QuickStats recommendations={recommendations} userFunds={userFunds} />
    </div>
  )
}

// 市場概況組件
function MarketOverview({ marketData }) {
  if (!marketData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>市場概況</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">無法獲取市場數據</p>
        </CardContent>
      </Card>
    )
  }

  const isPositive = marketData.change_percent >= 0
  const trendColor = isPositive ? 'text-green-600' : 'text-red-600'

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          今日市場概況
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold">台股加權指數</h3>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-3xl font-bold">
                {marketData.index_value?.toFixed(2)}
              </span>
              <div className={`flex items-center gap-1 ${trendColor}`}>
                {isPositive ? (
                  <TrendingUp className="h-5 w-5" />
                ) : (
                  <TrendingDown className="h-5 w-5" />
                )}
                <span className="text-lg font-semibold">
                  {isPositive ? '+' : ''}{marketData.change_percent?.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <Badge variant={isPositive ? 'default' : 'destructive'}>
              {marketData.trend_description || (isPositive ? '上漲' : '下跌')}
            </Badge>
            <p className="text-sm text-muted-foreground mt-2">
              波動率: {marketData.volatility ? (marketData.volatility * 100).toFixed(1) : '0.0'}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 投資建議組件
function InvestmentRecommendations({ recommendations, userFunds, setUserFunds, onExecute, executing }) {
  const totalInvestment = recommendations.reduce((sum, rec) => sum + (rec.target_amount || 0), 0)
  const expectedReturn = recommendations.length > 0 
    ? recommendations.reduce((sum, rec) => sum + (rec.expected_return || 0), 0) / recommendations.length 
    : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            今日投資建議
          </div>
          <Button 
            onClick={onExecute}
            disabled={recommendations.length === 0 || executing}
            size="lg"
            className="bg-green-600 hover:bg-green-700"
          >
            {executing ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                執行中...
              </>
            ) : (
              <>
                <DollarSign className="h-4 w-4 mr-2" />
                一鍵投資
              </>
            )}
          </Button>
        </CardTitle>
      </CardHeader>
        <CardContent className="space-y-6">
          {/* 資金設定 */}
          <div className="flex items-center gap-4">
            <Label htmlFor="funds" className="text-sm font-medium">
              可投資金額:
            </Label>
            <Input
              id="funds"
              type="number"
              value={userFunds}
              onChange={(e) => setUserFunds(Number(e.target.value))}
              className="w-40"
              min="0"
              step="10000"
            />
            <span className="text-sm text-muted-foreground">元</span>
          </div>

          {recommendations.length > 0 ? (
            <>
              {/* 投資建議列表 */}
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  基於當前市場分析，建議投資以下ETF組合：
                </p>
                {recommendations.map((rec, index) => (
                  <RecommendationCard key={index} recommendation={rec} />
                ))}
              </div>

              {/* 投資摘要 */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-semibold text-green-800 mb-3">投資摘要</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-green-600">總投資金額</p>
                    <p className="font-bold text-green-800">
                      ${totalInvestment.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-green-600">預期年化報酬</p>
                    <p className="font-bold text-green-800">
                      {(expectedReturn * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-green-600">風險分散度</p>
                    <p className="font-bold text-green-800">
                      {recommendations.length} 檔ETF
                    </p>
                  </div>
                  <div>
                    <p className="text-green-600">剩餘現金</p>
                    <p className="font-bold text-green-800">
                      ${(userFunds - totalInvestment).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                當前市場條件下暫無推薦投資，建議等待更好的投資時機，或考慮增加現金部位。
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    )
  }

// 單個投資建議卡片
function RecommendationCard({ recommendation }) {
  const riskColors = {
    '低': 'bg-green-100 text-green-800',
    '中': 'bg-yellow-100 text-yellow-800',
    '高': 'bg-red-100 text-red-800'
  }

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-lg">
            {recommendation.etf} - {recommendation.etf_name}
          </h4>
          <p className="text-sm text-muted-foreground mt-1">
            {recommendation.reason}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold">
            ${recommendation.target_amount?.toLocaleString()}
          </p>
          <p className="text-sm text-muted-foreground">
            {recommendation.shares?.toLocaleString()} 股
          </p>
        </div>
      </div>
      
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <span>預期報酬: {(recommendation.expected_return * 100).toFixed(1)}%</span>
          <Badge 
            variant="secondary" 
            className={riskColors[recommendation.risk_level] || 'bg-gray-100 text-gray-800'}
          >
            風險: {recommendation.risk_level}
          </Badge>
        </div>
        <div className="text-muted-foreground">
          評分: {recommendation.score?.toFixed(0)}/100
        </div>
      </div>
    </div>
  )
}

// 快速統計組件
function QuickStats({ recommendations, userFunds }) {
  const totalInvestment = recommendations.reduce((sum, rec) => sum + (rec.target_amount || 0), 0)
  const investmentRatio = userFunds > 0 ? (totalInvestment / userFunds) * 100 : 0
  const avgExpectedReturn = recommendations.length > 0 
    ? recommendations.reduce((sum, rec) => sum + (rec.expected_return || 0), 0) / recommendations.length 
    : 0

  const stats = [
    {
      title: '建議投資比例',
      value: `${investmentRatio.toFixed(1)}%`,
      icon: PieChart,
      color: 'text-blue-600'
    },
    {
      title: '預期年化報酬',
      value: `${(avgExpectedReturn * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      title: '投資標的數量',
      value: recommendations.length.toString(),
      icon: Target,
      color: 'text-purple-600'
    },
    {
      title: '風險控制',
      value: '智能分散',
      icon: Shield,
      color: 'text-orange-600'
    }
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <Card key={index}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg bg-gray-100 ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{stat.title}</p>
                <p className="text-lg font-bold">{stat.value}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export default App

