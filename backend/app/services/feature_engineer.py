"""
FeatureEngineer Module

Generates technical indicators and features for ML models and backtesting.
Supports both individual symbol and batch feature generation.

Author: QuantFin Team
Date: 2025-10-09
"""

from typing import Dict, List, Optional, Tuple
import logging

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from app.services.data_preprocessor import DataPreprocessor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class FeatureEngineer:
    """
    Engineers features and technical indicators for stock analysis.
    
    Features generated:
    - Returns (daily, log returns)
    - Rolling statistics (mean, volatility, min, max)
    - Momentum indicators
    - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
    - Volume indicators
    - Price position indicators
    
    Attributes:
        preprocessor (DataPreprocessor): Data loading component
        logger (logging.Logger): Logger instance
    """
    
    def __init__(self, preprocessor: DataPreprocessor):
        """
        Initialize FeatureEngineer.
        
        Args:
            preprocessor: DataPreprocessor instance for loading stock data
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> engineer = FeatureEngineer(preprocessor)
        """
        self.preprocessor = preprocessor
        self.logger = logging.getLogger(__name__)
        self.logger.info("FeatureEngineer initialized")
    
    def _calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily returns and log returns.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added return columns
        """
        # Daily returns
        df['returns'] = df['Close'].pct_change()
        
        # Log returns (more stable for statistical modeling)
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        return df
    
    def _calculate_rolling_stats(self, df: pd.DataFrame, windows: List[int] = [7, 14, 21, 30]) -> pd.DataFrame:
        """
        Calculate rolling statistics for different time windows.
        
        Args:
            df: DataFrame with Close prices
            windows: List of rolling window sizes
        
        Returns:
            DataFrame with rolling statistics columns
        """
        for window in windows:
            # Rolling mean
            df[f'rolling_mean_{window}'] = df['Close'].rolling(window=window).mean()
            
            # Rolling standard deviation (volatility)
            df[f'rolling_std_{window}'] = df['Close'].rolling(window=window).std()
            
            # Rolling min and max
            df[f'rolling_min_{window}'] = df['Close'].rolling(window=window).min()
            df[f'rolling_max_{window}'] = df['Close'].rolling(window=window).max()
            
            # Normalize price within rolling window
            df[f'price_position_{window}'] = (
                (df['Close'] - df[f'rolling_min_{window}']) / 
                (df[f'rolling_max_{window}'] - df[f'rolling_min_{window}'])
            )
        
        return df
    
    def _calculate_momentum(self, df: pd.DataFrame, periods: List[int] = [5, 10, 20]) -> pd.DataFrame:
        """
        Calculate momentum indicators.
        
        Args:
            df: DataFrame with Close prices
            periods: List of momentum periods
        
        Returns:
            DataFrame with momentum columns
        """
        for period in periods:
            # Price momentum (percentage change)
            df[f'momentum_{period}'] = df['Close'].pct_change(periods=period)
            
            # Rate of change
            df[f'roc_{period}'] = (df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)
        
        return df
    
    def _calculate_sma_ema(self, df: pd.DataFrame, windows: List[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        """
        Calculate Simple Moving Average (SMA) and Exponential Moving Average (EMA).
        
        Args:
            df: DataFrame with Close prices
            windows: List of window sizes
        
        Returns:
            DataFrame with SMA and EMA columns
        """
        for window in windows:
            # Simple Moving Average
            df[f'sma_{window}'] = df['Close'].rolling(window=window).mean()
            
            # Exponential Moving Average
            df[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()
            
            # Distance from moving average (normalized)
            df[f'dist_from_sma_{window}'] = (df['Close'] - df[f'sma_{window}']) / df[f'sma_{window}']
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            df: DataFrame with Close prices
            period: RSI period (default: 14)
        
        Returns:
            DataFrame with RSI column
        """
        # Calculate price changes
        delta = df['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI overbought/oversold indicators
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        
        return df
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            df: DataFrame with Close prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            DataFrame with MACD columns
        """
        # Calculate MACD line
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        
        # Calculate MACD histogram
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # MACD crossover signals
        df['macd_bullish'] = ((df['macd'] > df['macd_signal']) & 
                              (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)
        df['macd_bearish'] = ((df['macd'] < df['macd_signal']) & 
                              (df['macd'].shift(1) >= df['macd_signal'].shift(1))).astype(int)
        
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            df: DataFrame with Close prices
            window: Rolling window size
            num_std: Number of standard deviations
        
        Returns:
            DataFrame with Bollinger Bands columns
        """
        # Middle band (SMA)
        df['bb_middle'] = df['Close'].rolling(window=window).mean()
        
        # Standard deviation
        rolling_std = df['Close'].rolling(window=window).std()
        
        # Upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (rolling_std * num_std)
        df['bb_lower'] = df['bb_middle'] - (rolling_std * num_std)
        
        # Band width (volatility indicator)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_width_normalized'] = df['bb_width'] / df['bb_middle']
        
        # Position within bands
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate volume-based indicators.
        
        Args:
            df: DataFrame with Volume data
        
        Returns:
            DataFrame with volume indicator columns
        """
        # Volume moving averages
        df['volume_sma_5'] = df['Volume'].rolling(window=5).mean()
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        
        # Volume ratio
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
        
        # Volume momentum
        df['volume_momentum'] = df['Volume'].pct_change(periods=5)
        
        # On-Balance Volume (OBV)
        df['obv'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        return df
    
    def _calculate_price_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate price-based indicators.
        
        Args:
            df: DataFrame with OHLC data
        
        Returns:
            DataFrame with price indicator columns
        """
        # Daily range
        df['high_low_range'] = df['High'] - df['Low']
        df['high_low_pct'] = df['high_low_range'] / df['Close']
        
        # Close position within daily range
        df['close_position'] = (df['Close'] - df['Low']) / df['high_low_range']
        
        # Gap indicators
        df['gap'] = df['Open'] - df['Close'].shift(1)
        df['gap_pct'] = df['gap'] / df['Close'].shift(1)
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr_14'] = true_range.rolling(window=14).mean()
        
        return df
    
    def generate_features(
        self, 
        symbol: str, 
        lookback: int = 60,
        include_technical: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Generate comprehensive feature set for a stock symbol.
        
        Args:
            symbol: Stock symbol
            lookback: Minimum number of historical days required
            include_technical: Whether to include technical indicators
        
        Returns:
            DataFrame with all features, or None if insufficient data
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> engineer = FeatureEngineer(preprocessor)
            >>> features = engineer.generate_features('RELIANCE', lookback=60)
            >>> print(features.columns)
            >>> print(f"Features shape: {features.shape}")
        """
        try:
            # Load stock data
            df = self.preprocessor.get_stock_data(symbol)
            
            if df is None:
                self.logger.error(f"Symbol {symbol}: Failed to load data")
                return None
            
            if len(df) < lookback:
                self.logger.warning(
                    f"Symbol {symbol}: Insufficient data ({len(df)} rows, need {lookback})"
                )
                return None
            
            self.logger.info(f"Symbol {symbol}: Generating features for {len(df)} rows")
            
            # Keep original OHLCV columns
            features = df.copy()
            
            # Calculate returns
            features = self._calculate_returns(features)
            
            # Calculate rolling statistics
            features = self._calculate_rolling_stats(features)
            
            # Calculate momentum
            features = self._calculate_momentum(features)
            
            if include_technical:
                # Calculate moving averages
                features = self._calculate_sma_ema(features)
                
                # Calculate RSI
                features = self._calculate_rsi(features)
                
                # Calculate MACD
                features = self._calculate_macd(features)
                
                # Calculate Bollinger Bands
                features = self._calculate_bollinger_bands(features)
                
                # Calculate volume indicators
                features = self._calculate_volume_indicators(features)
                
                # Calculate price indicators
                features = self._calculate_price_indicators(features)
            
            # Drop rows with NaN values (due to rolling calculations)
            initial_rows = len(features)
            features = features.dropna()
            dropped_rows = initial_rows - len(features)
            
            if dropped_rows > 0:
                self.logger.info(f"Symbol {symbol}: Dropped {dropped_rows} rows with NaN values")
            
            if len(features) < lookback:
                self.logger.warning(
                    f"Symbol {symbol}: After feature generation, only {len(features)} rows remain"
                )
                return None
            
            self.logger.info(f"Symbol {symbol}: Generated {len(features.columns)} features")
            
            return features
        
        except Exception as e:
            self.logger.error(f"Symbol {symbol}: Feature generation failed: {str(e)}")
            return None
    
    def generate_features_all(
        self, 
        symbols: List[str],
        lookback: int = 60,
        include_technical: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate features for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            lookback: Minimum number of historical days required
            include_technical: Whether to include technical indicators
        
        Returns:
            Dictionary mapping symbol to feature DataFrame (excludes failures)
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> engineer = FeatureEngineer(preprocessor)
            >>> symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
            >>> all_features = engineer.generate_features_all(symbols)
            >>> print(f"Generated features for {len(all_features)} symbols")
        """
        result = {}
        
        self.logger.info(f"Generating features for {len(symbols)} symbols")
        
        for symbol in symbols:
            features = self.generate_features(symbol, lookback, include_technical)
            if features is not None:
                result[symbol] = features
        
        self.logger.info(
            f"Successfully generated features for {len(result)} out of {len(symbols)} symbols"
        )
        
        return result
    
    def create_features(self, symbols: List[str]) -> Optional[pd.DataFrame]:
        """
        Create combined feature DataFrame for multiple symbols (alias for compatibility).
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Combined DataFrame with features for all symbols
        
        Note:
            This method concatenates features from multiple symbols into one DataFrame
            with a 'symbol' column for identification.
        """
        all_features = self.generate_features_all(symbols)
        
        if not all_features:
            self.logger.error("No features generated for any symbol")
            return None
        
        # Combine all features with symbol identifier
        combined = []
        for symbol, features in all_features.items():
            features_copy = features.copy()
            features_copy['symbol'] = symbol
            combined.append(features_copy)
        
        if not combined:
            return None
        
        result = pd.concat(combined, axis=0)
        self.logger.info(f"Combined features shape: {result.shape}")
        
        return result
    
    def normalize_features(
        self,
        df: pd.DataFrame,
        exclude_columns: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, StandardScaler]:
        """
        Normalize numerical features using StandardScaler.
        
        Args:
            df: DataFrame with features
            exclude_columns: Columns to exclude from normalization
        
        Returns:
            Tuple of (normalized DataFrame, fitted scaler)
        
        Example:
            >>> features = engineer.generate_features('RELIANCE')
            >>> normalized, scaler = engineer.normalize_features(
            ...     features, 
            ...     exclude_columns=['Close', 'Volume']
            ... )
        """
        if exclude_columns is None:
            exclude_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
        
        df_normalized = df.copy()
        
        # Select columns to normalize (all except excluded)
        cols_to_normalize = [col for col in df.columns if col not in exclude_columns]
        
        if not cols_to_normalize:
            self.logger.warning("No columns to normalize")
            return df_normalized, None
        
        # Replace inf values with NaN, then drop
        df_normalized[cols_to_normalize] = df_normalized[cols_to_normalize].replace([np.inf, -np.inf], np.nan)
        
        # Check for remaining NaN or inf
        if df_normalized[cols_to_normalize].isna().any().any():
            self.logger.warning("Found NaN values in features, filling with column mean")
            df_normalized[cols_to_normalize] = df_normalized[cols_to_normalize].fillna(
                df_normalized[cols_to_normalize].mean()
            )
        
        # Fit scaler and transform
        scaler = StandardScaler()
        df_normalized[cols_to_normalize] = scaler.fit_transform(df_normalized[cols_to_normalize])
        
        self.logger.info(f"Normalized {len(cols_to_normalize)} feature columns")
        
        return df_normalized, scaler


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("FeatureEngineer Testing")
    print("="*60)
    
    # Initialize
    preprocessor = DataPreprocessor()
    engineer = FeatureEngineer(preprocessor)
    
    # Test single symbol feature generation
    print("\n" + "="*60)
    print("Single Symbol Feature Generation")
    print("="*60)
    
    symbol = 'RELIANCE'
    features = engineer.generate_features(symbol, lookback=60)
    
    if features is not None:
        print(f"\n{symbol} Features:")
        print(f"  Shape: {features.shape}")
        print(f"  Columns: {len(features.columns)}")
        print(f"  Date range: {features.index.min()} to {features.index.max()}")
        print(f"\nSample feature columns:")
        print(f"  {list(features.columns[:10])}")
        print(f"\nLatest values:")
        print(features.iloc[-1][['Close', 'returns', 'rsi', 'macd', 'bb_position']].to_dict())
    
    # Test multiple symbols
    print("\n" + "="*60)
    print("Multiple Symbols Feature Generation")
    print("="*60)
    
    test_symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
    all_features = engineer.generate_features_all(test_symbols)
    
    print(f"\nGenerated features for {len(all_features)} symbols:")
    for sym, feat in all_features.items():
        print(f"  {sym}: {feat.shape}")
    
    # Test normalization
    print("\n" + "="*60)
    print("Feature Normalization")
    print("="*60)
    
    if features is not None:
        normalized, scaler = engineer.normalize_features(features)
        print(f"Normalized features shape: {normalized.shape}")
        print(f"Scaler mean: {scaler.mean_[:5]}")
        print(f"Scaler scale: {scaler.scale_[:5]}")
