"""
Test Script for Training Pipeline

This script validates the training pipeline with dummy data to ensure
all models can be trained and saved/loaded correctly.

Usage:
    python scripts/test_train_all.py

Author: QuantFin Team
Date: 2025-10-09
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml_models.linear_reg import LinearRegModel
from app.ml_models.logreg import LogisticRegModel
from app.ml_models.svm_model import SVMModel
from app.ml_models.arima_model import ARIMAModel
from app.ml_models.lstm_model import LSTMModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_dummy_data(n_samples: int = 500) -> pd.DataFrame:
    """
    Create dummy feature DataFrame for testing.
    
    Args:
        n_samples (int): Number of samples
    
    Returns:
        pd.DataFrame: Dummy data with features
    """
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=n_samples, freq='D')
    
    # Generate synthetic price data with trend and noise
    base_price = 100
    trend = np.linspace(0, 50, n_samples)
    noise = np.random.normal(0, 5, n_samples)
    prices = base_price + trend + noise
    prices = np.maximum(prices, 10)  # Ensure positive prices
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': prices * 0.98,
        'High': prices * 1.02,
        'Low': prices * 0.97,
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, n_samples),
    })
    
    # Add technical indicators
    df['SMA_10'] = df['Close'].rolling(10).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    df['RSI_14'] = 50 + np.random.normal(0, 10, n_samples)  # Simplified RSI
    df['BB_upper'] = df['Close'] * 1.05
    df['BB_lower'] = df['Close'] * 0.95
    df['vol_21'] = df['Close'].rolling(21).std()
    df['avg_volume_21'] = df['Volume'].rolling(21).mean()
    
    # Lagged returns
    df['return_1d'] = df['Close'].pct_change(1)
    df['return_5d'] = df['Close'].pct_change(5)
    df['return_21d'] = df['Close'].pct_change(21)
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    
    # Fill NaN values
    df = df.fillna(method='bfill').fillna(0)
    
    return df


def test_model(model_class, model_name: str, df: pd.DataFrame, temp_dir: Path) -> bool:
    """
    Test a single model's train/predict/save/load pipeline.
    
    Args:
        model_class: Model class to test
        model_name: Name of the model
        df: DataFrame with features
        temp_dir: Temporary directory for model storage
    
    Returns:
        bool: True if test passed
    """
    logger.info(f"\nTesting {model_name}...")
    
    try:
        symbol = "TEST"
        models_dir = str(temp_dir / model_name)
        
        # Create model instance
        model = model_class(symbol=symbol, models_dir=models_dir)
        
        # Test training
        logger.info(f"  → Training...")
        if model_name == 'arima':
            # ARIMA uses only Close prices
            train_df = df[['Date', 'Close']].copy()
            metrics = model.train(train_df, max_p=2, max_d=1, max_q=2, test_size=21)
        elif model_name == 'lstm':
            # LSTM with quick parameters
            metrics = model.train(
                df,
                sequence_length=30,
                test_size=0.2,
                epochs=5,
                batch_size=32,
                lstm_units_1=32,
                lstm_units_2=16,
                patience=3
            )
        else:
            # Other models
            metrics = model.train(df, test_size=0.2)
        
        logger.info(f"    ✓ Training completed")
        logger.info(f"      Metrics: {list(metrics.keys())[:5]}")
        
        # Test saving
        logger.info(f"  → Saving model...")
        saved_path = model.save_model("test_v1")
        assert Path(saved_path).exists(), "Model file not saved"
        logger.info(f"    ✓ Model saved to {saved_path}")
        
        # Test loading
        logger.info(f"  → Loading model...")
        new_model = model_class(symbol=symbol, models_dir=models_dir)
        loaded_metrics = new_model.load_model("test_v1")
        assert loaded_metrics is not None, "Failed to load metrics"
        logger.info(f"    ✓ Model loaded successfully")
        
        # Test prediction
        logger.info(f"  → Making prediction...")
        if model_name == 'arima':
            prediction = new_model.forecast(steps=21)
            assert 'expected_price' in prediction, "Missing expected_price in ARIMA forecast"
            assert len(prediction['expected_price']) == 21, "Wrong forecast length"
        else:
            prediction = new_model.predict(df)
            assert prediction is not None, "Prediction failed"
        
        logger.info(f"    ✓ Prediction successful")
        logger.info(f"      Keys: {list(prediction.keys())}")
        
        logger.info(f"✅ {model_name} test PASSED")
        return True
    
    except Exception as e:
        logger.error(f"❌ {model_name} test FAILED: {e}", exc_info=True)
        return False


def main():
    """Main test function."""
    logger.info("="*60)
    logger.info("Training Pipeline Test")
    logger.info("="*60)
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    logger.info(f"Using temporary directory: {temp_dir}")
    
    try:
        # Create dummy data
        logger.info("\nCreating dummy data...")
        df = create_dummy_data(n_samples=500)
        logger.info(f"  ✓ Created DataFrame with shape {df.shape}")
        logger.info(f"  ✓ Columns: {list(df.columns)}")
        
        # Test each model
        results = {}
        
        models_to_test = [
            (LinearRegModel, 'linear_reg'),
            (LogisticRegModel, 'logreg'),
            (SVMModel, 'svm'),
            (ARIMAModel, 'arima'),
            (LSTMModel, 'lstm')
        ]
        
        for model_class, model_name in models_to_test:
            results[model_name] = test_model(model_class, model_name, df, temp_dir)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("Test Summary")
        logger.info("="*60)
        
        passed = sum(results.values())
        total = len(results)
        
        for model_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {model_name:15} : {status}")
        
        logger.info("-"*60)
        logger.info(f"Total: {passed}/{total} passed ({passed/total*100:.0f}%)")
        logger.info("="*60)
        
        if passed == total:
            logger.info("\n🎉 All tests passed! Training pipeline is working correctly.")
            return True
        else:
            logger.error(f"\n❌ {total - passed} test(s) failed. Please fix the issues.")
            return False
    
    finally:
        # Cleanup
        logger.info(f"\nCleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
