from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd

class StockData(BaseModel):
    """Stock market data schema"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class TradingSignal(BaseModel):
    """Trading signal schema"""
    symbol: str
    signal: str = Field(..., pattern="^(BUY|SELL|HOLD)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    price: float
    timestamp: datetime
    strategy: str
    metadata: Dict[str, Any] = {}

class Portfolio(BaseModel):
    """Portfolio schema"""
    id: str
    name: str
    value: float
    cash: float
    holdings: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class PortfolioOptimization(BaseModel):
    """Portfolio optimization request"""
    symbols: List[str]
    investment_amount: float = 100000.0
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    time_horizon: int = 252  # Trading days (1 year)

class NewsAnalysis(BaseModel):
    """News analysis schema"""
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sentiment_label: str
    symbols: List[str] = []

class BacktestRequest(BaseModel):
    """Backtesting request schema"""
    strategy: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000.0
    parameters: Dict[str, Any] = {}

class BacktestResult(BaseModel):
    """Backtesting result schema"""
    strategy: str
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    trade_count: int
    final_value: float
    trades: List[Dict[str, Any]]

class FinancialRatios(BaseModel):
    """Financial ratios schema"""
    symbol: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    debt_to_equity: Optional[float]
    roe: Optional[float]
    revenue_growth: Optional[float]
    profit_margin: Optional[float]
    updated_at: datetime

class MLPrediction(BaseModel):
    """ML prediction schema"""
    symbol: str
    model_type: str
    predicted_price: float
    current_price: float
    expected_return: float
    confidence: float
    prediction_date: datetime
    target_date: datetime