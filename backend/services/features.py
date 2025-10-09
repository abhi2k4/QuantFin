"""
Feature Engineering Service for ETF Portfolio System

This module computes technical indicators and features for stock and sector data.
It provides comprehensive feature engineering capabilities including moving averages,
momentum indicators, volatility measures, and volume-based features.

Author: QuantFin Team
Date: 2025-10-09
"""

import logging
from typing import Dict, Optional, Tuple
import warnings

import pandas as pd
import numpy as np

from .preprocessing import get_preprocessor, DataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)


class FeatureEngineer:
    """
    Handles feature engineering for stock and sector data.
    
    This class computes technical indicators, momentum indicators, volatility measures,
    and other features useful for ML models and trading strategies.
    """
    
    def __init__(self, preprocessor: Optional[DataPreprocessor] = None):
        """
        Initialize the FeatureEngineer.
        
        Args:
            preprocessor (Optional[DataPreprocessor]): DataPreprocessor instance.
                                                       If None, uses global instance.
        """
        self.preprocessor = preprocessor or get_preprocessor()
        self.stock_features: Dict[str, pd.DataFrame] = {}
        self.sector_features: Dict[str, pd.DataFrame] = {}
        
        logger.info("FeatureEngineer initialized")
    
    def compute_sma(self, df: pd.DataFrame, column: str = 'Close', 
                    periods: list = [10, 50, 200]) -> pd.DataFrame:
        """
        Compute Simple Moving Averages.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute SMA on
            periods (list): List of periods for SMA calculation
        
        Returns:
            pd.DataFrame: DataFrame with SMA columns added
        """
        df_copy = df.copy()
        
        for period in periods:
            col_name = f'SMA_{period}'
            df_copy[col_name] = df_copy[column].rolling(window=period, min_periods=1).mean()
        
        return df_copy
    
    def compute_ema(self, df: pd.DataFrame, column: str = 'Close',
                    periods: list = [12, 26]) -> pd.DataFrame:
        """
        Compute Exponential Moving Averages.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute EMA on
            periods (list): List of periods for EMA calculation
        
        Returns:
            pd.DataFrame: DataFrame with EMA columns added
        """
        df_copy = df.copy()
        
        for period in periods:
            col_name = f'EMA_{period}'
            df_copy[col_name] = df_copy[column].ewm(span=period, adjust=False, min_periods=1).mean()
        
        return df_copy
    
    def compute_macd(self, df: pd.DataFrame, column: str = 'Close',
                     fast_period: int = 12, slow_period: int = 26, 
                     signal_period: int = 9) -> pd.DataFrame:
        """
        Compute MACD (Moving Average Convergence Divergence) and signal line.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute MACD on
            fast_period (int): Fast EMA period (default: 12)
            slow_period (int): Slow EMA period (default: 26)
            signal_period (int): Signal line period (default: 9)
        
        Returns:
            pd.DataFrame: DataFrame with MACD and MACD_signal columns added
        """
        df_copy = df.copy()
        
        # Calculate EMAs
        ema_fast = df_copy[column].ewm(span=fast_period, adjust=False, min_periods=1).mean()
        ema_slow = df_copy[column].ewm(span=slow_period, adjust=False, min_periods=1).mean()
        
        # MACD line
        df_copy['MACD'] = ema_fast - ema_slow
        
        # Signal line
        df_copy['MACD_signal'] = df_copy['MACD'].ewm(span=signal_period, adjust=False, min_periods=1).mean()
        
        # MACD histogram (optional but useful)
        df_copy['MACD_hist'] = df_copy['MACD'] - df_copy['MACD_signal']
        
        return df_copy
    
    def compute_rsi(self, df: pd.DataFrame, column: str = 'Close', 
                    period: int = 14) -> pd.DataFrame:
        """
        Compute Relative Strength Index (RSI).
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute RSI on
            period (int): RSI period (default: 14)
        
        Returns:
            pd.DataFrame: DataFrame with RSI column added
        """
        df_copy = df.copy()
        
        # Calculate price changes
        delta = df_copy[column].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period, min_periods=1).mean()
        avg_losses = losses.rolling(window=period, min_periods=1).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses.replace(0, np.finfo(float).eps)  # Avoid division by zero
        df_copy[f'RSI_{period}'] = 100 - (100 / (1 + rs))
        
        return df_copy
    
    def compute_bollinger_bands(self, df: pd.DataFrame, column: str = 'Close',
                                period: int = 20, num_std: float = 2.0) -> pd.DataFrame:
        """
        Compute Bollinger Bands.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute Bollinger Bands on
            period (int): Moving average period (default: 20)
            num_std (float): Number of standard deviations (default: 2.0)
        
        Returns:
            pd.DataFrame: DataFrame with BB_upper, BB_middle, BB_lower columns added
        """
        df_copy = df.copy()
        
        # Middle band (SMA)
        df_copy['BB_middle'] = df_copy[column].rolling(window=period, min_periods=1).mean()
        
        # Standard deviation
        rolling_std = df_copy[column].rolling(window=period, min_periods=1).std()
        
        # Upper and lower bands
        df_copy['BB_upper'] = df_copy['BB_middle'] + (rolling_std * num_std)
        df_copy['BB_lower'] = df_copy['BB_middle'] - (rolling_std * num_std)
        
        # Bollinger Band width (optional but useful)
        df_copy['BB_width'] = df_copy['BB_upper'] - df_copy['BB_lower']
        
        # %B indicator (position within bands)
        df_copy['BB_percent'] = (df_copy[column] - df_copy['BB_lower']) / (df_copy['BB_upper'] - df_copy['BB_lower'])
        
        return df_copy
    
    def compute_volatility(self, df: pd.DataFrame, column: str = 'Close',
                          period: int = 21) -> pd.DataFrame:
        """
        Compute rolling volatility (standard deviation of returns).
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute volatility on
            period (int): Rolling window period (default: 21)
        
        Returns:
            pd.DataFrame: DataFrame with volatility column added
        """
        df_copy = df.copy()
        
        # Calculate returns
        returns = df_copy[column].pct_change()
        
        # Calculate rolling volatility
        df_copy[f'vol_{period}'] = returns.rolling(window=period, min_periods=1).std()
        
        # Annualized volatility (assuming 252 trading days)
        df_copy[f'vol_{period}_annualized'] = df_copy[f'vol_{period}'] * np.sqrt(252)
        
        return df_copy
    
    def compute_volume_features(self, df: pd.DataFrame, period: int = 21) -> pd.DataFrame:
        """
        Compute volume-based features.
        
        Args:
            df (pd.DataFrame): DataFrame with volume data
            period (int): Rolling window period (default: 21)
        
        Returns:
            pd.DataFrame: DataFrame with volume features added
        """
        df_copy = df.copy()
        
        # Average volume
        df_copy[f'avg_volume_{period}'] = df_copy['Volume'].rolling(window=period, min_periods=1).mean()
        
        # Volume ratio (current volume vs average)
        df_copy['volume_ratio'] = df_copy['Volume'] / df_copy[f'avg_volume_{period}']
        
        # Volume change
        df_copy['volume_change'] = df_copy['Volume'].pct_change()
        
        return df_copy
    
    def compute_lagged_returns(self, df: pd.DataFrame, column: str = 'Close',
                              lags: list = [1, 5, 21]) -> pd.DataFrame:
        """
        Compute lagged returns.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute returns on
            lags (list): List of lag periods
        
        Returns:
            pd.DataFrame: DataFrame with lagged return columns added
        """
        df_copy = df.copy()
        
        # Calculate returns
        df_copy['returns'] = df_copy[column].pct_change()
        
        # Create lagged features
        for lag in lags:
            df_copy[f'lag_{lag}'] = df_copy['returns'].shift(lag)
        
        return df_copy
    
    def compute_price_momentum(self, df: pd.DataFrame, column: str = 'Close',
                              periods: list = [5, 10, 21]) -> pd.DataFrame:
        """
        Compute price momentum (rate of change).
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            column (str): Column name to compute momentum on
            periods (list): List of periods for momentum calculation
        
        Returns:
            pd.DataFrame: DataFrame with momentum columns added
        """
        df_copy = df.copy()
        
        for period in periods:
            df_copy[f'momentum_{period}'] = df_copy[column].pct_change(periods=period)
        
        return df_copy
    
    def compute_stock_features(self, ticker: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all features for a single stock.
        
        Args:
            ticker (str): Stock ticker symbol
            df (pd.DataFrame): DataFrame with OHLCV data
        
        Returns:
            pd.DataFrame: DataFrame with all computed features
        """
        logger.info(f"Computing features for {ticker}...")
        
        df_features = df.copy()
        
        # Moving averages
        df_features = self.compute_sma(df_features, periods=[10, 50, 200])
        df_features = self.compute_ema(df_features, periods=[12, 26])
        
        # MACD
        df_features = self.compute_macd(df_features)
        
        # RSI
        df_features = self.compute_rsi(df_features, period=14)
        
        # Bollinger Bands
        df_features = self.compute_bollinger_bands(df_features, period=20, num_std=2.0)
        
        # Volatility
        df_features = self.compute_volatility(df_features, period=21)
        
        # Volume features
        df_features = self.compute_volume_features(df_features, period=21)
        
        # Lagged returns
        df_features = self.compute_lagged_returns(df_features, lags=[1, 5, 21])
        
        # Price momentum
        df_features = self.compute_price_momentum(df_features, periods=[5, 10, 21])
        
        # Add ticker column
        df_features['Ticker'] = ticker
        
        logger.debug(f"Computed {len(df_features.columns)} features for {ticker}")
        
        return df_features
    
    def compute_all_stock_features(self) -> Dict[str, pd.DataFrame]:
        """
        Compute features for all stocks.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping ticker to features DataFrame
        """
        logger.info("=" * 60)
        logger.info("Starting feature computation for all stocks")
        logger.info("=" * 60)
        
        stock_data = self.preprocessor.stock_data
        
        if not stock_data:
            logger.warning("No stock data available. Loading data first...")
            self.preprocessor.load_all_stocks()
            stock_data = self.preprocessor.stock_data
        
        stock_features = {}
        total_stocks = len(stock_data)
        
        for idx, (ticker, df) in enumerate(stock_data.items(), 1):
            try:
                logger.info(f"[{idx}/{total_stocks}] Processing {ticker}...")
                features_df = self.compute_stock_features(ticker, df)
                
                # Handle missing values
                # Forward-fill first, then backward-fill, then fill remaining with 0
                features_df = features_df.fillna(method='ffill').fillna(method='bfill').fillna(0)
                
                stock_features[ticker] = features_df
                
            except Exception as e:
                logger.error(f"Error computing features for {ticker}: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully computed features for {len(stock_features)}/{total_stocks} stocks")
        
        self.stock_features = stock_features
        return stock_features
    
    def compute_sector_features(self, sector_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute features for a single sector.
        
        Args:
            sector_name (str): Sector name
            df (pd.DataFrame): DataFrame with sector OHLCV data
        
        Returns:
            pd.DataFrame: DataFrame with all computed features
        """
        logger.info(f"Computing features for sector: {sector_name}...")
        
        df_features = df.copy()
        
        # Calculate returns
        df_features['returns'] = df_features['Close'].pct_change()
        
        # Moving averages
        df_features = self.compute_sma(df_features, periods=[10, 50, 200])
        df_features = self.compute_ema(df_features, periods=[12, 26])
        
        # MACD
        df_features = self.compute_macd(df_features)
        
        # RSI
        df_features = self.compute_rsi(df_features, period=14)
        
        # Bollinger Bands
        df_features = self.compute_bollinger_bands(df_features, period=20, num_std=2.0)
        
        # Volatility
        df_features = self.compute_volatility(df_features, period=21)
        
        # Volume features
        df_features = self.compute_volume_features(df_features, period=21)
        
        # Lagged returns
        df_features = self.compute_lagged_returns(df_features, lags=[1, 5, 21])
        
        # Price momentum
        df_features = self.compute_price_momentum(df_features, periods=[5, 10, 21])
        
        # Add sector name
        df_features['Sector'] = sector_name
        
        logger.debug(f"Computed {len(df_features.columns)} features for sector {sector_name}")
        
        return df_features
    
    def compute_all_sector_features(self) -> Dict[str, pd.DataFrame]:
        """
        Compute features for all sectors.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sector name to features DataFrame
        """
        logger.info("=" * 60)
        logger.info("Starting feature computation for all sectors")
        logger.info("=" * 60)
        
        sector_data = self.preprocessor.sector_data
        
        if not sector_data:
            logger.warning("No sector data available. Aggregating sectors first...")
            self.preprocessor.aggregate_by_sector()
            sector_data = self.preprocessor.sector_data
        
        sector_features = {}
        total_sectors = len(sector_data)
        
        for idx, (sector, df) in enumerate(sector_data.items(), 1):
            try:
                logger.info(f"[{idx}/{total_sectors}] Processing {sector} sector...")
                features_df = self.compute_sector_features(sector, df)
                
                # Handle missing values
                features_df = features_df.fillna(method='ffill').fillna(method='bfill').fillna(0)
                
                sector_features[sector] = features_df
                
            except Exception as e:
                logger.error(f"Error computing features for {sector}: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully computed features for {len(sector_features)}/{total_sectors} sectors")
        
        self.sector_features = sector_features
        return sector_features
    
    def compute_all_features(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Compute features for both stocks and sectors.
        
        Returns:
            Dict containing:
            - 'stock_features': Dict mapping ticker to features DataFrame
            - 'sector_features': Dict mapping sector to features DataFrame
        """
        logger.info("=" * 60)
        logger.info("FEATURE ENGINEERING PIPELINE STARTED")
        logger.info("=" * 60)
        
        # Compute stock features
        stock_features = self.compute_all_stock_features()
        
        # Compute sector features
        sector_features = self.compute_all_sector_features()
        
        logger.info("=" * 60)
        logger.info("FEATURE ENGINEERING COMPLETED")
        logger.info(f"Stock features computed: {len(stock_features)}")
        logger.info(f"Sector features computed: {len(sector_features)}")
        logger.info("=" * 60)
        
        return {
            'stock_features': stock_features,
            'sector_features': sector_features
        }
    
    def get_feature_summary(self) -> Dict[str, any]:
        """
        Get a summary of computed features.
        
        Returns:
            Dict containing feature statistics and metadata
        """
        summary = {
            'num_stocks': len(self.stock_features),
            'num_sectors': len(self.sector_features),
            'stock_tickers': list(self.stock_features.keys()),
            'sector_names': list(self.sector_features.keys())
        }
        
        if self.stock_features:
            sample_ticker = list(self.stock_features.keys())[0]
            sample_df = self.stock_features[sample_ticker]
            summary['num_features'] = len(sample_df.columns)
            summary['feature_names'] = list(sample_df.columns)
            summary['date_range'] = {
                'start': sample_df['Date'].min().strftime('%Y-%m-%d'),
                'end': sample_df['Date'].max().strftime('%Y-%m-%d')
            }
        
        return summary
    
    def save_features(self, output_dir: str = None):
        """
        Save computed features to CSV files.
        
        Args:
            output_dir (str, optional): Directory to save features.
                                       Defaults to 'backend/data/features/'.
        """
        from pathlib import Path
        
        if output_dir is None:
            output_dir = self.preprocessor.data_dir / "features"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save stock features
        stock_dir = output_path / "stocks"
        stock_dir.mkdir(exist_ok=True)
        
        for ticker, df in self.stock_features.items():
            filepath = stock_dir / f"{ticker}_features.csv"
            df.to_csv(filepath, index=False)
            logger.debug(f"Saved features for {ticker}")
        
        # Save sector features
        sector_dir = output_path / "sectors"
        sector_dir.mkdir(exist_ok=True)
        
        for sector, df in self.sector_features.items():
            filepath = sector_dir / f"{sector}_features.csv"
            df.to_csv(filepath, index=False)
            logger.debug(f"Saved features for {sector}")
        
        logger.info(f"All features saved to {output_path}")


# Global feature engineer instance
_feature_engineer: Optional[FeatureEngineer] = None


def get_feature_engineer() -> FeatureEngineer:
    """
    Get or create a global FeatureEngineer instance.
    
    Returns:
        FeatureEngineer: Global feature engineer instance
    """
    global _feature_engineer
    
    if _feature_engineer is None:
        _feature_engineer = FeatureEngineer()
    
    return _feature_engineer


# Convenience functions
def compute_features() -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Compute features for all stocks and sectors.
    
    Returns:
        Dict containing stock_features and sector_features
    """
    engineer = get_feature_engineer()
    return engineer.compute_all_features()


def get_stock_features(ticker: str) -> Optional[pd.DataFrame]:
    """
    Get computed features for a specific stock.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        Optional[pd.DataFrame]: Features DataFrame or None if not computed
    """
    engineer = get_feature_engineer()
    
    if not engineer.stock_features:
        logger.info("Features not computed yet. Computing now...")
        engineer.compute_all_stock_features()
    
    return engineer.stock_features.get(ticker)


def get_sector_features(sector_name: str) -> Optional[pd.DataFrame]:
    """
    Get computed features for a specific sector.
    
    Args:
        sector_name (str): Sector name
    
    Returns:
        Optional[pd.DataFrame]: Features DataFrame or None if not computed
    """
    engineer = get_feature_engineer()
    
    if not engineer.sector_features:
        logger.info("Sector features not computed yet. Computing now...")
        engineer.compute_all_sector_features()
    
    return engineer.sector_features.get(sector_name)


def get_feature_summary() -> Dict[str, any]:
    """
    Get summary of computed features.
    
    Returns:
        Dict: Feature summary statistics
    """
    engineer = get_feature_engineer()
    return engineer.get_feature_summary()
