import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Plot from 'react-plotly.js'
import { api } from '../services/api'
import { BarChart3, TrendingUp, AlertCircle, Maximize2 } from 'lucide-react'
import LoadingSpinner from './LoadingSpinner'

const StockChart = ({ symbol, height = 400, period = "6mo" }) => {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [chartType, setChartType] = useState('candlestick') // candlestick, line, volume

  const { data, isLoading, error } = useQuery({
    queryKey: ['stock-chart', symbol, period],
    queryFn: () => api.get(`/api/data/stock/${symbol}?period=${period}&interval=1d`),
    retry: 2,
    retryDelay: 1000
  })

  if (isLoading) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700/50 backdrop-blur-sm" style={{ height }}>
        <LoadingSpinner message="Loading chart data..." fullScreen={false} variant="trading" />
      </div>
    )
  }

  if (error || !data?.data?.data) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700/50 backdrop-blur-sm flex items-center justify-center" style={{ height }}>
        <div className="text-center space-y-4">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto" />
          <div>
            <h3 className="text-white font-medium">Chart Unavailable</h3>
            <p className="text-gray-400 text-sm mt-1">
              {error?.response?.status === 500 ? 'Using fallback data - Chart temporarily unavailable' : 'Error loading chart data'}
            </p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  const stockData = data.data.data
  
  if (!stockData.length) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700/50 backdrop-blur-sm flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <div className="text-gray-400">No data available for {symbol}</div>
        </div>
      </div>
    )
  }

  // Prepare data
  const dates = stockData.map(d => d.Date)
  const opens = stockData.map(d => d.Open)
  const highs = stockData.map(d => d.High)
  const lows = stockData.map(d => d.Low)
  const closes = stockData.map(d => d.Close)
  const volumes = stockData.map(d => d.Volume)

  // Technical indicators
  const ema20 = stockData.map(d => d.EMA_20).filter(v => v !== undefined && !isNaN(v))
  const ema50 = stockData.map(d => d.EMA_50).filter(v => v !== undefined && !isNaN(v))
  const rsi = stockData.map(d => d.RSI).filter(v => v !== undefined && !isNaN(v))

  const getTraces = () => {
    const traces = []

    if (chartType === 'candlestick') {
      traces.push({
        type: 'candlestick',
        x: dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        name: symbol.replace('.NS', ''),
        increasing: { fillcolor: '#10b981', line: { color: '#10b981' } },
        decreasing: { fillcolor: '#f87171', line: { color: '#f87171' } }
      })
    } else if (chartType === 'line') {
      traces.push({
        type: 'scatter',
        mode: 'lines',
        x: dates,
        y: closes,
        name: 'Close Price',
        line: { color: '#3b82f6', width: 2 }
      })
    }

    // Add EMA lines
    if (ema20.length > 0 && chartType !== 'volume') {
      traces.push({
        type: 'scatter',
        mode: 'lines',
        x: dates.slice(-ema20.length),
        y: ema20,
        name: 'EMA 20',
        line: { color: '#8b5cf6', width: 1.5, dash: 'dot' }
      })
    }

    if (ema50.length > 0 && chartType !== 'volume') {
      traces.push({
        type: 'scatter',
        mode: 'lines',
        x: dates.slice(-ema50.length),
        y: ema50,
        name: 'EMA 50',
        line: { color: '#f59e0b', width: 1.5, dash: 'dash' }
      })
    }

    // Volume chart
    if (chartType === 'volume') {
      traces.push({
        type: 'bar',
        x: dates,
        y: volumes,
        name: 'Volume',
        marker: { color: volumes.map((_, i) => closes[i] > opens[i] ? '#10b981' : '#f87171') }
      })
    }

    return traces
  }

  const currentPrice = closes[closes.length - 1]
  const previousPrice = closes[closes.length - 2]
  const priceChange = currentPrice - previousPrice
  const priceChangePercent = (priceChange / previousPrice) * 100

  const layout = {
    height: isFullscreen ? window.innerHeight - 100 : height,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(17, 24, 39, 0.8)',
    font: { color: '#e5e7eb', family: 'Inter, sans-serif' },
    xaxis: {
      gridcolor: '#374151',
      gridwidth: 0.5,
      showgrid: true,
      zeroline: false,
      color: '#9ca3af',
      showspikes: true,
      spikecolor: '#6b7280',
      spikethickness: 1
    },
    yaxis: {
      gridcolor: '#374151',
      gridwidth: 0.5,
      showgrid: true,
      zeroline: false,
      color: '#9ca3af',
      title: { 
        text: chartType === 'volume' ? 'Volume' : 'Price (₹)', 
        font: { color: '#9ca3af', size: 12 } 
      },
      showspikes: true,
      spikecolor: '#6b7280',
      spikethickness: 1
    },
    margin: { l: 60, r: 40, t: 60, b: 60 },
    showlegend: true,
    legend: {
      x: 0,
      y: 1,
      bgcolor: 'rgba(17, 24, 39, 0.8)',
      bordercolor: '#374151',
      borderwidth: 1,
      font: { color: '#e5e7eb', size: 11 }
    },
    hovermode: 'x unified',
    dragmode: 'zoom'
  }

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true,
    toImageButtonOptions: {
      format: 'png',
      filename: `${symbol}_chart`,
      height: 600,
      width: 1000,
      scale: 1
    }
  }

  return (
    <div className={`bg-gray-800/50 rounded-xl border border-gray-700/50 backdrop-blur-sm overflow-hidden ${isFullscreen ? 'fixed inset-4 z-50' : ''}`}>
      {/* Chart Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700/50">
        <div className="flex items-center space-x-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-blue-400" />
              {symbol.replace('.NS', '')}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xl font-bold text-white">₹{currentPrice?.toFixed(2)}</span>
              <span className={`text-sm font-medium px-2 py-1 rounded ${
                priceChange >= 0 ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'
              }`}>
                {priceChange >= 0 ? '+' : ''}{priceChange?.toFixed(2)} ({priceChangePercent?.toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Chart type selector */}
          <div className="flex rounded-lg overflow-hidden border border-gray-600">
            {[
              { type: 'candlestick', label: 'Candle' },
              { type: 'line', label: 'Line' },
              { type: 'volume', label: 'Volume' }
            ].map(({ type, label }) => (
              <button
                key={type}
                onClick={() => setChartType(type)}
                className={`px-3 py-1 text-xs font-medium transition-colors ${
                  chartType === type 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            <Maximize2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="relative">
        <Plot
          data={getTraces()}
          layout={layout}
          config={config}
          style={{ width: '100%', height: isFullscreen ? window.innerHeight - 160 : height - 80 }}
          useResizeHandler={true}
        />
      </div>

      {/* Chart Footer with indicators */}
      {rsi.length > 0 && chartType !== 'volume' && (
        <div className="p-4 border-t border-gray-700/50">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">RSI (14): </span>
            <span className={`font-medium ${
              rsi[rsi.length - 1] > 70 ? 'text-red-400' : 
              rsi[rsi.length - 1] < 30 ? 'text-green-400' : 'text-gray-300'
            }`}>
              {rsi[rsi.length - 1]?.toFixed(2)}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default StockChart