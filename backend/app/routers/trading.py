from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import pandas as pd
import yfinance as yf
from datetime import datetime
from app.models.schemas import TradingSignal, BacktestRequest, BacktestResult
from app.services.ml_service import MLService
from app.services.portfolio_service import PortfolioService
from app.services.data_service import DataService

router = APIRouter()
ml_service = MLService()
portfolio_service = PortfolioService()
data_service = DataService()

@router.get("/signals/{symbol}")
async def get_trading_signal(symbol: str, strategy: str = "ema_crossover"):
    """Get trading signal for a specific stock"""
    try:
        if strategy == "ml_prediction":
            result = await ml_service.predict_stock_price(symbol)
        else:
            signals = await generate_trading_signals([symbol])
            result = signals[0] if signals else {
                "symbol": symbol,
                "signal": "HOLD",
                "confidence": 0.5,
                "price": 0.0,
                "timestamp": str(datetime.now()),
                "strategy": "EMA_Crossover"
            }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals")
async def get_multiple_signals(symbols: str = "RELIANCE.NS,TCS.NS,HDFCBANK.NS"):
    """Get trading signals for multiple stocks"""
    try:
        symbol_list = symbols.split(",")
        signals = await generate_trading_signals(symbol_list)
        return {"signals": signals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backtest")
async def backtest_strategy(request: BacktestRequest):
    """Backtest a trading strategy"""
    try:
        results = []
        
        for symbol in request.symbols:
            result = await portfolio_service.backtest_strategy(
                symbol=symbol,
                strategy=request.strategy,
                start_date=request.start_date.strftime("%Y-%m-%d"),
                end_date=request.end_date.strftime("%Y-%m-%d")
            )
            results.append(result)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train/{symbol}")
async def train_model(symbol: str, model_type: str = "linear_regression"):
    """Train ML model for a specific stock"""
    try:
        # Get training data
        stock_data = await data_service.get_stock_data(symbol, period="5y")
        df = pd.DataFrame(stock_data["data"])
        
        if model_type == "linear_regression":
            result = await ml_service.train_linear_regression(symbol, df)
        elif model_type == "xgboost":
            result = await ml_service.train_xgboost_classifier(symbol, df)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model type: {model_type}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/{symbol}")
async def get_prediction(symbol: str, model_type: str = "linear_regression"):
    """Get ML prediction for a stock"""
    try:
        result = await ml_service.predict_stock_price(symbol, model_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_available_strategies():
    """Get list of available trading strategies"""
    return {
        "strategies": [
            {
                "name": "EMA_Crossover",
                "description": "Exponential Moving Average crossover strategy",
                "parameters": {"short_period": 20, "long_period": 50}
            },
            {
                "name": "Linear_Regression", 
                "description": "Linear regression based price prediction",
                "parameters": {"lookback_period": 60}
            },
            {
                "name": "XGBoost",
                "description": "XGBoost machine learning classification",
                "parameters": {"n_estimators": 100, "max_depth": 5}
            },
            {
                "name": "SVM",
                "description": "Support Vector Machine classification",
                "parameters": {"kernel": "rbf", "C": 1.0}
            }
        ]
    }

async def generate_trading_signals(symbols: List[str]) -> List[Dict]:
    """Generate trading signals for multiple symbols using EMA crossover strategy"""
    signals = []
    
    for symbol in symbols:
        try:
            # Get data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo", interval="1d")
            
            if len(data) < 50:
                continue
            
            # EMA crossover strategy
            data['EMA_20'] = data['Close'].ewm(span=20).mean()
            data['EMA_50'] = data['Close'].ewm(span=50).mean()
            
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            # Signal logic
            if latest['EMA_20'] > latest['EMA_50'] and prev['EMA_20'] <= prev['EMA_50']:
                signal = "BUY"
                confidence = 0.8
            elif latest['EMA_20'] < latest['EMA_50'] and prev['EMA_20'] >= prev['EMA_50']:
                signal = "SELL"
                confidence = 0.8
            else:
                signal = "HOLD"
                confidence = 0.6
            
            signals.append({
                "symbol": symbol,
                "signal": signal,
                "confidence": confidence,
                "price": float(latest['Close']),
                "timestamp": str(latest.name),
                "strategy": "EMA_Crossover",
                "ema_20": float(latest['EMA_20']),
                "ema_50": float(latest['EMA_50'])
            })
            
        except Exception as e:
            print(f"Error generating signal for {symbol}: {e}")
            continue
    
    return signals