"""
Multi-provider financial data service with fallback support
Supports: Alpha Vantage, Twelve Data, Financial Modeling Prep, Yahoo Finance
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import os
from fastapi import HTTPException
import json

class MultiProviderDataService:
    """Financial data service with multiple provider fallback"""
    
    def __init__(self):
        # API Keys (set these in environment variables)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY', 'demo')
        self.fmp_key = os.getenv('FMP_API_KEY', 'demo')
        
        # Provider configurations
        self.providers = {
            'alpha_vantage': {
                'base_url': 'https://www.alphavantage.co/query',
                'rate_limit': 5,  # requests per minute
                'daily_limit': 25
            },
            'twelve_data': {
                'base_url': 'https://api.twelvedata.com',
                'rate_limit': 8,  # requests per minute
                'daily_limit': 800
            },
            'fmp': {
                'base_url': 'https://financialmodelingprep.com/api/v3',
                'rate_limit': 10,
                'daily_limit': 250
            }
        }
        
        # Indian stock symbol mappings
        self.indian_symbols = {
            'RELIANCE.NS': {'alpha': 'RELIANCE.BSE', 'twelve': 'RELIANCE', 'fmp': 'RELIANCE.NS'},
            'TCS.NS': {'alpha': 'TCS.BSE', 'twelve': 'TCS', 'fmp': 'TCS.NS'},
            'HDFCBANK.NS': {'alpha': 'HDFCBANK.BSE', 'twelve': 'HDFCBANK', 'fmp': 'HDFCBANK.NS'},
            'ICICIBANK.NS': {'alpha': 'ICICIBANK.BSE', 'twelve': 'ICICIBANK', 'fmp': 'ICICIBANK.NS'},
            'INFY.NS': {'alpha': 'INFY.BSE', 'twelve': 'INFY', 'fmp': 'INFY.NS'},
        }
    
    async def get_stock_data_alpha_vantage(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """Fetch data from Alpha Vantage"""
        try:
            mapped_symbol = self.indian_symbols.get(symbol, {}).get('alpha', symbol)
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': mapped_symbol,
                    'outputsize': 'full' if period in ['1y', '2y', '5y'] else 'compact',
                    'apikey': self.alpha_vantage_key
                }
                
                async with session.get(self.providers['alpha_vantage']['base_url'], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'Time Series (Daily)' in data:
                            time_series = data['Time Series (Daily)']
                            
                            # Convert to our standard format
                            records = []
                            for date, values in time_series.items():
                                records.append({
                                    'Date': date,
                                    'Open': float(values['1. open']),
                                    'High': float(values['2. high']),
                                    'Low': float(values['3. low']),
                                    'Close': float(values['4. close']),
                                    'Volume': int(values['5. volume'])
                                })
                            
                            # Sort by date and limit by period
                            records.sort(key=lambda x: x['Date'], reverse=True)
                            records = self._filter_by_period(records, period)
                            
                            return {
                                'symbol': symbol,
                                'data': records,
                                'data_source': 'alpha_vantage',
                                'last_updated': datetime.now().isoformat()
                            }
                        
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {str(e)}")
            return None
    
    async def get_stock_data_twelve_data(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """Fetch data from Twelve Data"""
        try:
            mapped_symbol = self.indian_symbols.get(symbol, {}).get('twelve', symbol.replace('.NS', ''))
            
            # Convert period to twelve data format
            interval_map = {'1d': '1day', '5d': '1day', '1mo': '1day', '3mo': '1day', 
                          '6mo': '1day', '1y': '1day', '2y': '1day', '5y': '1day'}
            interval = interval_map.get(period, '1day')
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'symbol': mapped_symbol,
                    'interval': interval,
                    'country': 'India',
                    'apikey': self.twelve_data_key,
                    'format': 'JSON',
                    'outputsize': '5000'
                }
                
                url = f"{self.providers['twelve_data']['base_url']}/time_series"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'values' in data and data['values']:
                            records = []
                            for item in data['values']:
                                records.append({
                                    'Date': item['datetime'],
                                    'Open': float(item['open']),
                                    'High': float(item['high']),
                                    'Low': float(item['low']),
                                    'Close': float(item['close']),
                                    'Volume': int(item['volume']) if item['volume'] else 0
                                })
                            
                            records = self._filter_by_period(records, period)
                            
                            return {
                                'symbol': symbol,
                                'data': records,
                                'data_source': 'twelve_data',
                                'last_updated': datetime.now().isoformat()
                            }
                        
        except Exception as e:
            print(f"Twelve Data error for {symbol}: {str(e)}")
            return None
    
    async def get_stock_data_fmp(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """Fetch data from Financial Modeling Prep"""
        try:
            mapped_symbol = self.indian_symbols.get(symbol, {}).get('fmp', symbol)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.providers['fmp']['base_url']}/historical-price-full/{mapped_symbol}"
                params = {'apikey': self.fmp_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'historical' in data and data['historical']:
                            records = []
                            for item in data['historical']:
                                records.append({
                                    'Date': item['date'],
                                    'Open': float(item['open']),
                                    'High': float(item['high']),
                                    'Low': float(item['low']),
                                    'Close': float(item['close']),
                                    'Volume': int(item['volume'])
                                })
                            
                            records = self._filter_by_period(records, period)
                            
                            return {
                                'symbol': symbol,
                                'data': records,
                                'data_source': 'fmp',
                                'last_updated': datetime.now().isoformat()
                            }
                        
        except Exception as e:
            print(f"FMP error for {symbol}: {str(e)}")
            return None
    
    def _filter_by_period(self, records: List[Dict], period: str) -> List[Dict]:
        """Filter records by time period"""
        if not records:
            return records
            
        # Calculate cutoff date
        days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
        days = days_map.get(period, 365)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter records
        filtered = []
        for record in records:
            record_date = datetime.strptime(record['Date'], '%Y-%m-%d')
            if record_date >= cutoff_date:
                filtered.append(record)
        
        return filtered[:days]  # Limit to requested period
    
    async def get_stock_data_with_fallback(self, symbol: str, period: str = "1y") -> Dict:
        """Get stock data with multi-provider fallback"""
        
        # Try providers in order of preference
        providers = [
            ('twelve_data', self.get_stock_data_twelve_data),
            ('alpha_vantage', self.get_stock_data_alpha_vantage),
            ('fmp', self.get_stock_data_fmp)
        ]
        
        for provider_name, provider_func in providers:
            try:
                print(f"Trying {provider_name} for {symbol}")
                result = await provider_func(symbol, period)
                if result and result.get('data'):
                    print(f"✅ Success with {provider_name}")
                    return result
                else:
                    print(f"❌ No data from {provider_name}")
            except Exception as e:
                print(f"❌ {provider_name} failed: {str(e)}")
                continue
        
        # If all providers fail, return mock data
        print(f"⚠️ All providers failed for {symbol}, using mock data")
        return self._generate_mock_data(symbol, period)
    
    def _generate_mock_data(self, symbol: str, period: str) -> Dict:
        """Generate mock data when all providers fail"""
        import random
        
        days_map = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825}
        days = days_map.get(period, 365)
        
        base_price = random.uniform(100, 2000)
        data = []
        current_price = base_price
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            change = random.uniform(-0.03, 0.03)  # ±3% daily change
            current_price *= (1 + change)
            
            volume = random.randint(100000, 10000000)
            open_price = current_price * random.uniform(0.99, 1.01)
            high_price = max(open_price, current_price) * random.uniform(1.00, 1.02)
            low_price = min(open_price, current_price) * random.uniform(0.98, 1.00)
            
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
            "data_source": "mock_fallback",
            "last_updated": datetime.now().isoformat()
        }
