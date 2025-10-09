// Mock Analytics API Service
// This file contains mock data and API functions for the Analytics dashboard
// Ready for backend integration - just replace mock data with real axios calls

import axios from 'axios';

// Base API URL (replace with real backend URL later)
const API_BASE_URL = '/api/analytics';

// ==================== TYPE DEFINITIONS ====================

export interface KPIData {
  portfolio_return: number;
  risk_metric: number;
  volatility: number;
  sharpe_ratio: number;
}

export interface ModelPerformance {
  model: string;
  accuracy: number;
  return: number;
  mae: number; // Mean Absolute Error
  rmse: number; // Root Mean Square Error
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

// ==================== MOCK DATA ====================

const mockKPIs: KPIData = {
  portfolio_return: 12.3,
  risk_metric: 0.8,
  volatility: 15.2,
  sharpe_ratio: 1.1
};

const mockModelPerformance: ModelPerformance[] = [
  { model: 'LSTM', accuracy: 87, return: 12.5, mae: 45.2, rmse: 67.8 },
  { model: 'Linear', accuracy: 74, return: 9.2, mae: 62.1, rmse: 89.3 },
  { model: 'Logistic', accuracy: 69, return: 7.8, mae: 71.4, rmse: 95.6 },
  { model: 'SVM', accuracy: 81, return: 10.3, mae: 52.3, rmse: 78.4 }
];

// Generate realistic stock data
const generateStockData = (symbol: string, days: number = 90): StockPrediction => {
  const dates: string[] = [];
  const actual: number[] = [];
  const lstm: number[] = [];
  const linear: number[] = [];
  const logistic: number[] = [];
  const svm: number[] = [];

  const basePrice = symbol === 'RELIANCE' ? 2500 : symbol === 'TCS' ? 3200 : 1500;
  const today = new Date();

  for (let i = days; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    dates.push(date.toISOString().split('T')[0]);

    // Generate actual price with realistic volatility
    const trend = Math.sin(i / 10) * 50;
    const noise = (Math.random() - 0.5) * 30;
    const actualPrice = basePrice + trend + noise;
    actual.push(Number(actualPrice.toFixed(2)));

    // LSTM prediction (most accurate)
    lstm.push(Number((actualPrice + (Math.random() - 0.5) * 20).toFixed(2)));

    // Linear prediction (moderate accuracy)
    linear.push(Number((actualPrice + (Math.random() - 0.5) * 40).toFixed(2)));

    // Logistic prediction (less accurate)
    logistic.push(Number((actualPrice + (Math.random() - 0.5) * 50).toFixed(2)));

    // SVM prediction (good accuracy)
    svm.push(Number((actualPrice + (Math.random() - 0.5) * 25).toFixed(2)));
  }

  return {
    symbol,
    dates,
    actual_prices: actual,
    predicted_prices: { LSTM: lstm, Linear: linear, Logistic: logistic, SVM: svm }
  };
};

const mockRecommendations: Recommendation[] = [
  {
    model: 'LSTM',
    return: 12.5,
    confidence: 0.87,
    action: 'Buy',
    description: 'Strong upward trend detected with high confidence. Neural network shows consistent positive signals.'
  },
  {
    model: 'SVM',
    return: 10.3,
    confidence: 0.81,
    action: 'Hold',
    description: 'Moderate growth expected. Support vector analysis indicates stable performance.'
  },
  {
    model: 'Linear',
    return: 9.2,
    confidence: 0.74,
    action: 'Hold',
    description: 'Linear regression shows steady but modest growth trajectory.'
  },
  {
    model: 'Logistic',
    return: 7.8,
    confidence: 0.69,
    action: 'Sell',
    description: 'Lower confidence in continued growth. Consider taking profits.'
  }
];

// ==================== API FUNCTIONS ====================

// Simulate network delay
const delay = (ms: number = 800) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Fetch KPI metrics
 * GET /api/analytics/kpis
 */
export const fetchKPIs = async (): Promise<KPIData> => {
  await delay(500);
  // TODO: Replace with real API call
  // return axios.get(`${API_BASE_URL}/kpis`).then(res => res.data);
  return mockKPIs;
};

/**
 * Fetch ML model performance data
 * GET /api/analytics/models
 */
export const fetchModelPerformance = async (): Promise<ModelPerformance[]> => {
  await delay(600);
  // TODO: Replace with real API call
  // return axios.get(`${API_BASE_URL}/models`).then(res => res.data);
  return mockModelPerformance;
};

/**
 * Fetch stock prediction data
 * GET /api/analytics/stock/:symbol?timeframe=3M
 */
export const fetchStockPrediction = async (
  symbol: string,
  timeframe: '1M' | '3M' | '6M' | '1Y' = '3M'
): Promise<StockPrediction> => {
  await delay(800);
  
  // Calculate days based on timeframe
  const days = {
    '1M': 30,
    '3M': 90,
    '6M': 180,
    '1Y': 365
  }[timeframe];

  // TODO: Replace with real API call
  // return axios.get(`${API_BASE_URL}/stock/${symbol}`, { params: { timeframe } }).then(res => res.data);
  return generateStockData(symbol, days);
};

/**
 * Fetch model recommendations
 * GET /api/analytics/recommendations
 */
export const fetchRecommendations = async (): Promise<Recommendation[]> => {
  await delay(700);
  // TODO: Replace with real API call
  // return axios.get(`${API_BASE_URL}/recommendations`).then(res => res.data);
  return mockRecommendations;
};

/**
 * Fetch filtered data based on timeframe
 * This will be used when user changes filters
 */
export const fetchFilteredAnalytics = async (
  timeframe: '1M' | '3M' | '6M' | '1Y',
  model?: string
) => {
  await delay(600);
  // TODO: Implement filtered API call
  // return axios.get(`${API_BASE_URL}/filtered`, { params: { timeframe, model } }).then(res => res.data);
  return {
    kpis: mockKPIs,
    models: mockModelPerformance,
    recommendations: mockRecommendations
  };
};
