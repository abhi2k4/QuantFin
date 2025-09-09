import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
import requests
from fastapi import HTTPException
import os
import math
import logging

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 300  # 5 minutes cache
        
        # Notebook API configuration
        self.notebook_api_url = "http://localhost:64441"  # Updated to match current server port
        self.use_notebook_api = True
        self.notebook_api_timeout = 10
        
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
        
        logger.info(f"🔧 DataService initialized")
        logger.info(f"📊 Notebook API URL: {self.notebook_api_url}")
        logger.info(f"🎯 Use Notebook API: {self.use_notebook_api}")
    
    def _check_notebook_api_health(self) -> bool:
        """Check if notebook API is available"""
        try:
            response = requests.get(f"{self.notebook_api_url}/api/health", timeout=3)
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Notebook API health check passed: {health_data}")
                return True
            else:
                logger.warning(f"⚠️ Notebook API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Notebook API not available: {str(e)}")
            return False
    
    async def _get_data_from_notebook_api(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict:
        """Get data from notebook API"""
        try:
            logger.info(f"🌐 Requesting data from notebook API: {symbol}")
            
            url = f"{self.notebook_api_url}/api/stock"
            params = {
                'symbol': symbol,
                'period': period,
                'interval': interval
            }
            
            response = requests.get(url, params=params, timeout=self.notebook_api_timeout)
            
            if response.status_code == 200:
                notebook_result = response.json()
                if notebook_result.get('success', False):
                    # Convert the data format to match our expected format
                    if 'data' in notebook_result:
                        # Convert the notebook API data format to our internal format
                        converted_data = []
                        for item in notebook_result['data']:
                            # Handle different date formats
                            date_str = item.get('Date', item.get('date', ''))
                            if date_str:
                                # Parse various date formats and convert to simple YYYY-MM-DD
                                if 'T' in date_str or '+' in date_str:
                                    # ISO format with timezone
                                    from datetime import datetime
                                    try:
                                        dt = datetime.fromisoformat(date_str.replace('+05:30', ''))
                                        date_str = dt.strftime('%Y-%m-%d')
                                    except:
                                        # Fallback: extract just the date part
                                        date_str = date_str.split('T')[0] if 'T' in date_str else date_str.split(' ')[0]
                            
                            converted_data.append({
                                'Date': date_str,  # Use 'Date' to match portfolio service expectations
                                'Open': float(item.get('Open', item.get('open', 0))),
                                'High': float(item.get('High', item.get('high', 0))),
                                'Low': float(item.get('Low', item.get('low', 0))),
                                'Close': float(item.get('Close', item.get('close', 0))),
                                'Volume': int(item.get('Volume', item.get('volume', 0)))
                            })
                        
                        # Calculate current price and change
                        current_price = converted_data[-1]['Close'] if converted_data else 0
                        change = 0
                        change_percent = 0
                        
                        if len(converted_data) >= 2:
                            prev_price = converted_data[-2]['Close']
                            change = current_price - prev_price
                            change_percent = (change / prev_price) * 100 if prev_price != 0 else 0
                        
                        # Return in our expected format
                        result = {
                            'symbol': symbol,
                            'data': converted_data,
                            'current_price': current_price,
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'info': notebook_result.get('info', {}),
                            'success': True,
                            'message': f"Successfully fetched {len(converted_data)} data points via notebook API",
                            'data_source': notebook_result.get('data_source', 'notebook_api')
                        }
                        
                        logger.info(f"✅ Notebook API success: {len(converted_data)} data points for {symbol}")
                        return result
                    
                    logger.info(f"✅ Notebook API success: {len(notebook_result.get('data', []))} data points for {symbol}")
                    return notebook_result
                else:
                    logger.error(f"❌ Notebook API returned unsuccessful response for {symbol}")
                    raise Exception("Notebook API returned unsuccessful response")
            else:
                logger.error(f"❌ Notebook API HTTP error {response.status_code} for {symbol}")
                raise Exception(f"Notebook API HTTP error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Notebook API request failed for {symbol}: {str(e)}")
            raise e
    
    def _get_cache_key(self, symbol: str, period: str, interval: str) -> str:
        """Generate cache key for data requests"""
        return f"{symbol}_{period}_{interval}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        cache_time = datetime.fromisoformat(cache_entry.get('cache_time', ''))
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def _get_symbol_alternatives(self, symbol: str) -> List[str]:
        """Get alternative symbol formats for Indian stocks"""
        symbol_map = {
            'RELIANCE.NS': ['RELIANCE.NS', 'RELIANCE.BO'],
            'TCS.NS': ['TCS.NS', 'TCS.BO'],
            'HDFCBANK.NS': ['HDFCBANK.NS', 'HDFCBANK.BO'],
            'ICICIBANK.NS': ['ICICIBANK.NS', 'ICICIBANK.BO'],
            'INFY.NS': ['INFY.NS', 'INFY.BO'],
            'LT.NS': ['LT.NS', 'LT.BO'],
            'ITC.NS': ['ITC.NS', 'ITC.BO'],
            'HINDUNILVR.NS': ['HINDUNILVR.NS', 'HINDUNILVR.BO'],
            'SBIN.NS': ['SBIN.NS', 'SBIN.BO'],
            'BHARTIARTL.NS': ['BHARTIARTL.NS', 'BHARTIARTL.BO'],
            'KOTAKBANK.NS': ['KOTAKBANK.NS', 'KOTAKBANK.BO'],
            'BAJFINANCE.NS': ['BAJFINANCE.NS', 'BAJFINANCE.BO'],
            'ASIANPAINT.NS': ['ASIANPAINT.NS', 'ASIANPAINT.BO'],
            'HCLTECH.NS': ['HCLTECH.NS', 'HCLTECH.BO'],
            'AXISBANK.NS': ['AXISBANK.NS', 'AXISBANK.BO'],
            'MARUTI.NS': ['MARUTI.NS', 'MARUTI.BO'],
            'SUNPHARMA.NS': ['SUNPHARMA.NS', 'SUNPHARMA.BO'],
            'NTPC.NS': ['NTPC.NS', 'NTPC.BO'],
            'TITAN.NS': ['TITAN.NS', 'TITAN.BO'],
            'ULTRACEMCO.NS': ['ULTRACEMCO.NS', 'ULTRACEMCO.BO'],
            'TECHM.NS': ['TECHM.NS', 'TECHM.BO'],
            'POWERGRID.NS': ['POWERGRID.NS', 'POWERGRID.BO'],
            'NESTLEIND.NS': ['NESTLEIND.NS', 'NESTLEIND.BO'],
            'TATASTEEL.NS': ['TATASTEEL.NS', 'TATASTEEL.BO'],
            'JSWSTEEL.NS': ['JSWSTEEL.NS', 'JSWSTEEL.BO'],
            'WIPRO.NS': ['WIPRO.NS', 'WIPRO.BO'],
            'ADANIENT.NS': ['ADANIENT.NS', 'ADANIENT.BO'],
            'DIVISLAB.NS': ['DIVISLAB.NS', 'DIVISLAB.BO'],
            'HDFCLIFE.NS': ['HDFCLIFE.NS', 'HDFCLIFE.BO'],
            'GRASIM.NS': ['GRASIM.NS', 'GRASIM.BO'],
            'M&M.NS': ['M&M.NS', 'M&M.BO'],
            'CIPLA.NS': ['CIPLA.NS', 'CIPLA.BO'],
            'BRITANNIA.NS': ['BRITANNIA.NS', 'BRITANNIA.BO'],
            'BPCL.NS': ['BPCL.NS', 'BPCL.BO'],
            'DRREDDY.NS': ['DRREDDY.NS', 'DRREDDY.BO'],
            'EICHERMOT.NS': ['EICHERMOT.NS', 'EICHERMOT.BO'],
            'SBILIFE.NS': ['SBILIFE.NS', 'SBILIFE.BO'],
            'HEROMOTOCO.NS': ['HEROMOTOCO.NS', 'HEROMOTOCO.BO'],
            'APOLLOHOSP.NS': ['APOLLOHOSP.NS', 'APOLLOHOSP.BO'],
            'BAJAJFINSV.NS': ['BAJAJFINSV.NS', 'BAJAJFINSV.BO'],
            'COALINDIA.NS': ['COALINDIA.NS', 'COALINDIA.BO'],
            'ONGC.NS': ['ONGC.NS', 'ONGC.BO'],
            'ADANIPORTS.NS': ['ADANIPORTS.NS', 'ADANIPORTS.BO'],
            'TATAMOTORS.NS': ['TATAMOTORS.NS', 'TATAMOTORS.BO'],
            'BAJAJ-AUTO.NS': ['BAJAJ-AUTO.NS', 'BAJAJ-AUTO.BO'],
            'INDUSINDBK.NS': ['INDUSINDBK.NS', 'INDUSINDBK.BO'],
            'HDFCAMC.NS': ['HDFCAMC.NS', 'HDFCAMC.BO'],
            'SHREECEM.NS': ['SHREECEM.NS', 'SHREECEM.BO'],
            'ICICIPRULI.NS': ['ICICIPRULI.NS', 'ICICIPRULI.BO'],
            'HINDALCO.NS': ['HINDALCO.NS', 'HINDALCO.BO']
        }
        
        return symbol_map.get(symbol, [symbol])

    async def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict:
        """Fetch stock data with notebook API first, then fallback to yfinance"""
        
        # Check cache first
        cache_key = self._get_cache_key(symbol, period, interval)
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            logger.info(f"📋 Cache hit for {symbol}")
            return self.cache[cache_key]['data']
        
        logger.info(f"🔍 Fetching fresh data for {symbol} (period: {period}, interval: {interval})")
        
        # Strategy 1: Try Notebook API first (if enabled)
        if self.use_notebook_api:
            try:
                logger.info(f"🌐 Attempting notebook API for {symbol}")
                notebook_result = await self._get_data_from_notebook_api(symbol, period, interval)
                
                if notebook_result and notebook_result.get('success', False):
                    # Cache the successful result
                    self.cache[cache_key] = {
                        'data': notebook_result,
                        'cache_time': datetime.now().isoformat()
                    }
                    
                    logger.info(f"✅ Notebook API success for {symbol}: {len(notebook_result.get('data', []))} data points")
                    return notebook_result
                    
            except Exception as notebook_error:
                logger.warning(f"⚠️ Notebook API failed for {symbol}: {str(notebook_error)}")
                logger.info("🔄 Falling back to direct yfinance...")
        
        # Strategy 2: Fallback to enhanced yfinance (existing method)
        try:
            logger.info(f"📊 Using enhanced yfinance for {symbol}")
            return await self._get_stock_data_yfinance(symbol, period, interval)
            
        except Exception as yfinance_error:
            logger.error(f"❌ Enhanced yfinance also failed for {symbol}: {str(yfinance_error)}")
            logger.info(f"🎭 Using mock data for {symbol}")
            return self._get_mock_stock_data(symbol, period)
    
    async def _get_stock_data_yfinance(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict:
        """Enhanced yfinance data fetching (original method)"""
        try:
            # Add initial delay to avoid rate limiting
            await asyncio.sleep(0.5)
            
            # Special handling for Indian stocks that might have issues
            if symbol.endswith('.NS') or symbol.endswith('.BO'):
                # Get alternative symbol formats
                alternative_symbols = self._get_symbol_alternatives(symbol)
                
                for i, alt_symbol in enumerate(alternative_symbols):
                    try:
                        logger.info(f"📊 Attempting yfinance with {alt_symbol} (attempt {i+1}/{len(alternative_symbols)})")
                        
                        # Progressive delay - longer delays for subsequent attempts
                        if i > 0:
                            delay = min(2 ** i, 10)  # Exponential backoff, max 10 seconds
                            await asyncio.sleep(delay)
                        
                        ticker = yf.Ticker(alt_symbol)
                        hist = ticker.history(period=period, interval=interval)
                        
                        # Try to get info with timeout/retry
                        try:
                            info = ticker.info
                        except:
                            info = {}  # Continue without info if it fails
                        
                        if not hist.empty and len(hist) > 10:  # Require at least 10 data points
                            # Success with this symbol
                            logger.info(f"✅ yfinance success with {alt_symbol}: {len(hist)} data points")
                            break
                        else:
                            logger.warning(f"⚠️ {alt_symbol} returned insufficient data: {len(hist)} points")
                            
                    except Exception as e:
                        logger.warning(f"❌ Failed to fetch {alt_symbol} via yfinance: {str(e)}")
                        # Check if it's a rate limiting error
                        if "429" in str(e) or "Too Many Requests" in str(e):
                            logger.warning(f"🚫 Rate limited on {alt_symbol}, waiting longer...")
                            await asyncio.sleep(5)  # Wait 5 seconds on rate limit
                        else:
                            await asyncio.sleep(1)  # Shorter wait for other errors
                        continue
                else:
                    # All alternatives failed
                    raise Exception(f"No valid data found for any alternative of {symbol}")
            else:
                # Non-Indian stocks
                await asyncio.sleep(0.5)  # Rate limiting for all requests
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=interval)
                try:
                    info = ticker.info
                except:
                    info = {}  # Continue without info if it fails
            
            # Format data
            if hist.empty:
                raise Exception(f"No data returned for {symbol}")
                
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            result = {
                'symbol': symbol,
                'data': data,
                'current_price': data[-1]['close'] if data else 0,
                'change': 0,
                'change_percent': 0,
                'info': info,
                'success': True,
                'message': f"Successfully fetched {len(data)} data points via yfinance"
            }
            
            # Cache the result
            cache_key = self._get_cache_key(symbol, period, interval)
            self.cache[cache_key] = {
                'data': result,
                'cache_time': datetime.now().isoformat()
            }
            
            logger.info(f"✅ yfinance data fetched for {symbol}: {len(data)} points")
            return result
            
        except Exception as e:
            logger.error(f"❌ yfinance fetch failed for {symbol}: {str(e)}")
            raise e

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
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(current_price, 2),
                "volume": volume
            })
        
        logger.warning(f"🎭 Generated mock data for {symbol}: {len(data)} points")
        
        return {
            "symbol": symbol,
            "data": data,
            "current_price": round(current_price, 2),
            "change": 0,
            "change_percent": 0,
            "info": {
                "symbol": symbol,
                "longName": f"Mock Company {symbol.replace('.NS', '')}",
                "currentPrice": round(current_price, 2),
                "marketCap": random.randint(10000000000, 500000000000),
                "trailingPE": round(random.uniform(10, 30), 2),
                "dividendYield": round(random.uniform(0.01, 0.05), 4)
            },
            "success": True,
            "message": f"Generated {len(data)} mock data points",
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