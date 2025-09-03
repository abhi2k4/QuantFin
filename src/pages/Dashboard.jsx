import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, BarChart3, Activity, Wifi, WifiOff, RefreshCw, Eye, Calendar, Clock, AlertCircle, DollarSign } from 'lucide-react'
import { api, dataAPI, healthCheck } from '../services/api'
import StockChart from '../components/StockChart'
import LoadingSpinner from '../components/LoadingSpinner'
import MetricCard from '../components/MetricCard'

const Dashboard = () => {
  const [connectionStatus, setConnectionStatus] = useState({ connected: false, checking: true })
  const [selectedPeriod, setSelectedPeriod] = useState('6mo')
  const [selectedStock, setSelectedStock] = useState('RELIANCE.NS')

  // Check API connection on component mount
  useEffect(() => {
    const checkConnection = async () => {
      const status = await healthCheck()
      setConnectionStatus({ ...status, checking: false })
    }
    checkConnection()
  }, [])

  const { data: marketData, isLoading: marketLoading, error: marketError, refetch: refetchMarket } = useQuery({
    queryKey: ['market-overview'],
    queryFn: () => api.get('/api/data/market-overview'),
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: 2,
    retryDelay: 1000,
  })

  const { data: sentimentData, isLoading: sentimentLoading, refetch: refetchSentiment } = useQuery({
    queryKey: ['market-sentiment'],
    queryFn: () => api.get('/api/reports/market-sentiment'),
    refetchInterval: 60000, // Refresh every minute
    retry: 2,
  })

  const { data: signalsData, isLoading: signalsLoading, refetch: refetchSignals } = useQuery({
    queryKey: ['trading-signals'],
    queryFn: () => api.get('/api/trading/signals'),
    refetchInterval: 30000,
    retry: 2,
  })

  const { data: watchlistData, isLoading: watchlistLoading, refetch: refetchWatchlist } = useQuery({
    queryKey: ['watchlist'],
    queryFn: () => dataAPI.getWatchlist(),
    retry: 2,
    staleTime: 2 * 60 * 1000,
  })

  const handleRefreshData = async () => {
    await Promise.all([refetchMarket(), refetchSentiment(), refetchSignals(), refetchWatchlist()])
    const status = await healthCheck()
    setConnectionStatus({ ...status, checking: false })
  }

  if (marketLoading || sentimentLoading || signalsLoading) {
    return <LoadingSpinner message="Loading dashboard..." />
  }

  const marketOverview = marketData?.data?.market_overview || {}
  const niftyData = marketOverview['^NSEI'] || {}
  const sensexData = marketOverview['^BSESN'] || {}
  const sentiment = sentimentData?.data || {}
  const signals = signalsData?.data?.signals || []
  const watchlist = watchlistData?.data || []

  // Popular stocks for chart selection
  const popularStocks = [
    { symbol: 'RELIANCE.NS', name: 'Reliance' },
    { symbol: 'TCS.NS', name: 'TCS' },
    { symbol: 'INFY.NS', name: 'Infosys' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank' },
    { symbol: 'HINDUNILVR.NS', name: 'HUL' }
  ]

  const periodOptions = [
    { value: '1mo', label: '1M' },
    { value: '3mo', label: '3M' },
    { value: '6mo', label: '6M' },
    { value: '1y', label: '1Y' },
    { value: '2y', label: '2Y' }
  ]

  return (
    <div className="space-y-6">
      {/* Enhanced Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Real-time market insights and portfolio overview</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${
            connectionStatus.checking 
              ? 'border-yellow-500/30 bg-yellow-500/10'
              : connectionStatus.connected 
                ? 'border-green-500/30 bg-green-500/10' 
                : 'border-red-500/30 bg-red-500/10'
          }`}>
            {connectionStatus.checking ? (
              <Clock className="h-4 w-4 text-yellow-400" />
            ) : connectionStatus.connected ? (
              <Wifi className="h-4 w-4 text-green-400" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-400" />
            )}
            <span className={`text-sm font-medium ${
              connectionStatus.checking 
                ? 'text-yellow-400'
                : connectionStatus.connected 
                  ? 'text-green-400' 
                  : 'text-red-400'
            }`}>
              {connectionStatus.checking 
                ? 'Checking...'
                : connectionStatus.connected 
                  ? 'Connected' 
                  : 'Offline'
              }
            </span>
          </div>

          <div className="bg-gray-800/50 px-4 py-2 rounded-lg border border-gray-700/50 backdrop-blur-sm">
            <span className="text-gray-400 text-sm">Last Updated</span>
            <div className="text-white font-medium">
              {new Date().toLocaleTimeString()}
            </div>
          </div>

          <button
            onClick={handleRefreshData}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            title="Refresh data"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(marketOverview).map(([index, data]) => (
          <div key={index} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">{index === '^NSEI' ? 'Nifty 50' : 'BSE Sensex'}</p>
                <p className="text-2xl font-bold text-white">
                  {data.value?.toLocaleString()}
                </p>
              </div>
              <div className="flex items-center">
                {data.change >= 0 ? (
                  <TrendingUp className="h-8 w-8 text-green-400" />
                ) : (
                  <TrendingDown className="h-8 w-8 text-red-400" />
                )}
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className={`text-sm font-medium ${
                data.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {data.change_percent >= 0 ? '+' : ''}{data.change_percent?.toFixed(2)}%
              </span>
              <span className="text-gray-400 text-sm ml-2">
                ({data.change >= 0 ? '+' : ''}{data.change?.toFixed(2)})
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Market Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            Market Sentiment
          </h3>
          {sentiment.market_sentiment && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Overall Sentiment</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  sentiment.market_sentiment === 'Bullish' ? 'bg-green-600 text-green-100' :
                  sentiment.market_sentiment === 'Bearish' ? 'bg-red-600 text-red-100' :
                  'bg-gray-600 text-gray-100'
                }`}>
                  {sentiment.market_sentiment}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Sentiment Score</span>
                <span className="text-white font-medium">
                  {(sentiment.average_sentiment * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Articles Analyzed</span>
                <span className="text-white font-medium">{sentiment.total_articles}</span>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="text-center">
                  <div className="text-green-400 text-lg font-bold">{sentiment.positive_percentage}%</div>
                  <div className="text-gray-400 text-xs">Positive</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-lg font-bold">{sentiment.neutral_count || 0}</div>
                  <div className="text-gray-400 text-xs">Neutral</div>
                </div>
                <div className="text-center">
                  <div className="text-red-400 text-lg font-bold">{sentiment.negative_percentage}%</div>
                  <div className="text-gray-400 text-xs">Negative</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recent Trading Signals */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Recent Trading Signals
          </h3>
          <div className="space-y-3">
            {signals.slice(0, 5).map((signal, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                <div>
                  <div className="text-white font-medium">{signal.symbol}</div>
                  <div className="text-gray-400 text-sm">₹{signal.price?.toFixed(2)}</div>
                </div>
                <div className="text-right">
                  <div className={`px-2 py-1 rounded text-sm font-medium ${
                    signal.signal === 'BUY' ? 'bg-green-600 text-green-100' :
                    signal.signal === 'SELL' ? 'bg-red-600 text-red-100' :
                    'bg-gray-600 text-gray-100'
                  }`}>
                    {signal.signal}
                  </div>
                  <div className="text-gray-400 text-xs mt-1">
                    {(signal.confidence * 100).toFixed(0)}% confidence
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Stock Chart */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Nifty 50 Performance</h3>
        <StockChart symbol="^NSEI" height={400} />
      </div>
    </div>
  )
}

export default Dashboard