import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from fastapi import HTTPException
import os
import math

try:
    from app.utils.config import get_settings
    from app.utils.json_encoder import clean_data_for_json
except ImportError:
    def get_settings(): 
        return type('Settings', (), {})()  # Simple mock settings
    def clean_data_for_json(data):
        return data  # Fallback if import fails

class DataService:
    """Service for fetching and managing financial data"""
    
    def __init__(self):
        self.settings = get_settings()
        self.nifty50_symbols = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS', 
            'LT.NS', 'ITC.NS', 'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS',
            'KOTAKBANK.NS', 'BAJFINANCE.NS', 'ASIANPAINT.NS', 'HCLTECH.NS', 
            'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'NTPC.NS', 'TITAN.NS',
            'ULTRACEMCO.NS', 'TECHM.NS', 'POWERGRID.NS', 'NESTLEIND.NS',
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'WIPRO.NS', 'ADANIENT.NS',
            'DIVISLAB.NS', 'HDFCLIFE.NS', 'GRASIM.NS', 'M&M.NS', 'CIPLA.NS',
            'BRITANNIA.NS', 'BPCL.NS', 'DRREDDY.NS', 'EICHERMOT.NS',
            'SBILIFE.NS', 'HEROMOTOCO.NS', 'APOLLOHOSP.NS', 'BAJAJFINSV.NS',
            'COALINDIA.NS', 'ONGC.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS',
            'BAJAJ-AUTO.NS', 'INDUSINDBK.NS', 'HDFCAMC.NS', 'SHREECEM.NS',
            'ICICIPRULI.NS', 'HINDALCO.NS'
        ]
    
    async def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict:
        """Fetch stock data using yfinance with fallback"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            info = ticker.info
            
            # Check if we got meaningful data
            if hist.empty or len(hist) == 0:
                raise Exception("No data received from Yahoo Finance")
            
            # Clean the data and handle NaN/Inf values
            hist_clean = hist.reset_index()
            
            # Replace NaN and infinite values
            hist_clean = hist_clean.replace([np.inf, -np.inf], np.nan)
            hist_clean = hist_clean.fillna(method='ffill').fillna(0)
            
            # Convert to records and clean
            data_records = hist_clean.to_dict('records')
            cleaned_records = clean_data_for_json(data_records)
            
            # Clean info data
            cleaned_info = {}
            if info:
                for key, value in info.items():
                    if isinstance(value, (int, float)):
                        if math.isnan(value) if isinstance(value, float) else False:
                            cleaned_info[key] = None
                        elif math.isinf(value) if isinstance(value, float) else False:
                            cleaned_info[key] = None
                        else:
                            cleaned_info[key] = value
                    else:
                        cleaned_info[key] = value
            
            return {
                "symbol": symbol,
                "data": cleaned_records,
                "info": cleaned_info,
                "last_updated": datetime.now().isoformat(),
                "data_source": "yahoo_finance"
            }
        except Exception as e:
            print(f"Failed to get ticker '{symbol}' reason: {str(e)}")
            # Always use fallback if any error occurs
            return self._get_mock_stock_data(symbol, period)
    
    def _get_mock_stock_data(self, symbol: str, period: str) -> Dict:
        """Generate mock stock data for testing when Yahoo Finance is unavailable"""
        import random
        from datetime import datetime, timedelta
        
        # Determine number of days based on period
        days_map = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825}
        days = days_map.get(period, 365)
        
        # Generate mock price data
        base_price = random.uniform(100, 2000)  # Random base price
        data = []
        current_price = base_price
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # Simulate price movement (random walk)
            change = random.uniform(-0.05, 0.05)  # +/- 5% daily change
            current_price *= (1 + change)
            
            volume = random.randint(100000, 10000000)
            
            # OHLC data
            open_price = current_price * random.uniform(0.98, 1.02)
            high_price = max(open_price, current_price) * random.uniform(1.00, 1.03)
            low_price = min(open_price, current_price) * random.uniform(0.97, 1.00)
            
            data.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Open": round(open_price, 2),
                "High": round(high_price, 2),
                "Low": round(low_price, 2),
                "Close": round(current_price, 2),
                "Volume": volume
            })
        
        return {
            "symbol": symbol,
            "data": data,
            "info": {
                "symbol": symbol,
                "longName": f"Mock Company {symbol.replace('.NS', '')}",
                "currentPrice": round(current_price, 2),
                "marketCap": random.randint(10000000000, 500000000000),
                "trailingPE": round(random.uniform(10, 30), 2),
                "dividendYield": round(random.uniform(0.01, 0.05), 4)
            },
            "last_updated": datetime.now().isoformat(),
            "data_source": "mock_fallback"
        }
    
    async def get_multiple_stocks(self, symbols: List[str], period: str = "1y") -> Dict:
        """Fetch multiple stocks data"""
        try:
            data = yf.download(symbols, period=period, group_by='ticker', threads=True, auto_adjust=True)
            
            result = {}
            for symbol in symbols:
                if len(symbols) == 1:
                    symbol_data = data
                else:
                    symbol_data = data[symbol] if symbol in data.columns.levels[0] else None
                
                if symbol_data is not None:
                    result[symbol] = symbol_data.reset_index().to_dict('records')
            
            return {
                "data": result,
                "symbols": symbols,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching multiple stocks: {str(e)}")
    
    async def get_financial_ratios(self, symbol: str) -> Dict:
        """Get financial ratios for a stock with fallback"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "ratios": {
                    "pe_ratio": info.get('trailingPE'),
                    "pb_ratio": info.get('priceToBook'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "roe": info.get('returnOnEquity'),
                    "revenue_growth": info.get('revenueGrowth'),
                    "profit_margin": info.get('profitMargins'),
                    "market_cap": info.get('marketCap'),
                    "dividend_yield": info.get('dividendYield'),
                    "current_price": info.get('currentPrice'),
                    "52_week_high": info.get('fiftyTwoWeekHigh'),
                    "52_week_low": info.get('fiftyTwoWeekLow')
                },
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                # Return mock ratios when rate limited
                import random
                return {
                    "symbol": symbol,
                    "ratios": {
                        "pe_ratio": round(random.uniform(10, 30), 2),
                        "pb_ratio": round(random.uniform(1, 5), 2),
                        "debt_to_equity": round(random.uniform(0.1, 1.0), 2),
                        "roe": round(random.uniform(0.05, 0.25), 3),
                        "revenue_growth": round(random.uniform(-0.1, 0.3), 3),
                        "profit_margin": round(random.uniform(0.05, 0.20), 3),
                        "market_cap": random.randint(10000000000, 500000000000),
                        "dividend_yield": round(random.uniform(0.01, 0.05), 4),
                        "current_price": round(random.uniform(100, 2000), 2),
                        "52_week_high": round(random.uniform(1200, 2200), 2),
                        "52_week_low": round(random.uniform(80, 800), 2)
                    },
                    "last_updated": datetime.now().isoformat(),
                    "data_source": "mock_fallback"
                }
            else:
                raise HTTPException(status_code=500, detail=f"Error fetching ratios for {symbol}: {str(e)}")
    
    async def get_nifty50_data(self, period: str = "5y") -> Dict:
        """Get Nifty 50 constituent data"""
        try:
            return await self.get_multiple_stocks(self.nifty50_symbols, period)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching Nifty 50 data: {str(e)}")
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = data.copy()
        
        # Ensure numeric dtype and handle NaN values
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        
        # Fill NaN values with forward fill then 0
        df = df.fillna(method='ffill').fillna(0)
        
        close = df['Close'].astype(float)
        
        # Simple Moving Averages
        df['SMA_20'] = close.rolling(window=20, min_periods=1).mean()
        df['SMA_50'] = close.rolling(window=50, min_periods=1).mean()
        
        # Exponential Moving Averages
        df['EMA_20'] = close.ewm(span=20, min_periods=1).mean()
        df['EMA_50'] = close.ewm(span=50, min_periods=1).mean()
        
        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(window=14, min_periods=1).mean()
        loss = (-delta).clip(lower=0).rolling(window=14, min_periods=1).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = close.ewm(span=12, min_periods=1).mean()
        ema_26 = close.ewm(span=26, min_periods=1).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, min_periods=1).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = close.rolling(window=20, min_periods=1).mean()
        bb_std = close.rolling(window=20, min_periods=1).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Replace any remaining NaN or inf values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        return df