"""
Services package for QuantFin ETF Portfolio System.

This package contains service modules for data processing and business logic.
"""

from .preprocessing import (
    DataPreprocessor,
    get_preprocessor,
    get_sector_data,
    get_stock_data,
    get_available_sectors,
    get_available_tickers
)

from .features import (
    FeatureEngineer,
    get_feature_engineer,
    compute_features,
    get_stock_features,
    get_sector_features,
    get_feature_summary
)

__all__ = [
    # Preprocessing
    'DataPreprocessor',
    'get_preprocessor',
    'get_sector_data',
    'get_stock_data',
    'get_available_sectors',
    'get_available_tickers',
    # Feature Engineering
    'FeatureEngineer',
    'get_feature_engineer',
    'compute_features',
    'get_stock_features',
    'get_sector_features',
    'get_feature_summary'
]
