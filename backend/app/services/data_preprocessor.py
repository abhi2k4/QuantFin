"""
DataPreprocessor Module

Handles loading, cleaning, and validating historical stock data from CSV files.
Provides caching for performance and robust error handling.

Author: QuantFin Team
Date: 2025-10-09
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

import pandas as pd
import numpy as np


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DataPreprocessor:
    """
    Preprocesses and manages historical stock data from CSV files.
    
    Features:
    - Loads CSV files for stock symbols
    - Handles missing files and data quality issues
    - Validates required columns
    - Caches loaded data for performance
    - Provides clean, sorted DataFrames
    
    Attributes:
        data_dir (Path): Directory containing CSV files
        required_columns (List[str]): Required column names
        logger (logging.Logger): Logger instance
    """
    
    REQUIRED_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize DataPreprocessor.
        
        Args:
            data_dir: Path to directory containing stock CSV files.
                     Defaults to backend/data/ if not specified.
        """
        if data_dir is None:
            # Default to backend/data/ directory
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, pd.DataFrame] = {}
        self.logger = logging.getLogger(__name__)
        
        # Validate data directory exists
        if not self.data_dir.exists():
            self.logger.warning(f"Data directory does not exist: {self.data_dir}")
        else:
            self.logger.info(f"DataPreprocessor initialized with data_dir: {self.data_dir}")
    
    def get_all_symbols(self) -> List[str]:
        """
        Get list of all available stock symbols from CSV files.
        
        Returns:
            List of stock symbols (CSV filenames without extension).
            Excludes special files like 'nifty50.csv' and 'tcs_combined_news.csv'.
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> symbols = preprocessor.get_all_symbols()
            >>> print(symbols[:5])
            ['ADANIENT', 'ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO']
        """
        if not self.data_dir.exists():
            self.logger.error(f"Data directory not found: {self.data_dir}")
            return []
        
        symbols = []
        excluded_files = {'nifty50', 'tcs_combined_news', 'processed'}
        
        for csv_file in self.data_dir.glob("*.csv"):
            symbol = csv_file.stem
            if symbol.lower() not in excluded_files:
                symbols.append(symbol)
        
        self.logger.info(f"Found {len(symbols)} stock symbols")
        return sorted(symbols)
    
    def _validate_columns(self, df: pd.DataFrame, symbol: str) -> bool:
        """
        Validate that DataFrame contains all required columns.
        
        Args:
            df: DataFrame to validate
            symbol: Stock symbol (for logging)
        
        Returns:
            True if all required columns present, False otherwise
        """
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_cols:
            self.logger.error(f"Symbol {symbol}: Missing required columns: {missing_cols}")
            return False
        
        return True
    
    def _handle_multi_row_header(self, csv_path: Path) -> pd.DataFrame:
        """
        Handle CSV files with potential multi-row headers.
        
        Args:
            csv_path: Path to CSV file
        
        Returns:
            DataFrame with proper single-row header
        """
        try:
            # Our CSVs have a 3-row header structure:
            # Row 0: Price,Close,High,Low,Open,Volume (actual column names)
            # Row 1: Ticker,RELIANCE.NS,... (ticker info)
            # Row 2: Date,,,, (empty row)
            # Row 3+: Actual data with date in first column
            
            # Read with header from row 0
            df = pd.read_csv(csv_path, header=0)
            
            # Skip the ticker and empty rows (rows 1 and 2 become data)
            # They'll have non-numeric values, so we'll filter them
            df = df[df.iloc[:, 0].apply(lambda x: not isinstance(x, str) or x.replace('-', '').replace('/', '').isdigit() or '-' in str(x)[:10])]
            
            # Rename 'Price' column to 'Date' (first column is actually dates)
            if 'Price' in df.columns:
                df = df.rename(columns={'Price': 'Date'})
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error reading {csv_path.name}: {str(e)}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Clean and prepare DataFrame for analysis.
        
        Args:
            df: Raw DataFrame
            symbol: Stock symbol (for logging)
        
        Returns:
            Cleaned DataFrame with Date index, sorted ascending
        """
        # Convert Date column to datetime
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        except Exception as e:
            self.logger.error(f"Symbol {symbol}: Failed to parse Date column: {str(e)}")
            raise
        
        # Remove rows with invalid dates
        invalid_dates = df['Date'].isna().sum()
        if invalid_dates > 0:
            self.logger.warning(f"Symbol {symbol}: Removing {invalid_dates} rows with invalid dates")
            df = df.dropna(subset=['Date'])
        
        # Sort by date ascending
        df = df.sort_values('Date')
        
        # Set Date as index
        df = df.set_index('Date')
        
        # Handle missing values in OHLCV columns
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Check for missing values
        missing_counts = df[numeric_cols].isna().sum()
        if missing_counts.sum() > 0:
            self.logger.warning(f"Symbol {symbol}: Missing values detected:")
            for col, count in missing_counts.items():
                if count > 0:
                    self.logger.warning(f"  {col}: {count} missing values")
            
            # Forward fill then backward fill for price data
            df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
            
            # If still have NaN (first/last rows), drop them
            remaining_na = df[numeric_cols].isna().sum().sum()
            if remaining_na > 0:
                self.logger.warning(f"Symbol {symbol}: Dropping {remaining_na} remaining NaN values")
                df = df.dropna(subset=numeric_cols)
        
        # Ensure numeric types
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove any remaining NaN rows after type conversion
        df = df.dropna(subset=numeric_cols)
        
        # Validate data quality
        if len(df) == 0:
            raise ValueError(f"Symbol {symbol}: No valid data after cleaning")
        
        if len(df) < 100:
            self.logger.warning(f"Symbol {symbol}: Only {len(df)} rows - may be insufficient for analysis")
        
        # Remove duplicates (keep last occurrence)
        duplicates = df.index.duplicated(keep='last').sum()
        if duplicates > 0:
            self.logger.warning(f"Symbol {symbol}: Removing {duplicates} duplicate dates")
            df = df[~df.index.duplicated(keep='last')]
        
        self.logger.info(f"Symbol {symbol}: Loaded {len(df)} clean rows from {df.index.min()} to {df.index.max()}")
        
        return df
    
    def get_stock_data(self, symbol: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Load and return cleaned stock data for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            use_cache: Whether to use cached data if available (default: True)
        
        Returns:
            DataFrame with Date index and OHLCV columns, or None if loading fails
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> df = preprocessor.get_stock_data('RELIANCE')
            >>> print(df.columns)
            Index(['Open', 'High', 'Low', 'Close', 'Volume'], dtype='object')
            >>> print(df.index.name)
            Date
        """
        # Check cache first
        if use_cache and symbol in self._cache:
            self.logger.debug(f"Symbol {symbol}: Returning cached data")
            return self._cache[symbol].copy()
        
        # Construct file path
        csv_path = self.data_dir / f"{symbol}.csv"
        
        if not csv_path.exists():
            self.logger.error(f"Symbol {symbol}: CSV file not found at {csv_path}")
            return None
        
        try:
            # Load CSV
            df = self._handle_multi_row_header(csv_path)
            
            # Validate columns
            if not self._validate_columns(df, symbol):
                return None
            
            # Clean data
            df = self._clean_dataframe(df, symbol)
            
            # Cache the result
            self._cache[symbol] = df.copy()
            
            return df
        
        except Exception as e:
            self.logger.error(f"Symbol {symbol}: Failed to load data: {str(e)}")
            return None
    
    def load_multiple_symbols(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Load data for multiple symbols at once.
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbol to DataFrame (excludes failed loads)
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> data = preprocessor.load_multiple_symbols(['RELIANCE', 'TCS', 'HDFCBANK'])
            >>> print(f"Loaded {len(data)} symbols")
            Loaded 3 symbols
        """
        result = {}
        
        for symbol in symbols:
            df = self.get_stock_data(symbol)
            if df is not None:
                result[symbol] = df
        
        self.logger.info(f"Successfully loaded {len(result)} out of {len(symbols)} symbols")
        return result
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cached data.
        
        Args:
            symbol: Specific symbol to clear, or None to clear all cache
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> preprocessor.clear_cache('RELIANCE')  # Clear specific symbol
            >>> preprocessor.clear_cache()  # Clear all cache
        """
        if symbol is None:
            self._cache.clear()
            self.logger.info("Cleared all cached data")
        elif symbol in self._cache:
            del self._cache[symbol]
            self.logger.info(f"Cleared cache for {symbol}")
    
    def get_date_range(self, symbol: str) -> Optional[tuple]:
        """
        Get the date range for a symbol's data.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Tuple of (start_date, end_date) or None if data not available
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> start, end = preprocessor.get_date_range('RELIANCE')
            >>> print(f"Data from {start} to {end}")
        """
        df = self.get_stock_data(symbol)
        if df is None or len(df) == 0:
            return None
        
        return (df.index.min(), df.index.max())
    
    def get_stock_list(self) -> List[str]:
        """
        Alias for get_all_symbols() for backwards compatibility.
        
        Returns:
            List of stock symbols
        """
        return self.get_all_symbols()


# Example usage and testing
if __name__ == "__main__":
    # Initialize preprocessor
    preprocessor = DataPreprocessor()
    
    # Get all available symbols
    print("\n" + "="*60)
    print("Available Symbols")
    print("="*60)
    symbols = preprocessor.get_all_symbols()
    print(f"Found {len(symbols)} symbols")
    print(f"First 10: {symbols[:10]}")
    
    # Test loading a few symbols
    print("\n" + "="*60)
    print("Loading Sample Data")
    print("="*60)
    
    test_symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
    for symbol in test_symbols:
        df = preprocessor.get_stock_data(symbol)
        if df is not None:
            print(f"\n{symbol}:")
            print(f"  Rows: {len(df)}")
            print(f"  Date range: {df.index.min()} to {df.index.max()}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Latest close: {df['Close'].iloc[-1]:.2f}")
        else:
            print(f"\n{symbol}: Failed to load")
    
    # Test caching
    print("\n" + "="*60)
    print("Testing Cache")
    print("="*60)
    
    import time
    
    # First load (no cache)
    start = time.time()
    df1 = preprocessor.get_stock_data('RELIANCE', use_cache=False)
    time1 = time.time() - start
    
    # Second load (with cache)
    start = time.time()
    df2 = preprocessor.get_stock_data('RELIANCE', use_cache=True)
    time2 = time.time() - start
    
    print(f"First load (no cache): {time1*1000:.2f}ms")
    print(f"Second load (with cache): {time2*1000:.2f}ms")
    print(f"Speedup: {time1/time2:.1f}x")
