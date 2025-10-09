// QuantFin AI - Backend API Service Layer
// Centralized Axios configuration and API endpoint functions

import axios, { AxiosInstance, AxiosError } from 'axios';

// ==================== CONFIGURATION ====================

// Base API URL - Update this to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Auth token - For now using placeholder, replace with real auth later
const getAuthToken = (): string | null => {
  // TODO: Replace with real token from localStorage/context
  return localStorage.getItem('auth_token') || null;
};

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      console.error('Unauthorized access - please log in');
      // TODO: Redirect to login page
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

// ==================== TYPE DEFINITIONS ====================

// Portfolio Types
export interface Position {
  symbol: string;
  quantity: number;
  avg_buy_price: number;
  current_price: number;
  invested: number;
  current_value: number;
  gain_loss: number;
  gain_loss_percent: number;
  daily_change: number;
  daily_change_percent: number;
  allocation_percent: number;
}

export interface PortfolioSummary {
  total_value: number;
  invested_value: number;
  current_holdings_value: number;
  cash_balance: number;
  total_gain_loss: number;
  total_gain_loss_percent: number;
  daily_change: number;
  daily_change_percent: number;
  total_positions: number;
  positions: Position[];
}

export interface PortfolioPerformance {
  dates: string[];
  values: number[];
}

export interface RebalanceRequest {
  strategy: 'LSTM' | 'Linear' | 'Logistic' | 'SVM';
  capital_allocation: number;
}

export interface RebalanceResponse extends PortfolioSummary {
  message?: string;
  execution_time?: number;
}

// Analytics Types
export interface KPIData {
  portfolio_return: number;
  risk_metric: number;
  volatility: number;
  sharpe_ratio: number;
}

export interface ModelPerformance {
  model: string;
  accuracy: number;
  train_accuracy: number;
  mae: number;
  rmse: number;
  r2_score: number;
  training_samples: number;
  status?: string;
}

export interface StockPrediction {
  symbol: string;
  dates: string[];
  actual_prices: number[];
  predicted_prices: {
    LSTM: number[];
    Linear: number[];
    Logistic: number[];
    SVM: number[];
  };
}

export interface Recommendation {
  model: string;
  return: number;
  confidence: number;
  action: 'Buy' | 'Hold' | 'Sell';
  description: string;
}

// Backtest Types
export interface DailyResult {
  date: string;
  portfolio_value: number;
  daily_return: number;
  cash: number;
}

export interface BacktestMetrics {
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_return: number;
  final_value: number;
  num_trades: number;
}

export interface BacktestResponse {
  configuration: {
    symbols: string[];
    strategy: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    rebalance_freq: number;
  };
  daily_results: DailyResult[];
  cumulative_returns: number[];
  drawdowns: number[];
  metrics: BacktestMetrics;
  warnings: string[];
}

export interface BacktestRequest {
  symbols: string[];
  start_date: string;
  end_date: string;
  strategy?: string;
  rebalance_freq?: number;
  initial_capital?: number;
  transaction_cost?: number;
}

// ==================== PORTFOLIO API ENDPOINTS ====================

/**
 * Get portfolio summary with current positions and total value
 * GET /api/portfolio/summary
 */
export const getPortfolioSummary = async (): Promise<PortfolioSummary> => {
  try {
    const response = await apiClient.get<PortfolioSummary>('/portfolio/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio summary:', error);
    throw error;
  }
};

/**
 * Get historical portfolio performance data
 * GET /api/portfolio/performance?timeframe=1M
 */
