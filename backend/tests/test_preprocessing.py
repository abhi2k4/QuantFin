"""
Unit tests for data preprocessing service.

This module contains tests for the DataPreprocessor class and related functions.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from services.preprocessing import (
    DataPreprocessor,
    get_sector_data,
    get_stock_data,
    get_available_sectors,
    get_available_tickers,
    REQUIRED_COLUMNS
)


class TestDataPreprocessor:
    """Test suite for DataPreprocessor class."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing."""
        data = {
            'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
            'High': [101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0],
            'Low': [99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0],
            'Close': [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5, 108.5, 109.5],
            'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def temp_data_dir(self, sample_csv_data):
        """Create temporary directory with sample CSV files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample CSV files
            sample_csv_data.to_csv(os.path.join(tmpdir, 'TCS.csv'), index=False)
            sample_csv_data.to_csv(os.path.join(tmpdir, 'INFY.csv'), index=False)
            yield tmpdir
    
    def test_preprocessor_initialization(self, temp_data_dir):
        """Test DataPreprocessor initialization."""
        preprocessor = DataPreprocessor(data_dir=temp_data_dir)
        assert preprocessor.data_dir == Path(temp_data_dir)
        assert preprocessor.sector_data == {}
        assert preprocessor.stock_data == {}
    
    def test_validate_columns(self, temp_data_dir, sample_csv_data):
        """Test column validation."""
        preprocessor = DataPreprocessor(data_dir=temp_data_dir)
        
        # Valid DataFrame
        assert preprocessor._validate_columns(sample_csv_data, 'test.csv') is True
        
        # Missing columns
        invalid_df = sample_csv_data.drop(columns=['Volume'])
        assert preprocessor._validate_columns(invalid_df, 'test.csv') is False
    
    def test_clean_dataframe(self, temp_data_dir, sample_csv_data):
        """Test DataFrame cleaning."""
        preprocessor = DataPreprocessor(data_dir=temp_data_dir)
        
        # Add some missing values
        df_with_na = sample_csv_data.copy()
        df_with_na.loc[5, 'Close'] = None
        
        cleaned_df = preprocessor._clean_dataframe(df_with_na, 'test.csv')
        
        # Check that missing values are handled
        assert cleaned_df['Close'].isnull().sum() == 0
        assert len(cleaned_df) <= len(df_with_na)
    
    def test_load_single_csv(self, temp_data_dir):
        """Test loading a single CSV file."""
        preprocessor = DataPreprocessor(data_dir=temp_data_dir)
        csv_path = Path(temp_data_dir) / 'TCS.csv'
        
        df = preprocessor.load_single_csv(csv_path)
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert all(col in df.columns for col in REQUIRED_COLUMNS)
    
    def test_load_all_stocks(self, temp_data_dir):
        """Test loading all stock data."""
        preprocessor = DataPreprocessor(data_dir=temp_data_dir)
        stock_data = preprocessor.load_all_stocks()
        
        assert isinstance(stock_data, dict)
        assert len(stock_data) > 0
        assert 'TCS' in stock_data
        assert 'INFY' in stock_data
    
    def test_get_available_sectors(self):
        """Test getting available sectors."""
        sectors = get_available_sectors()
        assert isinstance(sectors, list)
        assert 'Banking' in sectors or 'IT' in sectors
    
    def test_get_available_tickers(self):
        """Test getting available tickers."""
        tickers = get_available_tickers()
        assert isinstance(tickers, list)
        assert len(tickers) > 0


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_get_sector_data(self):
        """Test get_sector_data function."""
        # This test requires actual data to be present
        # It's more of an integration test
        pass
    
    def test_get_stock_data(self):
        """Test get_stock_data function."""
        # This test requires actual data to be present
        # It's more of an integration test
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
