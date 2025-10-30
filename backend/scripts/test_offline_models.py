"""
Quick test script to verify offline-trained models work correctly.

This script:
1. Loads saved models from offline_training.py
2. Makes predictions on test data
3. Verifies predictions are reasonable
4. Compares with raw predictions (no scaling)

Usage:
    python scripts/test_offline_models.py --symbol RELIANCE --model linear
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import argparse
import pickle
import pandas as pd
import numpy as np
from app.services.real_data_service import RealDataService

def load_model(symbol: str, model_type: str, models_dir: str = "models"):
    """Load trained model and scaler."""
    models_path = Path(models_dir)
    
    if model_type == 'linear':
        model_file = models_path / "linear_reg" / f"{symbol}_linear.pkl"
        scaler_file = models_path / "linear_reg" / f"{symbol}_scaler.pkl"
    elif model_type == 'svm':
        model_file = models_path / "svm" / f"{symbol}_svm.pkl"
        scaler_file = models_path / "svm" / f"{symbol}_scaler.pkl"
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    if not model_file.exists():
        raise FileNotFoundError(f"Model not found: {model_file}")
    
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
    
    with open(scaler_file, 'rb') as f:
        scaler = pickle.load(f)
    
    return model, scaler

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features (same as offline_training.py)."""
    df = df.copy()
    
    df['return_1d'] = df['Close'].pct_change(1)
    df['return_5d'] = df['Close'].pct_change(5)
    df['return_10d'] = df['Close'].pct_change(10)
    df['volatility_21'] = df['return_1d'].rolling(window=21).std()
    df['volume_avg_21'] = df['Volume'].rolling(window=21).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_avg_21']
    df['price_ma_21'] = df['Close'].rolling(window=21).mean()
    df['price_momentum'] = (df['Close'] - df['price_ma_21']) / df['price_ma_21']
    
    df = df.dropna()
    return df

def test_model(symbol: str, model_type: str):
    """Test a trained model."""
    print(f"\n{'='*60}")
    print(f"Testing {model_type.upper()} model for {symbol}")
    print(f"{'='*60}\n")
    
    # Load data
    data_service = RealDataService(data_dir="data")
    df = data_service.load_stock_data(symbol)
    print(f"✅ Loaded {len(df)} records")
    
    # Engineer features
    df = engineer_features(df)
    print(f"✅ Engineered features: {len(df)} rows after cleaning")
    
    # Load model
    model, scaler = load_model(symbol, model_type)
    print(f"✅ Loaded {model_type} model")
    
    # Get last 30 days for testing
    df_test = df.tail(30).copy()
    
    feature_cols = [
        'return_1d', 'return_5d', 'return_10d',
        'volatility_21', 'volume_ratio', 'price_momentum'
    ]
    
    X_test = df_test[feature_cols].values
    X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Scale and predict
    X_test_scaled = scaler.transform(X_test)
    predictions = model.predict(X_test_scaled)
    
    # Show predictions
    print(f"\n{'='*60}")
    print(f"RAW PREDICTIONS (no fake accuracy scaling!)")
    print(f"{'='*60}\n")
    
    df_test['predicted_return_21d'] = predictions
    df_test['predicted_return_pct'] = predictions * 100
    
    # Display results
    display_df = df_test[['Date', 'Close', 'predicted_return_pct']].tail(10)
    print(display_df.to_string(index=False))
    
    # Statistics
    print(f"\n{'='*60}")
    print(f"PREDICTION STATISTICS")
    print(f"{'='*60}\n")
    print(f"Mean prediction: {predictions.mean()*100:.2f}%")
    print(f"Std prediction:  {predictions.std()*100:.2f}%")
    print(f"Min prediction:  {predictions.min()*100:.2f}%")
    print(f"Max prediction:  {predictions.max()*100:.2f}%")
    
    # Sanity checks
    print(f"\n{'='*60}")
    print(f"SANITY CHECKS")
    print(f"{'='*60}\n")
    
    if np.abs(predictions.mean()) < 0.5:  # Less than 50% avg return
        print("✅ Predictions are reasonable (not extreme)")
    else:
        print("⚠️ Predictions seem extreme (>50% avg return)")
    
    if predictions.std() < 0.3:  # Less than 30% std
        print("✅ Predictions have reasonable variance")
    else:
        print("⚠️ Predictions have high variance (>30% std)")
    
    if not np.any(np.isnan(predictions)):
        print("✅ No NaN predictions")
    else:
        print("❌ Found NaN predictions!")
    
    if not np.any(np.isinf(predictions)):
        print("✅ No infinite predictions")
    else:
        print("❌ Found infinite predictions!")
    
    print(f"\n{'='*60}")
    print(f"✅ Model test complete!")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="Test offline-trained models")
    parser.add_argument('--symbol', default='RELIANCE', help='Stock symbol')
    parser.add_argument('--model', default='linear', choices=['linear', 'svm'], help='Model type')
    
    args = parser.parse_args()
    
    try:
        test_model(args.symbol, args.model)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
