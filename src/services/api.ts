// QuantFin AI - Backend API Service Layer
// Centralized Axios configuration and API endpoint functions

import axios, { AxiosInstance, AxiosError } from 'axios';

/** Returns true for requests that were intentionally aborted (cleanup on unmount / timeframe change). */
const isCanceledError = (error: unknown): boolean => {
  if (axios.isCancel(error)) return true;
  const e = error as { code?: string; name?: string };
  return e?.code === 'ERR_CANCELED' || e?.name === 'CanceledError';
};

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
  timeout: 60000, // Increased to 60 seconds for ML model operations
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
  timeframe: string;
  data: Array<{
    date: string;
    value: number;
  }>;
  metrics: {
    initial_value: number;
    final_value: number;
    total_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
  };
  warnings?: string[];
}

export interface RebalanceRequest {
  strategy: 'LSTM' | 'Linear' | 'Logistic' | 'SVM' | 'ARIMA';
  capital_allocation: number;
}

export interface AllocationRecommendation {
  symbol: string;
  weight_percent: number;
  allocation_amount: number;
  quantity: number;
  buy_price: number;
  predicted_price: number;
  predicted_return: number;
  confidence: number;
  action: string;
}

export interface RebalanceResponse extends PortfolioSummary {
  allocations: AllocationRecommendation[];
  expected_return: number;
  expected_risk: number;
  sharpe_ratio?: number;
  total_recommended_stocks?: number;
  message?: string;
  execution_time?: number;
}

export interface StrategyPerformance {
  dates: string[];
  values: number[];
  total_return: number;
  expected_return?: number;
  expected_risk?: number;
  sharpe_ratio?: number;
  final_value: number;
  top_stocks?: string[];
}

export interface StrategyComparisonResponse {
  timeframe: string;
  initial_capital: number;
  strategies: {
    LSTM: StrategyPerformance | null;
    Linear: StrategyPerformance | null;
    SVM: StrategyPerformance | null;
    ARIMA: StrategyPerformance | null;
    NIFTY50: StrategyPerformance | null;
  };
  timestamp: string;
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

// Predicted vs Actual Types
export interface PredictedVsActualResponse {
  stocks: Array<{
    symbol: string;
    predicted_return: number;
    actual_return: number;
    error: number;
    confidence: number;
  }>;
  overall_accuracy: number;
  avg_error: number;
  strategy: string;
  period: string;
}

// Backtest Types
export interface BacktestRequest {
  strategy: string;
  start_date: string;
  end_date: string;
  capital: number;
  top_n: number;
  rebalance_frequency: string;
}

export interface BacktestResponse {
  strategy_cagr: number;
  strategy_sharpe: number;
  strategy_sortino: number;
  strategy_max_drawdown: number;
  strategy_volatility: number;
  strategy_calmar: number;
  strategy_win_rate: number;
  benchmark_cagr: number;
  benchmark_sharpe: number;
  benchmark_sortino: number;
  benchmark_max_drawdown: number;
  benchmark_volatility: number;
  benchmark_calmar: number;
  benchmark_win_rate: number;
  dates: string[];
  portfolio_values: number[];
  benchmark_values: number[];
  monthly_returns: number[];
  initial_capital: number;
  final_value: number;
  num_rebalances: number;
  total_periods: number;
}

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

// Old backtest request (keeping for backward compatibility)
export interface OldBacktestRequest {
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
export const getPortfolioSummary = async (signal?: AbortSignal): Promise<PortfolioSummary> => {
  try {
    const response = await apiClient.get<PortfolioSummary>('/portfolio/summary', {
      signal,
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    if (!isCanceledError(error)) console.error('Error fetching portfolio summary:', error);
    throw error;
  }
};

/**
 * Get historical portfolio performance data
 * GET /api/portfolio/performance?timeframe=1M
 */
export const getPortfolioPerformance = async (
  timeframe: '1M' | '3M' | '6M' | '1Y' = '3M',
  signal?: AbortSignal
): Promise<PortfolioPerformance> => {
  try {
    const response = await apiClient.get<PortfolioPerformance>('/portfolio/performance', {
      params: { timeframe },
      signal,
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    if (!isCanceledError(error)) console.error('Error fetching portfolio performance:', error);
    throw error;
  }
};

/**
 * Rebalance portfolio using selected ML model strategy
 * POST /api/portfolio/rebalance
 */
export const rebalancePortfolio = async (
  request: RebalanceRequest,
  signal?: AbortSignal
): Promise<RebalanceResponse> => {
  try {
    const response = await apiClient.post<RebalanceResponse>('/portfolio/rebalance', request, {
      signal,
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    if (!isCanceledError(error)) console.error('Error rebalancing portfolio:', error);
    throw error;
  }
};

/**
 * Get strategy comparison data for all ML models vs Nifty50
 * GET /api/portfolio/strategy-comparison?timeframe=3M&capital=100000
 */
export const getStrategyComparison = async (
  timeframe: '1M' | '3M' | '6M' | '1Y' = '3M',
  capital: number = 100000,
  signal?: AbortSignal
): Promise<StrategyComparisonResponse> => {
  try {
    const response = await apiClient.get<StrategyComparisonResponse>('/portfolio/strategy-comparison', {
      params: { timeframe, capital },
      signal,
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    if (!isCanceledError(error)) console.error('Error fetching strategy comparison:', error);
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
/**
 * Start training all ML models in the background
 * POST /api/analytics/models/train
 */
export const trainModels = async (force: boolean = false): Promise<{
  message: string;
  status: string;
  estimated_time_seconds: number;
}> => {
  try {
    const response = await apiClient.post('/analytics/models/train', null, {
      params: { force }
    });
    return response.data;
  } catch (error) {
    console.error('Error starting model training:', error);
    throw error;
  }
};

/**
 * Get current training status and progress
 * GET /api/analytics/models/training-status
 */
export const getTrainingStatus = async (): Promise<{
  status: 'idle' | 'training' | 'completed' | 'failed';
  progress: number;
  current_model: string | null;
  models_completed: string[];
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}> => {
  try {
    const response = await apiClient.get('/analytics/models/training-status');
    return response.data;
  } catch (error) {
    console.error('Error fetching training status:', error);
    throw error;
  }
};

/**
 * Get ML model performance metrics
 * GET /api/analytics/models
 */
export const getModelPerformance = async (train: boolean = false): Promise<ModelPerformance[]> => {
  try {
    const response = await apiClient.get<{models: ModelPerformance[]} | ModelPerformance[]>('/analytics/models', {
      params: { train }
    });
    // Handle both response formats
    if (Array.isArray(response.data)) {
      return response.data;
    } else if ('models' in response.data) {
      return response.data.models;
    }
    return [];
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

/**
 * Get predicted vs actual performance comparison
 * GET /api/portfolio/predicted-vs-actual?days=90
 */
export const getPredictedVsActual = async (days: number = 90): Promise<PredictedVsActualResponse> => {
  try {
    const response = await apiClient.get<PredictedVsActualResponse>('/portfolio/predicted-vs-actual', {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching predicted vs actual:', error);
    throw error;
  }
};

// Update cash balance
export const updateCashBalance = async (cashBalance: number): Promise<{ success: boolean; cash_balance: number; message: string }> => {
  try {
    const response = await apiClient.put('/portfolio/cash-balance', {
      cash_balance: cashBalance
    });
    return response.data;
  } catch (error) {
    console.error('Error updating cash balance:', error);
    throw error;
  }
};

export default apiClient;