export const getPortfolioPerformance = async (
  timeframe: '1M' | '3M' | '6M' | '1Y' = '3M'
): Promise<PortfolioPerformance> => {
  try {
    const response = await apiClient.get<PortfolioPerformance>('/portfolio/performance', {
      params: { timeframe }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio performance:', error);
    throw error;
  }
};

/**
 * Rebalance portfolio using selected ML model strategy
 * POST /api/portfolio/rebalance
 */
export const rebalancePortfolio = async (
  request: RebalanceRequest
): Promise<RebalanceResponse> => {
  try {
    const response = await apiClient.post<RebalanceResponse>('/portfolio/rebalance', request);
    return response.data;
  } catch (error) {
    console.error('Error rebalancing portfolio:', error);
    throw error;
  }
};

// ==================== ANALYTICS API ENDPOINTS ====================

/**
 * Get KPI metrics (return, risk, volatility, sharpe ratio)
 * GET /api/analytics/kpis
 */
export const getAnalyticsKPIs = async (): Promise<KPIData> => {
  try {
    const response = await apiClient.get<KPIData>('/analytics/kpis');
    return response.data;
  } catch (error) {
    console.error('Error fetching KPIs:', error);
    throw error;
  }
};

/**
 * Get ML model performance metrics
 * GET /api/analytics/models?train=false
 */
export const getModelPerformance = async (train: boolean = false): Promise<ModelPerformance[]> => {
  try {
    const response = await apiClient.get<ModelPerformance[]>('/analytics/models', {
      params: { train }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching model performance:', error);
    throw error;
  }
};

/**
 * Get stock prediction data (actual vs predicted prices)
 * GET /api/analytics/stock/:symbol?timeframe=3M
 */
export const getStockPrediction = async (
  symbol: string,
  timeframe: '1M' | '3M' | '6M' | '1Y' = '3M'
): Promise<StockPrediction> => {
  try {
    const response = await apiClient.get<StockPrediction>(`/analytics/stock/${symbol}`, {
      params: { timeframe }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stock prediction:', error);
    throw error;
  }
};

/**
 * Get model recommendations (buy/hold/sell signals)
 * GET /api/analytics/recommendations
 */
export const getRecommendations = async (): Promise<Recommendation[]> => {
  try {
    const response = await apiClient.get<Recommendation[]>('/analytics/recommendations');
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

/**
 * Get filtered analytics data based on timeframe and model
 * GET /api/analytics/filtered?timeframe=3M&model=LSTM
 */
export const getFilteredAnalytics = async (
  timeframe: '1M' | '3M' | '6M' | '1Y',
  model?: string
): Promise<{
  kpis: KPIData;
  models: ModelPerformance[];
  recommendations: Recommendation[];
}> => {
  try {
    const response = await apiClient.get('/analytics/filtered', {
      params: { timeframe, model }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching filtered analytics:', error);
    throw error;
  }
};

// ==================== UTILITY FUNCTIONS ====================

/**
 * Check if backend API is reachable
 */
export const checkAPIHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

/**
 * Handle API errors and return user-friendly messages
 */
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      return error.response.data?.message || `Error: ${error.response.status}`;
    } else if (error.request) {
      return 'No response from server. Please check your connection.';
    }
  }
  return 'An unexpected error occurred.';
};

/**
 * Get candlestick/OHLCV data for a stock
 * GET /api/analytics/candlestick/:symbol?days=90
 */
export const getCandlestickData = async (
  symbol: string,
  days: number = 90
): Promise<{ symbol: string; data: Array<{
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}> }> => {
  try {
    const response = await apiClient.get(`/analytics/candlestick/${symbol}`, {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching candlestick data:', error);
    throw error;
  }
};

/**
 * Run a backtest simulation
 * POST /api/backtest/run
 */
export const runBacktest = async (
  request: BacktestRequest
): Promise<BacktestResponse> => {
  try {
    const response = await apiClient.post<BacktestResponse>('/backtest/run', request);
    return response.data;
  } catch (error) {
    console.error('Error running backtest:', error);
    throw error;
  }
};

/**
 * Get backtesting results (legacy - use runBacktest instead)
 * GET /api/backtest/results?strategy=LSTM&timeframe=1Y
 */
export const getBacktestResults = async (
  strategy: string = 'LSTM',
  timeframe: string = '1Y'
): Promise<any> => {
  try {
    const response = await apiClient.get('/backtest/results', {
      params: { strategy, timeframe }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching backtest results:', error);
    throw error;
  }
};

export default apiClient;
