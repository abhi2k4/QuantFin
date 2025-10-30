"""
Offline Training Script - Professional Quant Finance Approach

This script trains ML models WITHOUT data leakage:
1. Time-based split (NO shuffling)
2. Proper feature engineering
3. 21-day forward returns as target
4. Train/test split: Before 2023-01-01 / After 2023-01-01
5. Evaluation using regression metrics (MSE, MAE, R²)
6. Save trained models for production use

Usage:
    # Train Linear and SVM models for all stocks
    python scripts/offline_training.py --models linear svm
    
    # Train only for specific stocks
    python scripts/offline_training.py --symbols RELIANCE TCS INFY --models linear
    
    # Use different train/test split date
    python scripts/offline_training.py --split-date 2024-01-01

Author: QuantFin Team
Date: 2025-10-31
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import logging
import argparse
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pickle
from tqdm import tqdm

# Scikit-learn models
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Import data service
from app.services.real_data_service import RealDataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OfflineTrainer:
    """
    Professional offline trainer without data leakage.
    
    Key principles:
    - Time-based split (no shuffling)
    - Train on past data only
    - Test on future data only
    - Pure regression task (predict % returns)
    - No fake accuracy scaling
    """
    
    def __init__(self, data_dir: str = "data", models_dir: str = "models", split_date: str = "2023-01-01"):
        """
        Initialize offline trainer.
        
        Args:
            data_dir: Directory containing CSV files
            models_dir: Directory to save trained models
            split_date: Date to split train/test (format: YYYY-MM-DD)
        """
        self.data_service = RealDataService(data_dir=data_dir)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.split_date = pd.to_datetime(split_date)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'split_date': split_date,
            'models_trained': [],
            'errors': [],
            'summary': {}
        }
        
        logger.info(f"OfflineTrainer initialized")
        logger.info(f"Train/Test split date: {split_date}")
        logger.info(f"Available symbols: {len(self.data_service.symbols)}")
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from OHLCV data.
        
        Features:
        - returns[-1]: 1-day return
        - returns[-5]: 5-day return
        - returns[-10]: 10-day return
        - volatility_21: 21-day rolling volatility
        - volume_ratio: Current volume / 21-day avg volume
        
        Target:
        - future_return_21: 21-day forward return
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features and target
        """
        df = df.copy()
        
        # Calculate returns
        df['return_1d'] = df['Close'].pct_change(1)
        df['return_5d'] = df['Close'].pct_change(5)
        df['return_10d'] = df['Close'].pct_change(10)
        
        # Volatility (21-day rolling std of daily returns)
        df['volatility_21'] = df['return_1d'].rolling(window=21).std()
        
        # Volume ratio
        df['volume_avg_21'] = df['Volume'].rolling(window=21).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_avg_21']
        
        # Price momentum (current price vs 21-day MA)
        df['price_ma_21'] = df['Close'].rolling(window=21).mean()
        df['price_momentum'] = (df['Close'] - df['price_ma_21']) / df['price_ma_21']
        
        # Target: 21-day forward return (NO DATA LEAKAGE!)
        # shift(-21) means we're predicting 21 days into the future
        df['future_return_21'] = df['Close'].pct_change(21).shift(-21)
        
        # Drop NaN rows
        df = df.dropna()
        
        return df
    
    def prepare_train_test_split(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train/test based on time (NO SHUFFLING).
        
        Args:
            df: DataFrame with features and target
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        # Define feature columns
        feature_cols = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_21', 'volume_ratio', 'price_momentum'
        ]
        
        # Split by date (time-based, NO shuffling)
        train_mask = df['Date'] < self.split_date
        test_mask = df['Date'] >= self.split_date
        
        df_train = df[train_mask]
        df_test = df[test_mask]
        
        # Extract features and target
        X_train = df_train[feature_cols].values
        y_train = df_train['future_return_21'].values
        X_test = df_test[feature_cols].values
        y_test = df_test['future_return_21'].values
        
        # Replace inf/nan with 0
        X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
        X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)
        y_train = np.nan_to_num(y_train, nan=0.0, posinf=0.0, neginf=0.0)
        y_test = np.nan_to_num(y_test, nan=0.0, posinf=0.0, neginf=0.0)
        
        logger.debug(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test
    
    def train_linear_model(self, symbol: str) -> Dict:
        """
        Train Ridge regression model for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info(f"Training Linear model for {symbol}...")
            
            # Load data
            df = self.data_service.load_stock_data(symbol)
            
            # Engineer features
            df = self.engineer_features(df)
            
            # Check if we have enough data
            if len(df) < 100:
                raise ValueError(f"Insufficient data: {len(df)} rows")
            
            # Prepare train/test split
            X_train, X_test, y_train, y_test = self.prepare_train_test_split(df)
            
            if len(X_train) == 0 or len(X_test) == 0:
                raise ValueError("Train or test set is empty after split")
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Ridge regression
            model = Ridge(alpha=1.0, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_train_pred = model.predict(X_train_scaled)
            y_test_pred = model.predict(X_test_scaled)
            
            # Calculate metrics (REGRESSION metrics, not accuracy!)
            train_mse = mean_squared_error(y_train, y_train_pred)
            test_mse = mean_squared_error(y_test, y_test_pred)
            train_mae = mean_absolute_error(y_train, y_train_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            
            # Save model
            model_dir = self.models_dir / "linear_reg"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            model_path = model_dir / f"{symbol}_linear.pkl"
            scaler_path = model_dir / f"{symbol}_scaler.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            
            logger.info(f"✅ Linear model saved: {model_path}")
            
            result = {
                'status': 'success',
                'symbol': symbol,
                'model_type': 'linear',
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'train_mse': float(train_mse),
                'test_mse': float(test_mse),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'train_r2': float(train_r2),
                'test_r2': float(test_r2),
                'model_path': str(model_path)
            }
            
            self.results['models_trained'].append(result)
            return result
            
        except Exception as e:
            logger.error(f"❌ Linear training failed for {symbol}: {e}")
            error_result = {
                'status': 'error',
                'symbol': symbol,
                'model_type': 'linear',
                'error': str(e)
            }
            self.results['errors'].append(error_result)
            return error_result
    
    def train_svm_model(self, symbol: str) -> Dict:
        """
        Train SVR (Support Vector Regression) model for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info(f"Training SVM model for {symbol}...")
            
            # Load data
            df = self.data_service.load_stock_data(symbol)
            
            # Engineer features
            df = self.engineer_features(df)
            
            # Check if we have enough data
            if len(df) < 100:
                raise ValueError(f"Insufficient data: {len(df)} rows")
            
            # Prepare train/test split
            X_train, X_test, y_train, y_test = self.prepare_train_test_split(df)
            
            if len(X_train) == 0 or len(X_test) == 0:
                raise ValueError("Train or test set is empty after split")
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train SVR with RBF kernel
            model = SVR(kernel='rbf', C=1.0, epsilon=0.1)
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_train_pred = model.predict(X_train_scaled)
            y_test_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            train_mse = mean_squared_error(y_train, y_train_pred)
            test_mse = mean_squared_error(y_test, y_test_pred)
            train_mae = mean_absolute_error(y_train, y_train_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            
            # Save model
            model_dir = self.models_dir / "svm"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            model_path = model_dir / f"{symbol}_svm.pkl"
            scaler_path = model_dir / f"{symbol}_scaler.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            
            logger.info(f"✅ SVM model saved: {model_path}")
            
            result = {
                'status': 'success',
                'symbol': symbol,
                'model_type': 'svm',
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'train_mse': float(train_mse),
                'test_mse': float(test_mse),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'train_r2': float(train_r2),
                'test_r2': float(test_r2),
                'model_path': str(model_path)
            }
            
            self.results['models_trained'].append(result)
            return result
            
        except Exception as e:
            logger.error(f"❌ SVM training failed for {symbol}: {e}")
            error_result = {
                'status': 'error',
                'symbol': symbol,
                'model_type': 'svm',
                'error': str(e)
            }
            self.results['errors'].append(error_result)
            return error_result
    
    def train_all(self, symbols: Optional[List[str]] = None, models: List[str] = ['linear', 'svm']) -> Dict:
        """
        Train models for multiple symbols.
        
        Args:
            symbols: List of symbols to train (None = all available)
            models: List of model types to train ('linear', 'svm')
            
        Returns:
            Dictionary with summary results
        """
        if symbols is None:
            symbols = self.data_service.symbols
        
        logger.info(f"Training {len(symbols)} symbols with models: {models}")
        
        for symbol in tqdm(symbols, desc="Training models"):
            if 'linear' in models:
                self.train_linear_model(symbol)
            
            if 'svm' in models:
                self.train_svm_model(symbol)
        
        # Calculate summary statistics
        successful = [r for r in self.results['models_trained'] if r['status'] == 'success']
        failed = [r for r in self.results['errors']]
        
        if successful:
            avg_test_r2 = np.mean([r['test_r2'] for r in successful])
            avg_test_mae = np.mean([r['test_mae'] for r in successful])
        else:
            avg_test_r2 = 0.0
            avg_test_mae = 0.0
        
        self.results['summary'] = {
            'total_models': len(successful) + len(failed),
            'successful': len(successful),
            'failed': len(failed),
            'avg_test_r2': float(avg_test_r2),
            'avg_test_mae': float(avg_test_mae),
            'symbols_trained': len(set(r['symbol'] for r in successful)),
            'split_date': self.split_date.strftime('%Y-%m-%d')
        }
        
        logger.info("=" * 60)
        logger.info("TRAINING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total models: {self.results['summary']['total_models']}")
        logger.info(f"Successful: {self.results['summary']['successful']}")
        logger.info(f"Failed: {self.results['summary']['failed']}")
        logger.info(f"Avg Test R²: {self.results['summary']['avg_test_r2']:.4f}")
        logger.info(f"Avg Test MAE: {self.results['summary']['avg_test_mae']:.4f}")
        logger.info("=" * 60)
        
        return self.results
    
    def save_results(self, output_path: str = "training_results.json"):
        """Save training results to JSON file."""
        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {output_file}")


def main():
    """Main entry point for offline training."""
    parser = argparse.ArgumentParser(
        description="Offline training script without data leakage"
    )
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=None,
        help='Symbols to train (default: all available)'
    )
    parser.add_argument(
        '--models',
        nargs='+',
        default=['linear', 'svm'],
        choices=['linear', 'svm'],
        help='Models to train (default: linear svm)'
    )
    parser.add_argument(
        '--split-date',
        default='2023-01-01',
        help='Train/test split date (default: 2023-01-01)'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Data directory (default: data)'
    )
    parser.add_argument(
        '--models-dir',
        default='models',
        help='Models directory (default: models)'
    )
    parser.add_argument(
        '--save-results',
        action='store_true',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = OfflineTrainer(
        data_dir=args.data_dir,
        models_dir=args.models_dir,
        split_date=args.split_date
    )
    
    # Train models
    results = trainer.train_all(
        symbols=args.symbols,
        models=args.models
    )
    
    # Save results if requested
    if args.save_results:
        trainer.save_results()
    
    # Exit with error code if any training failed
    if results['summary']['failed'] > 0:
        logger.warning(f"⚠️ {results['summary']['failed']} models failed to train")
        sys.exit(1)
    else:
        logger.info("✅ All models trained successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
