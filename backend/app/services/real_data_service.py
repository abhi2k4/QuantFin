"""
Real Data Service - Loads and manages actual stock data from CSV files

This service replaces ALL mock data with real historical stock data.
No random numbers, no fake values - only actual market data.

Author: QuantFin Team
Date: 2025-10-10
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class RealDataService:
    """
    Service for loading and managing real stock data from CSV files.
    Handles all 48 Nifty50 stocks + Nifty50 index data.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize with data directory containing CSV files."""
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, pd.DataFrame] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load all available symbols
        self.symbols = self._get_all_symbols()
        self.logger.info(f"RealDataService initialized with {len(self.symbols)} stocks")
    
    def _get_all_symbols(self) -> List[str]:
        """Get list of all available stock symbols from CSV files."""
        if not self.data_dir.exists():
            self.logger.error(f"Data directory not found: {self.data_dir}")
            return []
        
        symbols = []
        excluded_files = {'nifty50', 'tcs_combined_news', 'processed'}
        
        for csv_file in self.data_dir.glob("*.csv"):
            symbol = csv_file.stem
            if symbol.lower() not in excluded_files:
                symbols.append(symbol)
        
        return sorted(symbols)
    
    def load_stock_data(self, symbol: str, cache: bool = True) -> pd.DataFrame:
        """
        Load stock data for a given symbol from CSV.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            cache: Whether to cache the loaded data
            
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        # Check cache first
        if cache and symbol in self._cache:
            return self._cache[symbol].copy()
        
        csv_path = self.data_dir / f"{symbol}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"No data file found for {symbol}")
        
        try:
            # Read CSV (skip first 3 rows which are headers)
            df = pd.read_csv(csv_path, skiprows=3)
            
            # Rename columns to standard format
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            
            # Convert Date to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Convert price columns to numeric
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove any rows with NaN values
            df = df.dropna()
            
            # Sort by date
            df = df.sort_values('Date').reset_index(drop=True)
            
            # Cache if requested
            if cache:
                self._cache[symbol] = df.copy()
            
            self.logger.info(f"Loaded {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading {symbol}: {e}")
            raise
    
    def get_latest_prices(self, symbols: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Get latest closing prices for given symbols.
        
        Args:
            symbols: List of symbols (if None, uses all available)
            
        Returns:
            Dict mapping symbol to latest close price
        """
        if symbols is None:
            symbols = self.symbols
        
        prices = {}
        for symbol in symbols:
            try:
                df = self.load_stock_data(symbol)
                if not df.empty:
                    prices[symbol] = float(df.iloc[-1]['Close'])
            except Exception as e:
                self.logger.warning(f"Could not get price for {symbol}: {e}")
                continue
        
        return prices
    
    def get_price_on_date(self, symbol: str, date: datetime) -> Optional[float]:
        """Get closing price for a symbol on a specific date."""
        try:
            df = self.load_stock_data(symbol)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Find closest date
            idx = (df['Date'] - date).abs().idxmin()
            return float(df.loc[idx, 'Close'])
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol} on {date}: {e}")
            return None
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get historical data for a symbol within date range.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (if None, uses earliest available)
            end_date: End date (if None, uses latest available)
            
        Returns:
            Filtered DataFrame
        """
        df = self.load_stock_data(symbol)
        
        if start_date:
            df = df[df['Date'] >= start_date]
        if end_date:
            df = df[df['Date'] <= end_date]
        
        return df.reset_index(drop=True)
    
    def calculate_returns(self, symbol: str, period: int = 1) -> pd.Series:
        """
        Calculate returns for a symbol.
        
        Args:
            symbol: Stock symbol
            period: Period for return calculation (1 = daily, 7 = weekly, etc.)
            
        Returns:
            Series of returns
        """
        df = self.load_stock_data(symbol)
        returns = df['Close'].pct_change(period).dropna()
        return returns
    
    def get_ohlcv_data(
        self, 
        symbol: str, 
        last_n_days: Optional[int] = None
    ) -> List[Dict]:
        """
        Get OHLCV data for candlestick charts.
        
        Args:
            symbol: Stock symbol
            last_n_days: Number of recent days (if None, returns all)
            
        Returns:
            List of dicts with date, open, high, low, close, volume
        """
        df = self.load_stock_data(symbol)
        
        if last_n_days:
            df = df.tail(last_n_days)
        
        ohlcv = []
        for _, row in df.iterrows():
            ohlcv.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        return ohlcv
    
    def get_portfolio_value(
        self, 
        positions: Dict[str, int],
        date: Optional[datetime] = None
    ) -> float:
        """
        Calculate total portfolio value on a given date.
        
        Args:
            positions: Dict of {symbol: quantity}
            date: Date for valuation (if None, uses latest)
            
        Returns:
            Total portfolio value
        """
        total_value = 0.0
        
        for symbol, quantity in positions.items():
            try:
                if date:
                    price = self.get_price_on_date(symbol, date)
                else:
                    df = self.load_stock_data(symbol)
                    price = float(df.iloc[-1]['Close'])
                
                if price:
                    total_value += quantity * price
                    
            except Exception as e:
                self.logger.warning(f"Error calculating value for {symbol}: {e}")
                continue
        
        return total_value
    
    def get_date_range(self, symbol: str) -> Tuple[datetime, datetime]:
        """Get the date range available for a symbol."""
        df = self.load_stock_data(symbol)
        return df['Date'].min(), df['Date'].max()
    
    def prepare_ml_features(self, symbol: str, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for ML models.
        
        Args:
            symbol: Stock symbol
            lookback: Number of days to use as features
            
        Returns:
            Tuple of (X features, y targets)
        """
        df = self.load_stock_data(symbol)
        
        # Calculate technical indicators
        df['Returns'] = df['Close'].pct_change()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Drop NaN values
        df = df.dropna()
        
        # Create sequences
        X, y = [], []
        for i in range(lookback, len(df)):
            X.append(df['Close'].iloc[i-lookback:i].values)
            y.append(df['Close'].iloc[i])
        
        return np.array(X), np.array(y)
    
    def get_correlation_matrix(self, symbols: List[str]) -> pd.DataFrame:
        """Calculate correlation matrix between stocks."""
        returns_data = {}
        
        for symbol in symbols:
            try:
                returns = self.calculate_returns(symbol)
                returns_data[symbol] = returns
            except Exception as e:
                self.logger.warning(f"Could not calculate returns for {symbol}: {e}")
                continue
        
        returns_df = pd.DataFrame(returns_data)
        return returns_df.corr()
    
    def get_summary_stats(self, symbol: str) -> Dict:
        """Get summary statistics for a stock."""
        df = self.load_stock_data(symbol)
        returns = self.calculate_returns(symbol)
        
        return {
            'symbol': symbol,
            'total_records': len(df),
            'start_date': df['Date'].min().strftime('%Y-%m-%d'),
            'end_date': df['Date'].max().strftime('%Y-%m-%d'),
            'latest_close': float(df.iloc[-1]['Close']),
            'mean_return': float(returns.mean()),
            'volatility': float(returns.std()),
            'min_price': float(df['Close'].min()),
            'max_price': float(df['Close'].max()),
            'avg_volume': float(df['Volume'].mean())
        }


# Global instance
_real_data_service = None


def get_real_data_service() -> RealDataService:
    """Get or create global RealDataService instance."""
    global _real_data_service
    if _real_data_service is None:
        _real_data_service = RealDataService()
    return _real_data_service
