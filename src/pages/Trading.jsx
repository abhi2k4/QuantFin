import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { TrendingUp, Play, BarChart3, Target } from 'lucide-react'
import { api } from '../services/api'

import StockChart from '../components/StockChart'
import LoadingSpinner from '../components/LoadingSpinner'

const Trading = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NS')
  const [selectedStrategy, setSelectedStrategy] = useState('EMA_Crossover')
  const [backtestResults, setBacktestResults] = useState(null)

  // Get available strategies first
  const { data: strategiesData } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => api.get('/api/trading/strategies'),
  })

  // Only fetch other data if strategies are available
  const strategiesAvailable = strategiesData?.data?.strategies?.length > 0

  const { data: stockData, isLoading: stockLoading } = useQuery({
    queryKey: ['stock-data', selectedSymbol],
    queryFn: () => api.get(`/api/data/stock/${selectedSymbol}?period=1y`),
    enabled: strategiesAvailable,
    retry: 1,
    onError: (error) => console.error('Stock data error:', error)
  })

  const { data: signalData, isLoading: signalLoading } = useQuery({
    queryKey: ['trading-signal', selectedSymbol],
    queryFn: () => api.get(`/api/trading/signals/${selectedSymbol}`),
    refetchInterval: 30000,
    enabled: strategiesAvailable,
    retry: 1,
    onError: (error) => console.error('Signal data error:', error)
  })

  // Add query for multiple signals - but make it optional
  const { data: signalsData, isLoading: signalsLoading } = useQuery({
    queryKey: ['trading-signals'],
    queryFn: () => api.get('/api/trading/signals'),
    refetchInterval: 30000,
    enabled: strategiesAvailable,
    retry: 1,
    onError: (error) => console.error('Multiple signals error:', error)
  })

  const backtestMutation = useMutation({
    mutationFn: (data) => api.post('/api/trading/backtest', data),
    onSuccess: (data) => setBacktestResults(data.data),
    onError: (error) => console.error('Backtest error:', error)
  })

  const handleBacktest = () => {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setFullYear(endDate.getFullYear() - 2)

    backtestMutation.mutate({
      strategy: selectedStrategy,
      symbols: [selectedSymbol],
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      initial_capital: 100000,
    })
  }

  const popularStocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'
  ]

  const strategies = strategiesData?.data?.strategies || []
  const signals = signalsData?.data?.signals || []

  // Show loading for essential data
  if (!strategiesAvailable && !strategiesData) {
    return <LoadingSpinner />
  }

  const signal = signalData?.data || {}

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Algorithmic Trading</h1>
        <div className="flex items-center space-x-4">
          <div className="bg-gray-800 px-4 py-2 rounded-lg">
            <span className="text-gray-400 text-sm">Active Strategies</span>
            <div className="text-white font-medium">{strategies.length}</div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Stock Selection</h3>
          <div className="space-y-3">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              {popularStocks.map(symbol => (
                <option key={symbol} value={symbol}>
                  {symbol.replace('.NS', '')}
                </option>
              ))}
            </select>
            {signal.signal && (
              <div className="mt-4 p-4 bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Current Signal</span>
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    signal.signal === 'BUY' ? 'bg-green-600 text-green-100' :
                    signal.signal === 'SELL' ? 'bg-red-600 text-red-100' :
                    'bg-gray-600 text-gray-100'
                  }`}>
                    {signal.signal}
                  </span>
                </div>
                {signal.confidence && (
                  <div className="mt-2 text-sm text-gray-300">
                    Confidence: {(signal.confidence * 100).toFixed(0)}%
                  </div>
                )}
                {signal.price && (
                  <div className="text-sm text-gray-300">
                    Price: ₹{signal.price.toFixed(2)}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Strategy Selection</h3>
          <div className="space-y-3">
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              {strategies.map(strategy => (
                <option key={strategy.name} value={strategy.name}>
                  {strategy.name.replace('_', ' ')}
                </option>
              ))}
            </select>
            <button
              onClick={handleBacktest}
              disabled={backtestMutation.isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
            >
              <Play className="h-4 w-4" />
              <span>{backtestMutation.isLoading ? 'Running...' : 'Run Backtest'}</span>
            </button>
          </div>
        </div>

        {backtestResults && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Backtest Results</h3>
            <div className="space-y-3">
              {backtestResults.results?.map((result, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Return</span>
                    <span className={`font-medium ${
                      result.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {result.total_return?.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Trades</span>
                    <span className="text-white">{result.trade_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Final Value</span>
                    <span className="text-white">₹{result.final_value?.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Stock Chart - Only show if data is available */}
      {stockData && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">
              {selectedSymbol.replace('.NS', '')} Price Chart
            </h3>
            <div className="flex items-center space-x-2 text-gray-400">
              <BarChart3 className="h-4 w-4" />
              <span>Technical Analysis</span>
            </div>
          </div>
          <StockChart symbol={selectedSymbol} height={500} />
        </div>
      )}

      {/* Trading Signals Table */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
          <Target className="h-5 w-5 mr-2" />
          Live Trading Signals
        </h3>
        {signalsLoading ? (
          <div className="text-center py-8">
            <LoadingSpinner />
            <p className="text-gray-400 mt-2">Loading trading signals...</p>
          </div>
        ) : signals.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-400 font-medium py-3">Symbol</th>
                  <th className="text-left text-gray-400 font-medium py-3">Signal</th>
                  <th className="text-left text-gray-400 font-medium py-3">Price</th>
                  <th className="text-left text-gray-400 font-medium py-3">Confidence</th>
                  <th className="text-left text-gray-400 font-medium py-3">Strategy</th>
                </tr>
              </thead>
              <tbody>
                {signals.map((signal, index) => (
                  <tr key={index} className="border-b border-gray-700/50">
                    <td className="py-3 text-white font-medium">
                      {signal.symbol?.replace('.NS', '')}
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-sm font-medium ${
                        signal.signal === 'BUY' ? 'bg-green-600 text-green-100' :
                        signal.signal === 'SELL' ? 'bg-red-600 text-red-100' :
                        'bg-gray-600 text-gray-100'
                      }`}>
                        {signal.signal}
                      </span>
                    </td>
                    <td className="py-3 text-white">₹{signal.price?.toFixed(2)}</td>
                    <td className="py-3 text-white">{signal.confidence ? (signal.confidence * 100).toFixed(0) : 'N/A'}%</td>
                    <td className="py-3 text-gray-300">{signal.strategy}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-400">No trading signals available</p>
            <p className="text-gray-500 text-sm mt-2">
              Backend API endpoints may be loading or experiencing issues
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Trading