import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { PieChart, DollarSign, TrendingUp, Briefcase, Target } from 'lucide-react'
import { api } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Portfolio = () => {
  const [investmentAmount, setInvestmentAmount] = useState(100000)
  const [optimizedPortfolio, setOptimizedPortfolio] = useState(null)

  const optimizeMutation = useMutation({
    mutationFn: (data) => api.post('/api/portfolio/optimize', data),
    onSuccess: (data) => setOptimizedPortfolio(data.data),
  })

  const { data: nifty50Optimization, isLoading: optimizationLoading } = useQuery({
    queryKey: ['nifty50-optimization', investmentAmount],
    queryFn: () => api.get(`/api/portfolio/nifty50-optimization?investment_amount=${investmentAmount}`),
    enabled: !!investmentAmount,
  })

  const handleOptimize = () => {
    const topStocks = [
      'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
      'KOTAKBANK.NS', 'BAJFINANCE.NS', 'AXISBANK.NS', 'HCLTECH.NS', 'WIPRO.NS'
    ]

    optimizeMutation.mutate({
      symbols: topStocks,
      investment_amount: investmentAmount,
      risk_tolerance: 0.6,
      time_horizon: 252 * 5
    })
  }

  if (optimizationLoading) {
    return <LoadingSpinner />
  }

  const portfolio = optimizedPortfolio || nifty50Optimization?.data

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Portfolio Management</h1>
        <div className="flex items-center space-x-4">
          <div className="bg-gray-800 px-4 py-2 rounded-lg">
            <span className="text-gray-400 text-sm">Investment Amount</span>
            <div className="text-white font-medium">₹{investmentAmount.toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* Portfolio Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Target className="h-5 w-5 mr-2" />
            Portfolio Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-400 text-sm mb-2">Investment Amount (₹)</label>
              <input
                type="number"
                value={investmentAmount}
                onChange={(e) => setInvestmentAmount(Number(e.target.value))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                min="10000"
                step="10000"
              />
            </div>
            <button
              onClick={handleOptimize}
              disabled={optimizeMutation.isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
            >
              <Briefcase className="h-4 w-4" />
              <span>Optimize Portfolio</span>
            </button>
          </div>
        </div>

        {/* Portfolio Summary */}
        {portfolio && (
          <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Portfolio Summary
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-700 p-4 rounded-lg">
                <div className="text-gray-400 text-sm">Total Investment</div>
                <div className="text-xl font-bold text-white">
                  ₹{portfolio.investment_amount?.toLocaleString()}
                </div>
              </div>
              <div className="bg-gray-700 p-4 rounded-lg">
                <div className="text-gray-400 text-sm">Allocated</div>
                <div className="text-xl font-bold text-white">
                  ₹{portfolio.total_allocated?.toLocaleString()}
                </div>
              </div>
              <div className="bg-gray-700 p-4 rounded-lg">
                <div className="text-gray-400 text-sm">Predicted Value (5Y)</div>
                <div className="text-xl font-bold text-green-400">
                  ₹{portfolio.predicted_value_5y?.toLocaleString()}
                </div>
              </div>
              <div className="bg-gray-700 p-4 rounded-lg">
                <div className="text-gray-400 text-sm">Expected Return</div>
                <div className="text-xl font-bold text-green-400">
                  {portfolio.expected_return_5y?.toFixed(2)}%
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Holdings Table */}
      {portfolio?.holdings && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <DollarSign className="h-5 w-5 mr-2" />
            Recommended Holdings
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-400 font-medium py-3">Symbol</th>
                  <th className="text-right text-gray-400 font-medium py-3">Weight %</th>
                  <th className="text-right text-gray-400 font-medium py-3">Allocation</th>
                  <th className="text-right text-gray-400 font-medium py-3">Current Price</th>
                  <th className="text-right text-gray-400 font-medium py-3">Quantity</th>
                  <th className="text-right text-gray-400 font-medium py-3">Predicted Price</th>
                  <th className="text-right text-gray-400 font-medium py-3">Expected Return</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.holdings.map((holding, index) => (
                  <tr key={index} className="border-b border-gray-700/50">
                    <td className="py-3 text-white font-medium">
                      {holding.index?.replace('.NS', '') || holding.symbol?.replace('.NS', '')}
                    </td>
                    <td className="py-3 text-right text-white">
                      {((holding.weight || holding['Weight']) * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 text-right text-white">
                      ₹{(holding.allocation || holding['Allocation (₹)']).toLocaleString()}
                    </td>
                    <td className="py-3 text-right text-white">
                      ₹{(holding.current_price || holding['Current Price']).toFixed(2)}
                    </td>
                    <td className="py-3 text-right text-white">
                      {holding.quantity || holding['Quantity']}
                    </td>
                    <td className="py-3 text-right text-green-400">
                      ₹{(holding.predicted_price || holding['Predicted Price']).toFixed(2)}
                    </td>
                    <td className="py-3 text-right text-green-400">
                      {((holding.expected_return || holding['Expected Return']) * 100).toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Portfolio Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Portfolio Allocation</h3>
          {portfolio?.holdings && (
            <div className="space-y-3">
              {portfolio.holdings.slice(0, 8).map((holding, index) => {
                const weight = (holding.weight || holding['Weight']) * 100
                return (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="text-white font-medium">
                        {holding.index?.replace('.NS', '') || holding.symbol?.replace('.NS', '')}
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-32 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(weight, 100)}%` }}
                        />
                      </div>
                      <span className="text-white text-sm font-medium min-w-[3rem] text-right">
                        {weight.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Performance Projection</h3>
          {portfolio && (
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-700 rounded-lg">
                <span className="text-gray-400">Current Portfolio Value</span>
                <span className="text-white font-bold text-xl">
                  ₹{portfolio.total_allocated?.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center p-4 bg-green-900/20 border border-green-700 rounded-lg">
                <span className="text-gray-400">Projected Value (5Y)</span>
                <span className="text-green-400 font-bold text-xl">
                  ₹{portfolio.predicted_value_5y?.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
                <span className="text-gray-400">Expected CAGR</span>
                <span className="text-blue-400 font-bold text-xl">
                  {(portfolio.expected_return_5y / 5).toFixed(2)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Portfolio