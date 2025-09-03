import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor with enhanced logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Enhanced response interceptor with fallback handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    const { response, request, message } = error
    
    if (response) {
      console.error(`❌ API Error [${response.status}]:`, {
        url: response.config?.url,
        status: response.status,
        message: response.data?.message || response.statusText
      })
      
      // Handle specific error cases
      if (response.status === 429) {
        console.warn('⚠️ Rate limit exceeded - using fallback data')
      } else if (response.status >= 500) {
        console.warn('⚠️ Server error - using fallback data')
      } else if (response.status === 401) {
        console.warn('🔒 Unauthorized access')
        // window.location.href = '/login' // Uncomment if authentication is needed
      }
    } else if (request) {
      console.error('❌ Network Error:', {
        message: 'No response received from server',
        timeout: error.code === 'ECONNABORTED'
      })
    } else {
      console.error('❌ Request Setup Error:', message)
    }
    
    return Promise.reject(error)
  }
)

// Enhanced API methods with better error handling
export const tradingAPI = {
  getSignal: (symbol) => api.get(`/api/trading/signals/${symbol}`),
  getSignals: (symbols) => api.get(`/api/trading/signals?symbols=${symbols.join(',')}`),
  backtest: (data) => api.post('/api/trading/backtest', data),
  getPrediction: (symbol, modelType = 'linear_regression') => 
    api.get(`/api/trading/predictions/${symbol}?model_type=${modelType}`),
  getStrategies: () => api.get('/api/trading/strategies'),
  executeOrder: (orderData) => api.post('/api/trading/execute', orderData),
}

export const portfolioAPI = {
  optimize: (data) => api.post('/api/portfolio/optimize', data),
  getNifty50Optimization: (amount = 100000) => 
    api.get(`/api/portfolio/nifty50-optimization?investment_amount=${amount}`),
  getPerformance: (symbols, quantities, costPrices) => 
    api.get(`/api/portfolio/performance?symbols=${symbols.join(',')}&quantities=${quantities.join(',')}&cost_prices=${costPrices.join(',')}`),
  getRecommendations: (symbols) => 
    api.get(`/api/portfolio/recommendations/${symbols.join(',')}`),
  getPortfolio: () => api.get('/api/portfolio'),
  addToPortfolio: (data) => api.post('/api/portfolio/add', data),
  updatePortfolioItem: (id, data) => api.put(`/api/portfolio/${id}`, data),
  removeFromPortfolio: (id) => api.delete(`/api/portfolio/${id}`),
}

export const reportsAPI = {
  getNews: (symbol) => api.get(`/api/reports/news/${symbol}`),
  getMarketSentiment: (symbols) => 
    api.get(`/api/reports/market-sentiment?symbols=${symbols.join(',')}`),
  getFundamentalAnalysis: (symbol) => 
    api.get(`/api/reports/fundamental-analysis/${symbol}`),
  getSectorAnalysis: () => api.get('/api/reports/sector-analysis'),
  getReports: () => api.get('/api/reports'),
  generateReport: (type, params) => api.post('/api/reports/generate', { type, params }),
}

export const dataAPI = {
  getStock: (symbol, period = '1y', interval = '1d') => 
    api.get(`/api/data/stock/${symbol}?period=${period}&interval=${interval}`),
  getNifty50: (period = '1y') => api.get(`/api/data/nifty50?period=${period}`),
  getRatios: (symbol) => api.get(`/api/data/ratios/${symbol}`),
  compareStocks: (symbols) => api.get(`/api/data/comparison?symbols=${symbols.join(',')}`),
  getMarketOverview: () => api.get('/api/data/market-overview'),
  getWatchlist: () => api.get('/api/data/watchlist'),
  searchStocks: (query) => api.get(`/api/data/search?query=${query}`),
}

// Health check utility
export const healthCheck = async () => {
  try {
    const response = await api.get('/health')
    return { connected: true, message: 'API connection successful', data: response.data }
  } catch (error) {
    return { 
      connected: false, 
      message: error.response?.data?.message || 'API connection failed',
      status: error.response?.status || 'Network Error'
    }
  }
}

// Connection status monitoring
export const checkApiConnection = healthCheck

export default api