import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, Newspaper, BarChart3, TrendingUp, AlertCircle } from 'lucide-react'
import { api } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Reports = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('TCS.NS')

  const { data: newsData, isLoading: newsLoading } = useQuery({
    queryKey: ['stock-news', selectedSymbol],
    queryFn: () => api.get(`/api/reports/news/${selectedSymbol}`),
  })

  const { data: fundamentalData, isLoading: fundamentalLoading } = useQuery({
    queryKey: ['fundamental-analysis', selectedSymbol],
    queryFn: () => api.get(`/api/reports/fundamental-analysis/${selectedSymbol}`),
  })

  const { data: sectorData } = useQuery({
    queryKey: ['sector-analysis'],
    queryFn: () => api.get('/api/reports/sector-analysis'),
  })

  const popularStocks = [
    'TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'
  ]

  if (newsLoading || fundamentalLoading) {
    return <LoadingSpinner />
  }

  const news = newsData?.data?.news || []
  const fundamental = fundamentalData?.data || {}
  const sectors = sectorData?.data?.sector_analysis || {}

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Financial Reports & Analysis</h1>
        <div className="flex items-center space-x-4">
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white"
          >
            {popularStocks.map(symbol => (
              <option key={symbol} value={symbol}>
                {symbol.replace('.NS', '')}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Fundamental Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Fundamental Analysis - {selectedSymbol.replace('.NS', '')}
          </h3>
          {fundamental.current_price && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Current Price</div>
                  <div className="text-xl font-bold text-white">
                    ₹{fundamental.current_price.toFixed(2)}
                  </div>
                </div>
                <div className="bg-gray-700 p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Volatility</div>
                  <div className="text-xl font-bold text-white">
                    {fundamental.volatility?.toFixed(2)}%
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="text-lg font-medium text-white">Financial Ratios</h4>
                {fundamental.financial_ratios && Object.entries(fundamental.financial_ratios).map(([key, value]) => (
                  value !== null && value !== undefined && (
                    <div key={key} className="flex justify-between items-center p-2 bg-gray-700 rounded">
                      <span className="text-gray-400 capitalize">
                        {key.replace(/_/g, ' ').replace(/ratio|yield/i, '')}
                      </span>
                      <span className="text-white font-medium">
                        {typeof value === 'number' ? 
                          (key.includes('cap') ? `₹${(value / 1e7).toFixed(0)}Cr` : value.toFixed(2)) : 
                          value
                        }
                      </span>
                    </div>
                  )
                ))}
              </div>

              <div className="space-y-2">
                <h4 className="text-lg font-medium text-white">Price Trends</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-700 p-3 rounded-lg">
                    <div className="text-gray-400 text-sm">30-Day Change</div>
                    <div className={`text-lg font-bold ${
                      fundamental.price_trends?.['30_day_change'] >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {fundamental.price_trends?.['30_day_change']?.toFixed(2)}%
                    </div>
                  </div>
                  <div className="bg-gray-700 p-3 rounded-lg">
                    <div className="text-gray-400 text-sm">90-Day Change</div>
                    <div className={`text-lg font-bold ${
                      fundamental.price_trends?.['90_day_change'] >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {fundamental.price_trends?.['90_day_change']?.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* News Analysis */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <Newspaper className="h-5 w-5 mr-2" />
            News Sentiment Analysis
          </h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {news.slice(0, 8).map((article, index) => (
              <div key={index} className="border border-gray-700 rounded-lg p-4">
                <h4 className="text-white font-medium mb-2 line-clamp-2">
                  {article.title}
                </h4>
                <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                  {article.summary}
                </p>
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    article.sentiment_label === 'Positive' ? 'bg-green-600 text-green-100' :
                    article.sentiment_label === 'Negative' ? 'bg-red-600 text-red-100' :
                    'bg-gray-600 text-gray-100'
                  }`}>
                    {article.sentiment_label}
                  </span>
                  <span className="text-gray-400 text-xs">
                    Score: {(article.sentiment_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sector Analysis */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Sector Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(sectors).map(([sector, stocks]) => (
            <div key={sector} className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-lg font-medium text-white mb-3">{sector}</h4>
              <div className="space-y-2">
                {stocks.map((stock, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-300">{stock.symbol?.replace('.NS', '')}</span>
                    <div className="text-right">
                      <div className="text-white font-medium">
                        ₹{stock.current_price?.toFixed(2)}
                      </div>
                      <div className="text-gray-400 text-xs">
                        PE: {stock.pe_ratio?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Reports