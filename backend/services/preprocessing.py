"""
Data Preprocessing Service for ETF Portfolio System

This module handles the ingestion, cleaning, and preprocessing of stock market data
from CSV files. It provides utilities for loading sector-wise data, handling missing
values, and validating data integrity.

Author: QuantFin Team
Date: 2025-10-09
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define required columns for stock data
REQUIRED_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

# Sector mapping: Map stock tickers to their respective sectors
SECTOR_MAPPING = {
    'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK'],
    'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM'],
    'Pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB'],
    'Auto': ['MARUTI', 'TATAMOTORS', 'BAJAJ-AUTO', 'EICHERMOT', 'HEROMOTOCO', 'M&M'],
    'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'TATACONSUM', 'TITAN'],
    'Energy': ['RELIANCE', 'ONGC', 'BPCL', 'COALINDIA', 'NTPC', 'POWERGRID'],
    'Metals': ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'COALINDIA'],
    'Cement': ['ULTRACEMCO', 'SHREECEM', 'GRASIM'],
    'Telecom': ['BHARTIARTL'],
    'Conglomerate': ['RELIANCE', 'LT', 'ADANIENT', 'ADANIPORTS'],
    'Financial_Services': ['BAJFINANCE', 'BAJAJFINSV', 'SBILIFE'],
    'Agriculture': ['UPL'],
    'Paints': ['ASIANPAINT']
}


class DataPreprocessor:
    """
    Handles data preprocessing operations for stock market data.
    
    This class provides methods to load, clean, validate, and merge stock data
    from multiple CSV files organized by sectors.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the DataPreprocessor.
        
        Args:
            data_dir (str, optional): Path to the directory containing CSV files.
                                     Defaults to 'backend/data/'.
        """
        if data_dir is None:
            # Get the backend directory path
            current_file = Path(__file__).resolve()
            backend_dir = current_file.parent.parent
            data_dir = backend_dir / "data"
        
        self.data_dir = Path(data_dir)
        self.sector_data: Dict[str, pd.DataFrame] = {}
        self.stock_data: Dict[str, pd.DataFrame] = {}
        
        logger.info(f"DataPreprocessor initialized with data directory: {self.data_dir}")
    
    def _validate_columns(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Validate that the DataFrame contains all required columns.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            filename (str): Name of the file being validated (for logging)
        
        Returns:
            bool: True if all required columns are present, False otherwise
        """
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"{filename}: Missing columns {missing_columns}")
            return False
        
        return True
    
    def _clean_dataframe(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """
        Clean and preprocess a single DataFrame.
        
        Operations performed:
        1. Convert Date column to datetime
        2. Sort by date
        3. Remove duplicates
        4. Handle missing values (forward-fill up to 5 days)
        5. Remove rows with remaining NaN values
        6. Reset index
        
        Args:
            df (pd.DataFrame): Raw DataFrame to clean
            filename (str): Name of the file being processed (for logging)
        
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Convert Date column to datetime
        try:
            df_clean['Date'] = pd.to_datetime(df_clean['Date'])
        except Exception as e:
            logger.error(f"{filename}: Error converting Date column: {e}")
            raise
        
        # Sort by date
        df_clean = df_clean.sort_values('Date').reset_index(drop=True)
        
        # Remove duplicate dates (keep the first occurrence)
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['Date'], keep='first')
        duplicates_removed = initial_rows - len(df_clean)
        
        if duplicates_removed > 0:
            logger.info(f"{filename}: Removed {duplicates_removed} duplicate date entries")
        
        # Count missing values before cleaning
        missing_before = df_clean[REQUIRED_COLUMNS].isnull().sum().sum()
        
        # Handle missing values: forward-fill up to 5 days
        df_clean[REQUIRED_COLUMNS[1:]] = df_clean[REQUIRED_COLUMNS[1:]].fillna(method='ffill', limit=5)
        
        # Drop rows that still have missing values after forward-fill
        rows_before = len(df_clean)
        df_clean = df_clean.dropna(subset=REQUIRED_COLUMNS)
        rows_dropped = rows_before - len(df_clean)
        
        missing_after = df_clean[REQUIRED_COLUMNS].isnull().sum().sum()
        
        if missing_before > 0:
            logger.info(
                f"{filename}: Handled {missing_before} missing values, "
                f"dropped {rows_dropped} rows with remaining NaN values"
            )
        
        # Reset index after dropping rows
        df_clean = df_clean.reset_index(drop=True)
        
        # Ensure numeric columns are of correct type
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Validate data integrity (e.g., High >= Low, High >= Open, High >= Close)
        invalid_rows = df_clean[
            (df_clean['High'] < df_clean['Low']) |
            (df_clean['High'] < df_clean['Open']) |
            (df_clean['High'] < df_clean['Close']) |
            (df_clean['Low'] > df_clean['Open']) |
            (df_clean['Low'] > df_clean['Close'])
        ]
        
        if len(invalid_rows) > 0:
            logger.warning(f"{filename}: Found {len(invalid_rows)} rows with invalid OHLC data")
            df_clean = df_clean.drop(invalid_rows.index).reset_index(drop=True)
        
        logger.info(f"{filename}: Cleaned successfully. Final shape: {df_clean.shape}")
        
        return df_clean
    
    def load_single_csv(self, filepath: Path) -> Optional[pd.DataFrame]:
        """
        Load and clean a single CSV file.
        
        Args:
            filepath (Path): Path to the CSV file
        
        Returns:
            Optional[pd.DataFrame]: Cleaned DataFrame, or None if loading fails
        """
        filename = filepath.name
        
        try:
            # Read CSV file
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {filename} with shape {df.shape}")
            
            # Validate columns
            if not self._validate_columns(df, filename):
                logger.error(f"{filename}: Skipping due to missing required columns")
                return None
            
            # Clean the DataFrame
            df_clean = self._clean_dataframe(df, filename)
            
            return df_clean
            
        except FileNotFoundError:
            logger.error(f"{filename}: File not found at {filepath}")
            return None
        except pd.errors.EmptyDataError:
            logger.error(f"{filename}: File is empty")
            return None
        except Exception as e:
            logger.error(f"{filename}: Unexpected error during loading: {e}")
            return None
    
    def load_all_stocks(self) -> Dict[str, pd.DataFrame]:
        """
        Load all stock CSV files from the data directory.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping stock ticker to DataFrame
        """
        logger.info("Starting to load all stock data...")
        
        if not self.data_dir.exists():
            logger.error(f"Data directory does not exist: {self.data_dir}")
            return {}
        
        # Get all CSV files in the data directory (excluding processed subfolder)
        csv_files = [f for f in self.data_dir.glob("*.csv")]
        
        if not csv_files:
            logger.warning(f"No CSV files found in {self.data_dir}")
            return {}
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        stock_data = {}
        successful_loads = 0
        failed_loads = 0
        
        for csv_file in csv_files:
            # Extract stock ticker from filename (e.g., 'TCS.csv' -> 'TCS')
            ticker = csv_file.stem
            
            df = self.load_single_csv(csv_file)
            
            if df is not None:
                stock_data[ticker] = df
                successful_loads += 1
            else:
                failed_loads += 1
        
        logger.info(
            f"Finished loading stock data. "
            f"Successful: {successful_loads}, Failed: {failed_loads}"
        )
        
        self.stock_data = stock_data
        return stock_data
    
    def aggregate_by_sector(self) -> Dict[str, pd.DataFrame]:
        """
        Aggregate stock data by sectors.
        
        This method combines individual stock data into sector-level DataFrames
        by calculating weighted averages based on volume.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sector name to aggregated DataFrame
        """
        if not self.stock_data:
            logger.warning("No stock data loaded. Call load_all_stocks() first.")
            return {}
        
        logger.info("Aggregating stock data by sectors...")
        
        sector_data = {}
        
        for sector, tickers in SECTOR_MAPPING.items():
            # Get available data for this sector
            sector_dfs = []
            available_tickers = []
            
            for ticker in tickers:
                if ticker in self.stock_data:
                    df = self.stock_data[ticker].copy()
                    df['Ticker'] = ticker
                    sector_dfs.append(df)
                    available_tickers.append(ticker)
            
            if not sector_dfs:
                logger.warning(f"No data available for sector: {sector}")
                continue
            
            # Merge all stock data for this sector
            combined_df = pd.concat(sector_dfs, ignore_index=True)
            
            # Calculate volume-weighted average for OHLC
            sector_agg = combined_df.groupby('Date').apply(
                lambda x: pd.Series({
                    'Open': np.average(x['Open'], weights=x['Volume']),
                    'High': np.average(x['High'], weights=x['Volume']),
                    'Low': np.average(x['Low'], weights=x['Volume']),
                    'Close': np.average(x['Close'], weights=x['Volume']),
                    'Volume': x['Volume'].sum(),
                    'StockCount': len(x)
                })
            ).reset_index()
            
            # Sort by date
            sector_agg = sector_agg.sort_values('Date').reset_index(drop=True)
            
            sector_data[sector] = sector_agg
            
            logger.info(
                f"Sector '{sector}': Aggregated {len(available_tickers)} stocks, "
                f"Final shape: {sector_agg.shape}"
            )
        
        self.sector_data = sector_data
        return sector_data
    
    def get_sector_data(self, sector_name: str) -> Optional[pd.DataFrame]:
        """
        Retrieve data for a specific sector.
        
        Args:
            sector_name (str): Name of the sector (e.g., 'Banking', 'IT')
        
        Returns:
            Optional[pd.DataFrame]: DataFrame containing sector data, or None if not found
        """
        if not self.sector_data:
            logger.info("Sector data not loaded. Loading now...")
            self.load_all_stocks()
            self.aggregate_by_sector()
        
        if sector_name not in self.sector_data:
            logger.warning(f"Sector '{sector_name}' not found. Available sectors: {list(self.sector_data.keys())}")
            return None
        
        return self.sector_data[sector_name].copy()
    
    def get_stock_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Retrieve data for a specific stock ticker.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'TCS', 'RELIANCE')
        
        Returns:
            Optional[pd.DataFrame]: DataFrame containing stock data, or None if not found
        """
        if not self.stock_data:
            logger.info("Stock data not loaded. Loading now...")
            self.load_all_stocks()
        
        if ticker not in self.stock_data:
            logger.warning(f"Ticker '{ticker}' not found. Available tickers: {list(self.stock_data.keys())[:10]}...")
            return None
        
        return self.stock_data[ticker].copy()
    
    def get_available_sectors(self) -> List[str]:
        """
        Get list of available sectors.
        
        Returns:
            List[str]: List of sector names
        """
        if not self.sector_data:
            return list(SECTOR_MAPPING.keys())
        
        return list(self.sector_data.keys())
    
    def get_available_tickers(self) -> List[str]:
        """
        Get list of available stock tickers.
        
        Returns:
            List[str]: List of stock ticker symbols
        """
        if not self.stock_data:
            # Return expected tickers from sector mapping
            return [ticker for tickers in SECTOR_MAPPING.values() for ticker in tickers]
        
        return list(self.stock_data.keys())
    
    def get_date_range(self) -> Optional[tuple]:
        """
        Get the overall date range of the loaded data.
        
        Returns:
            Optional[tuple]: (start_date, end_date) or None if no data is loaded
        """
        if not self.stock_data:
            return None
        
        all_dates = []
        for df in self.stock_data.values():
            all_dates.extend([df['Date'].min(), df['Date'].max()])
        
        return (min(all_dates), max(all_dates))
    
    def save_processed_data(self, output_dir: str = None):
        """
        Save processed sector data to CSV files.
        
        Args:
            output_dir (str, optional): Directory to save processed data.
                                       Defaults to 'backend/data/processed/'.
        """
        if not self.sector_data:
            logger.warning("No sector data to save. Load and aggregate data first.")
            return
        
        if output_dir is None:
            output_dir = self.data_dir / "processed"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for sector, df in self.sector_data.items():
            filepath = output_path / f"{sector.lower()}.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"Saved {sector} data to {filepath}")
        
        logger.info(f"All processed data saved to {output_path}")


# Global preprocessor instance
_preprocessor: Optional[DataPreprocessor] = None


def get_preprocessor() -> DataPreprocessor:
    """
    Get or create a global DataPreprocessor instance.
    
    Returns:
        DataPreprocessor: Global preprocessor instance
    """
    global _preprocessor
    
    if _preprocessor is None:
        _preprocessor = DataPreprocessor()
        # Load data on first access
        _preprocessor.load_all_stocks()
        _preprocessor.aggregate_by_sector()
    
    return _preprocessor


# Convenience functions
def get_sector_data(sector_name: str) -> Optional[pd.DataFrame]:
    """
    Get data for a specific sector.
    
    Args:
        sector_name (str): Name of the sector
    
    Returns:
        Optional[pd.DataFrame]: Sector data or None
    """
    preprocessor = get_preprocessor()
    return preprocessor.get_sector_data(sector_name)


def get_stock_data(ticker: str) -> Optional[pd.DataFrame]:
    """
    Get data for a specific stock ticker.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        Optional[pd.DataFrame]: Stock data or None
    """
    preprocessor = get_preprocessor()
    return preprocessor.get_stock_data(ticker)


def get_available_sectors() -> List[str]:
    """
    Get list of available sectors.
    
    Returns:
        List[str]: List of sector names
    """
    preprocessor = get_preprocessor()
    return preprocessor.get_available_sectors()


def get_available_tickers() -> List[str]:
    """
    Get list of available stock tickers.
    
    Returns:
        List[str]: List of ticker symbols
    """
    preprocessor = get_preprocessor()
    return preprocessor.get_available_tickers()
