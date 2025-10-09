"""
ML Model Service - Train and predict with real models

Implements LSTM, Linear Regression, Logistic Regression, and SVM
for stock price prediction using actual historical data.

Author: QuantFin Team
Date: 2025-10-10
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
import pickle
from pathlib import Path

# Scikit-learn models
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
from sklearn.model_selection import train_test_split

# TensorFlow/Keras for LSTM
try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False

from .real_data_service import get_real_data_service

logger = logging.getLogger(__name__)


class MLModelService:
    """
    Service for training and predicting with ML models on real stock data.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """Initialize ML model service."""
        if models_dir is None:
            models_dir = Path(__file__).resolve().parent.parent.parent / "models"
        
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.data_service = get_real_data_service()
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.logger = logging.getLogger(__name__)
        
        # Model cache
        self._trained_models: Dict[str, any] = {}
        self._model_metrics: Dict[str, Dict] = {}
    
    def prepare_data(
        self, 
        symbol: str, 
        lookback: int = 60,
        test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, MinMaxScaler]:
        """
        Prepare data for ML models.
        
        Args:
            symbol: Stock symbol
            lookback: Number of previous days to use as features
            test_size: Fraction of data to use for testing
            
        Returns:
            X_train, X_test, y_train, y_test, scaler
        """
        df = self.data_service.load_stock_data(symbol)
        
        # Use close prices
        prices = df['Close'].values.reshape(-1, 1)
        
        # Scale data
        scaled_prices = self.scaler.fit_transform(prices)
        
        # Create sequences
        X, y = [], []
        for i in range(lookback, len(scaled_prices)):
            X.append(scaled_prices[i-lookback:i, 0])
            y.append(scaled_prices[i, 0])
        
        X, y = np.array(X), np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        return X_train, X_test, y_train, y_test, self.scaler
    
    def train_lstm(
        self, 
        symbol: str, 
        lookback: int = 60,
        epochs: int = 50,
        batch_size: int = 32
    ) -> Dict:
        """
        Train LSTM model on real stock data.
        
        Returns:
            Dict with model, metrics, and predictions
        """
        if not LSTM_AVAILABLE:
            raise ImportError("TensorFlow not available. Install with: pip install tensorflow")
        
        self.logger.info(f"Training LSTM for {symbol}")
        
        # Prepare data
        X_train, X_test, y_train, y_test, scaler = self.prepare_data(symbol, lookback)
        
        # Reshape for LSTM [samples, timesteps, features]
        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        # Build LSTM model
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        # Train
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Predictions
        y_pred_train = model.predict(X_train, verbose=0)
        y_pred_test = model.predict(X_test, verbose=0)
        
        # Inverse transform
        y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
        y_pred_train_actual = scaler.inverse_transform(y_pred_train)
        y_pred_test_actual = scaler.inverse_transform(y_pred_test)
        
        # Calculate metrics
        metrics = {
            'model_type': 'LSTM',
            'symbol': symbol,
            'train_rmse': float(np.sqrt(mean_squared_error(y_train_actual, y_pred_train_actual))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test_actual, y_pred_test_actual))),
            'train_mae': float(mean_absolute_error(y_train_actual, y_pred_train_actual)),
            'test_mae': float(mean_absolute_error(y_test_actual, y_pred_test_actual)),
            'train_r2': float(r2_score(y_train_actual, y_pred_train_actual)),
            'test_r2': float(r2_score(y_test_actual, y_pred_test_actual)),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'lookback': lookback
        }
        
        # Calculate accuracy (% predictions within 5% of actual)
        train_accuracy = np.mean(np.abs((y_train_actual - y_pred_train_actual) / y_train_actual) <= 0.05) * 100
        test_accuracy = np.mean(np.abs((y_test_actual - y_pred_test_actual) / y_test_actual) <= 0.05) * 100
        
        metrics['train_accuracy'] = float(train_accuracy)
        metrics['test_accuracy'] = float(test_accuracy)
        
        # Save model
        model_path = self.models_dir / f"{symbol}_lstm.h5"
        model.save(model_path)
        
        # Cache
        self._trained_models[f'{symbol}_lstm'] = model
        self._model_metrics[f'{symbol}_lstm'] = metrics
        
        self.logger.info(f"LSTM trained for {symbol}: Test Accuracy={test_accuracy:.2f}%, RMSE={metrics['test_rmse']:.2f}")
        
        return {
            'model': model,
            'metrics': metrics,
            'scaler': scaler,
            'history': history.history
        }
    
    def train_linear_regression(self, symbol: str, lookback: int = 60) -> Dict:
        """Train Linear Regression model."""
        self.logger.info(f"Training Linear Regression for {symbol}")
        
        X_train, X_test, y_train, y_test, scaler = self.prepare_data(symbol, lookback)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Inverse transform
        y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
        y_pred_train_actual = scaler.inverse_transform(y_pred_train.reshape(-1, 1))
        y_pred_test_actual = scaler.inverse_transform(y_pred_test.reshape(-1, 1))
        
        # Calculate metrics
        metrics = {
            'model_type': 'Linear Regression',
            'symbol': symbol,
            'train_rmse': float(np.sqrt(mean_squared_error(y_train_actual, y_pred_train_actual))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test_actual, y_pred_test_actual))),
            'train_mae': float(mean_absolute_error(y_train_actual, y_pred_train_actual)),
            'test_mae': float(mean_absolute_error(y_test_actual, y_pred_test_actual)),
            'train_r2': float(r2_score(y_train_actual, y_pred_train_actual)),
            'test_r2': float(r2_score(y_test_actual, y_pred_test_actual)),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        # Calculate accuracy
        train_accuracy = np.mean(np.abs((y_train_actual - y_pred_train_actual) / y_train_actual) <= 0.05) * 100
        test_accuracy = np.mean(np.abs((y_test_actual - y_pred_test_actual) / y_test_actual) <= 0.05) * 100
        
        metrics['train_accuracy'] = float(train_accuracy)
        metrics['test_accuracy'] = float(test_accuracy)
        
        # Save model
        model_path = self.models_dir / f"{symbol}_linear.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
        
        # Cache
        self._trained_models[f'{symbol}_linear'] = model
        self._model_metrics[f'{symbol}_linear'] = metrics
        
        self.logger.info(f"Linear Regression trained for {symbol}: Test Accuracy={test_accuracy:.2f}%")
        
        return {
            'model': model,
            'metrics': metrics,
            'scaler': scaler
        }
    
    def train_svm(self, symbol: str, lookback: int = 60) -> Dict:
        """Train SVM model."""
        self.logger.info(f"Training SVM for {symbol}")
        
        X_train, X_test, y_train, y_test, scaler = self.prepare_data(symbol, lookback)
        
        # Train model
        model = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.01)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Inverse transform
        y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
        y_pred_train_actual = scaler.inverse_transform(y_pred_train.reshape(-1, 1))
        y_pred_test_actual = scaler.inverse_transform(y_pred_test.reshape(-1, 1))
        
        # Calculate metrics
        metrics = {
            'model_type': 'SVM',
            'symbol': symbol,
            'train_rmse': float(np.sqrt(mean_squared_error(y_train_actual, y_pred_train_actual))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test_actual, y_pred_test_actual))),
            'train_mae': float(mean_absolute_error(y_train_actual, y_pred_train_actual)),
            'test_mae': float(mean_absolute_error(y_test_actual, y_pred_test_actual)),
            'train_r2': float(r2_score(y_train_actual, y_pred_train_actual)),
            'test_r2': float(r2_score(y_test_actual, y_pred_test_actual)),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        # Calculate accuracy
        train_accuracy = np.mean(np.abs((y_train_actual - y_pred_train_actual) / y_train_actual) <= 0.05) * 100
        test_accuracy = np.mean(np.abs((y_test_actual - y_pred_test_actual) / y_test_actual) <= 0.05) * 100
        
        metrics['train_accuracy'] = float(train_accuracy)
        metrics['test_accuracy'] = float(test_accuracy)
        
        # Save model
        model_path = self.models_dir / f"{symbol}_svm.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
        
        # Cache
        self._trained_models[f'{symbol}_svm'] = model
        self._model_metrics[f'{symbol}_svm'] = metrics
        
        self.logger.info(f"SVM trained for {symbol}: Test Accuracy={test_accuracy:.2f}%")
        
        return {
            'model': model,
            'metrics': metrics,
            'scaler': scaler
        }
    
    def predict_next_day(self, symbol: str, model_type: str = 'lstm', lookback: int = 60) -> Dict:
        """
        Predict next day's price using trained model.
        
        Args:
            symbol: Stock symbol
            model_type: 'lstm', 'linear', 'svm'
            lookback: Number of days to use
            
        Returns:
            Dict with prediction and confidence
        """
        df = self.data_service.load_stock_data(symbol)
        
        # Get last 'lookback' days
        recent_prices = df['Close'].tail(lookback).values.reshape(-1, 1)
        scaled_prices = self.scaler.fit_transform(recent_prices)
        
        # Prepare input
        X = scaled_prices.reshape(1, -1)
        
        # Load or train model
        model_key = f'{symbol}_{model_type}'
        if model_key not in self._trained_models:
            if model_type == 'lstm':
                self.train_lstm(symbol, lookback)
            elif model_type == 'linear':
                self.train_linear_regression(symbol, lookback)
            elif model_type == 'svm':
                self.train_svm(symbol, lookback)
        
        model = self._trained_models[model_key]
        
        # Predict
        if model_type == 'lstm':
            X = X.reshape(1, lookback, 1)
            prediction_scaled = model.predict(X, verbose=0)[0][0]
        else:
            prediction_scaled = model.predict(X)[0]
        
        # Inverse transform
        prediction = self.scaler.inverse_transform([[prediction_scaled]])[0][0]
        
        current_price = float(df.iloc[-1]['Close'])
        expected_return = ((prediction - current_price) / current_price) * 100
        
        # Get metrics for confidence
        metrics = self._model_metrics.get(model_key, {})
        confidence = metrics.get('test_accuracy', 0.0)
        
        return {
            'symbol': symbol,
            'model_type': model_type,
            'current_price': current_price,
            'predicted_price': float(prediction),
            'expected_return': float(expected_return),
            'confidence': confidence,
            'prediction_date': datetime.now().strftime('%Y-%m-%d'),
            'target_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
    
    def get_all_model_metrics(self) -> List[Dict]:
        """Get metrics for all trained models."""
        return list(self._model_metrics.values())


# Global instance
_ml_service = None


def get_ml_service() -> MLModelService:
    """Get or create global MLModelService instance."""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLModelService()
    return _ml_service
