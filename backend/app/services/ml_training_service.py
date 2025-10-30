"""
ML Training Service with Real Data Integration & Caching

Implements proper model caching, background training, and progress tracking.
NO MOCK DATA - Only real historical stock data used.

Author: QuantFin Team
Date: 2025-10-30
"""

import os
import pickle
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd

# Scikit-learn
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# LSTM support
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    LSTM_AVAILABLE = True
    
    # Configure GPU settings
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            # Enable memory growth to prevent TensorFlow from allocating all GPU memory
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            
            # Log GPU info
            gpu_names = [gpu.name for gpu in gpus]
            logging.info(f"🚀 GPU DETECTED! Training will use: {gpu_names}")
            logging.info(f"✓ TensorFlow {tf.__version__} with GPU acceleration enabled")
            logging.info(f"✓ {len(gpus)} GPU(s) available for training")
            
            # Verify CUDA/cuDNN
            if tf.test.is_built_with_cuda():
                logging.info("✓ TensorFlow built with CUDA support")
            if tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None):
                logging.info("✓ GPU is available and ready for training")
                
        except RuntimeError as e:
            logging.warning(f"GPU configuration error: {e}")
            logging.info("✓ TensorFlow available - LSTM will use CPU (may be slower)")
    else:
        logging.info("ℹ No GPU detected - LSTM will train on CPU")
        logging.info("✓ TensorFlow available - LSTM will use neural network on REAL DATA")
        
except ImportError:
    LSTM_AVAILABLE = False
    logging.info("ℹ TensorFlow not available - LSTM will use LinearRegression fallback (REAL DATA, not mock)")

# ARIMA support
try:
    from statsmodels.tsa.arima.model import ARIMA
    from pmdarima import auto_arima
    ARIMA_AVAILABLE = True
    logging.info("✓ statsmodels/pmdarima available - ARIMA will use time series analysis on REAL DATA")
except ImportError:
    ARIMA_AVAILABLE = False
    logging.info("ℹ statsmodels/pmdarima not available - ARIMA will use moving average fallback (REAL DATA, not mock)")

from .real_data_service import RealDataService

logger = logging.getLogger(__name__)


class MLTrainingService:
    """
    Service for training ML models with real data, caching, and progress tracking.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, cache_days: int = 7):
        """
        Initialize ML Training Service.
        
        Args:
            cache_dir: Directory to store cached models
            cache_days: Number of days before cache expires
        """
        if cache_dir is None:
            cache_dir = Path(__file__).resolve().parent.parent.parent / "model_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_expiry = timedelta(days=cache_days)
        self.data_service = RealDataService()
        
        # Training status tracking
        self.training_status = {
            "status": "idle",  # idle, training, completed, failed
            "progress": 0,
            "current_model": None,
            "models_completed": [],
            "error": None,
            "started_at": None,
            "completed_at": None
        }
        
        logger.info(f"MLTrainingService initialized. Cache dir: {self.cache_dir}")
    
    def get_cache_path(self, model_name: str) -> Path:
        """Get cache file path for a model."""
        safe_name = model_name.replace(" ", "_").lower()
        return self.cache_dir / f"{safe_name}_model.pkl"
    
    def is_cache_valid(self, model_name: str) -> bool:
        """Check if cached model exists and is still valid."""
        cache_path = self.get_cache_path(model_name)
        
        if not cache_path.exists():
            logger.info(f"No cache found for {model_name}")
            return False
        
        # Check cache age
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - cache_time
        
        if age > self.cache_expiry:
            logger.info(f"Cache expired for {model_name}. Age: {age.days} days")
            return False
        
        logger.info(f"Valid cache found for {model_name}. Age: {age.days} days")
        return True
    
    def load_cached_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Load a cached model from disk."""
        cache_path = self.get_cache_path(model_name)
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            logger.info(f"Loaded cached model: {model_name}")
            return cached_data
            
        except Exception as e:
            logger.error(f"Error loading cached model {model_name}: {e}")
            return None
    
    def save_model_cache(self, model_name: str, model_data: Dict[str, Any]):
        """Save trained model to disk cache."""
        cache_path = self.get_cache_path(model_name)
        
        try:
            # Add timestamp
            model_data['cached_at'] = datetime.now().isoformat()
            model_data['cache_expires'] = (datetime.now() + self.cache_expiry).isoformat()
            
            with open(cache_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Saved model cache: {model_name} -> {cache_path}")
            
        except Exception as e:
            logger.error(f"Error saving model cache {model_name}: {e}")
    
    def add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators and features to dataframe.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added features
        """
        df = df.copy()
        
        # Returns
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Rolling statistics
        for window in [7, 14, 21, 30]:
            df[f'sma_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'std_{window}'] = df['Close'].rolling(window=window).std()
            df[f'min_{window}'] = df['Close'].rolling(window=window).min()
            df[f'max_{window}'] = df['Close'].rolling(window=window).max()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['Close'].rolling(window=20).mean()
        df['bb_std'] = df['Close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        # Volume indicators
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Price position
        df['high_low_ratio'] = df['High'] / df['Low']
        df['close_open_ratio'] = df['Close'] / df['Open']
        
        return df
    
    def prepare_data(self, symbols: List[str], lookback: int = 60) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Prepare real training data from all stock symbols.
        
        Args:
            symbols: List of stock symbols to train on
            lookback: Number of days to look back for features
            
        Returns:
            X_train, y_train, full_dataframe
        """
        logger.info(f"Preparing data from {len(symbols)} stocks...")
        
        all_data = []
        
        for symbol in symbols[:10]:  # Use first 10 stocks for faster training
            try:
                # Load historical data
                df = self.data_service.load_stock_data(symbol, cache=True)
                
                if df is None or len(df) < 100:
                    logger.warning(f"Insufficient data for {symbol}, skipping")
                    continue
                
                # Add technical features
                df_featured = self.add_technical_features(df.copy())
                
                # Drop NaN values
                df_featured = df_featured.dropna()
                
                if len(df_featured) > 0:
                    all_data.append(df_featured)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        if not all_data:
            raise ValueError("No valid data could be prepared for training")
        
        # Combine all stock data
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined data shape: {combined_df.shape}")
        
        # Prepare features and target
        feature_cols = [col for col in combined_df.columns 
                       if col not in ['Date', 'Symbol', 'Close'] and not col.startswith('Unnamed')]
        
        X = combined_df[feature_cols].values
        y = combined_df['Close'].values
        
        return X, y, combined_df
    
    def get_optimal_batch_size(self) -> int:
        """
        Determine optimal batch size based on GPU availability.
        
        Returns:
            Optimal batch size (larger for GPU, smaller for CPU)
        """
        if LSTM_AVAILABLE:
            try:
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    # GPU available - use larger batch size for efficiency
                    return 128
            except:
                pass
        # CPU fallback - smaller batch size
        return 32
    
    async def train_lstm_model(self) -> Dict[str, Any]:
        """Train LSTM model on real data."""
        logger.info("=" * 80)
        logger.info("🧠 Training LSTM Model (Real Data)")
        logger.info("=" * 80)
        
        try:
            # Prepare data
            symbols = self.data_service.symbols[:10]
            logger.info(f"📊 Loading data from {len(symbols)} stocks: {', '.join(symbols[:5])}...")
            
            X, y, df = self.prepare_data(symbols, lookback=60)
            
            logger.info(f"✓ Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
            logger.info(f"🔧 Splitting into train/test sets...")
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale data
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
            
            X_train_scaled = scaler_X.fit_transform(X_train)
            X_test_scaled = scaler_X.transform(X_test)
            y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
            y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()
            
            # Reshape for LSTM (samples, timesteps, features)
            timesteps = 60
            X_train_lstm = []
            y_train_lstm = []
            
            for i in range(timesteps, len(X_train_scaled)):
                X_train_lstm.append(X_train_scaled[i-timesteps:i])
                y_train_lstm.append(y_train_scaled[i])
            
            X_train_lstm = np.array(X_train_lstm)
            y_train_lstm = np.array(y_train_lstm)
            
            X_test_lstm = []
            y_test_lstm = []
            
            for i in range(timesteps, len(X_test_scaled)):
                X_test_lstm.append(X_test_scaled[i-timesteps:i])
                y_test_lstm.append(y_test_scaled[i])
            
            X_test_lstm = np.array(X_test_lstm)
            y_test_lstm = np.array(y_test_lstm)
            
            logger.info(f"LSTM training data shape: {X_train_lstm.shape}")
            
            if LSTM_AVAILABLE:
                # Check GPU availability
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    logger.info(f"🚀 Training LSTM on GPU: {[gpu.name for gpu in gpus]}")
                else:
                    logger.info("⚠️ Training LSTM on CPU (consider using GPU for faster training)")
                
                # Get optimal batch size
                batch_size = self.get_optimal_batch_size()
                logger.info(f"Using batch size: {batch_size} ({'GPU-optimized' if batch_size > 32 else 'CPU-optimized'})")
                
                # Build LSTM model
                model = Sequential([
                    LSTM(64, return_sequences=True, input_shape=(timesteps, X_train.shape[1])),
                    Dropout(0.2),
                    LSTM(32, return_sequences=False),
                    Dropout(0.2),
                    Dense(16, activation='relu'),
                    Dense(1)
                ])
                
                model.compile(optimizer='adam', loss='mse', metrics=['mae'])
                
                # Early stopping
                early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
                
                # Train
                logger.info("Training LSTM neural network...")
                history = model.fit(
                    X_train_lstm, y_train_lstm,
                    validation_split=0.2,
                    epochs=30,
                    batch_size=batch_size,
                    callbacks=[early_stop],
                    verbose=1
                )
                
                # Predictions
                y_pred_train = model.predict(X_train_lstm).flatten()
                y_pred_test = model.predict(X_test_lstm).flatten()
                
                # Inverse transform
                y_pred_train_actual = scaler_y.inverse_transform(y_pred_train.reshape(-1, 1)).flatten()
                y_pred_test_actual = scaler_y.inverse_transform(y_pred_test.reshape(-1, 1)).flatten()
                y_train_actual = scaler_y.inverse_transform(y_train_lstm.reshape(-1, 1)).flatten()
                y_test_actual = scaler_y.inverse_transform(y_test_lstm.reshape(-1, 1)).flatten()
                
            else:
                # Fallback: Use linear model if LSTM not available
                logger.info("Using LinearRegression fallback (training on REAL DATA)")
                model = LinearRegression()
                model.fit(X_train_lstm.reshape(X_train_lstm.shape[0], -1), y_train_lstm)
                
                y_pred_train = model.predict(X_train_lstm.reshape(X_train_lstm.shape[0], -1))
                y_pred_test = model.predict(X_test_lstm.reshape(X_test_lstm.shape[0], -1))
                
                y_pred_train_actual = scaler_y.inverse_transform(y_pred_train.reshape(-1, 1)).flatten()
                y_pred_test_actual = scaler_y.inverse_transform(y_pred_test.reshape(-1, 1)).flatten()
                y_train_actual = scaler_y.inverse_transform(y_train_lstm.reshape(-1, 1)).flatten()
                y_test_actual = scaler_y.inverse_transform(y_test_lstm.reshape(-1, 1)).flatten()
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train_actual, y_pred_train_actual))
            test_rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred_test_actual))
            train_mae = mean_absolute_error(y_train_actual, y_pred_train_actual)
            test_mae = mean_absolute_error(y_test_actual, y_pred_test_actual)
            train_r2 = r2_score(y_train_actual, y_pred_train_actual)
            test_r2 = r2_score(y_test_actual, y_pred_test_actual)
            
            # Calculate MAPE (avoid division by zero)
            train_nonzero = y_train_actual != 0
            test_nonzero = y_test_actual != 0
            train_mape = np.mean(np.abs((y_train_actual[train_nonzero] - y_pred_train_actual[train_nonzero]) / y_train_actual[train_nonzero])) * 100 if np.any(train_nonzero) else 0.0
            test_mape = np.mean(np.abs((y_test_actual[test_nonzero] - y_pred_test_actual[test_nonzero]) / y_test_actual[test_nonzero])) * 100 if np.any(test_nonzero) else 0.0
            
            # Calculate accuracy (% predictions within 5% of actual)
            train_accuracy = np.mean(np.abs((y_train_actual[train_nonzero] - y_pred_train_actual[train_nonzero]) / y_train_actual[train_nonzero]) <= 0.05) * 100 if np.any(train_nonzero) else 0.0
            test_accuracy = np.mean(np.abs((y_test_actual[test_nonzero] - y_pred_test_actual[test_nonzero]) / y_test_actual[test_nonzero]) <= 0.05) * 100 if np.any(test_nonzero) else 0.0
            
            metrics = {
                "model": "LSTM",
                "train_accuracy": float(train_accuracy),
                "accuracy": float(test_accuracy),
                "train_rmse": float(train_rmse),
                "rmse": float(test_rmse),
                "train_mae": float(train_mae),
                "mae": float(test_mae),
                "train_mape": float(train_mape),
                "mape": float(test_mape),
                "train_r2": float(train_r2),
                "r2_score": float(test_r2),
                "training_samples": int(len(y_train_actual)),
                "test_samples": int(len(y_test_actual)),
                "trained_at": datetime.now().isoformat(),
                "model_type": "LSTM" if LSTM_AVAILABLE else "LinearRegression (LSTM fallback)"
            }
            
            logger.info(f"✓ LSTM Training Complete!")
            logger.info(f"  Train Accuracy: {train_accuracy:.2f}% (within 5% tolerance)")
            logger.info(f"  Test Accuracy: {test_accuracy:.2f}% (within 5% tolerance)")
            logger.info(f"  Test MAPE: {test_mape:.2f}%")
            logger.info(f"  Test RMSE: {test_rmse:.2f}")
            logger.info(f"  Test R²: {test_r2:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training LSTM: {e}", exc_info=True)
            raise
    
    async def train_linear_regression(self) -> Dict[str, Any]:
        """Train Linear Regression model on real data."""
        logger.info("=" * 80)
        logger.info("📈 Training Linear Regression Model (Real Data)")
        logger.info("=" * 80)
        
        try:
            # Prepare data
            symbols = self.data_service.symbols[:10]
            logger.info(f"📊 Loading data from {len(symbols)} stocks...")
            
            X, y, df = self.prepare_data(symbols)
            
            logger.info(f"✓ Data prepared: {X.shape[0]} samples, {X.shape[1]} features")
            logger.info(f"🔧 Splitting and scaling data...")
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale data
            scaler_X = StandardScaler()
            X_train_scaled = scaler_X.fit_transform(X_train)
            X_test_scaled = scaler_X.transform(X_test)
            
            # Train model
            logger.info("🤖 Training Linear Regression model...")
            model = LinearRegression()
            model.fit(X_train_scaled, y_train)
            
            logger.info("✓ Model training complete, calculating predictions...")
            
            # Predictions
            y_pred_train = model.predict(X_train_scaled)
            y_pred_test = model.predict(X_test_scaled)
            
            logger.info("📊 Computing performance metrics...")
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            
            # Calculate MAPE (avoid division by zero)
            train_nonzero = y_train != 0
            test_nonzero = y_test != 0
            train_mape = np.mean(np.abs((y_train[train_nonzero] - y_pred_train[train_nonzero]) / y_train[train_nonzero])) * 100 if np.any(train_nonzero) else 0.0
            test_mape = np.mean(np.abs((y_test[test_nonzero] - y_pred_test[test_nonzero]) / y_test[test_nonzero])) * 100 if np.any(test_nonzero) else 0.0
            
            # Calculate accuracy (% predictions within 5% of actual)
            train_accuracy = np.mean(np.abs((y_train[train_nonzero] - y_pred_train[train_nonzero]) / y_train[train_nonzero]) <= 0.05) * 100 if np.any(train_nonzero) else 0.0
            test_accuracy = np.mean(np.abs((y_test[test_nonzero] - y_pred_test[test_nonzero]) / y_test[test_nonzero]) <= 0.05) * 100 if np.any(test_nonzero) else 0.0
            
            metrics = {
                "model": "Linear Regression",
                "train_accuracy": float(train_accuracy),
                "accuracy": float(test_accuracy),
                "train_rmse": float(train_rmse),
                "rmse": float(test_rmse),
                "train_mae": float(train_mae),
                "mae": float(test_mae),
                "train_mape": float(train_mape),
                "mape": float(test_mape),
                "train_r2": float(train_r2),
                "r2_score": float(test_r2),
                "training_samples": int(len(y_train)),
                "test_samples": int(len(y_test)),
                "trained_at": datetime.now().isoformat()
            }
            
            logger.info(f"✓ Linear Regression Training Complete!")
            logger.info(f"  Train Accuracy: {train_accuracy:.2f}% (within 5% tolerance)")
            logger.info(f"  Test Accuracy: {test_accuracy:.2f}% (within 5% tolerance)")
            logger.info(f"  Test MAPE: {test_mape:.2f}%")
            logger.info(f"  Test RMSE: {test_rmse:.2f}")
            logger.info(f"  Test R²: {test_r2:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training Linear Regression: {e}", exc_info=True)
            raise
    
    async def train_svm_model(self) -> Dict[str, Any]:
        """Train SVM model on real data."""
        logger.info("=" * 80)
        logger.info("Training SVM Model (Real Data)")
        logger.info("=" * 80)
        
        try:
            # Prepare data
            symbols = self.data_service.symbols[:10]
            X, y, df = self.prepare_data(symbols)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale data
            scaler_X = StandardScaler()
            X_train_scaled = scaler_X.fit_transform(X_train)
            X_test_scaled = scaler_X.transform(X_test)
            
            # Train SVM with RBF kernel
            logger.info("Training SVM (RBF kernel)...")
            model = SVR(kernel='rbf', C=1.0, epsilon=0.1, cache_size=200)
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train_scaled)
            y_pred_test = model.predict(X_test_scaled)
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            
            # Calculate MAPE (avoid division by zero)
            train_nonzero = y_train != 0
            test_nonzero = y_test != 0
            train_mape = np.mean(np.abs((y_train[train_nonzero] - y_pred_train[train_nonzero]) / y_train[train_nonzero])) * 100 if np.any(train_nonzero) else 0.0
            test_mape = np.mean(np.abs((y_test[test_nonzero] - y_pred_test[test_nonzero]) / y_test[test_nonzero])) * 100 if np.any(test_nonzero) else 0.0
            
            # Calculate accuracy (% predictions within 5% of actual)
            train_accuracy = np.mean(np.abs((y_train[train_nonzero] - y_pred_train[train_nonzero]) / y_train[train_nonzero]) <= 0.05) * 100 if np.any(train_nonzero) else 0.0
            test_accuracy = np.mean(np.abs((y_test[test_nonzero] - y_pred_test[test_nonzero]) / y_test[test_nonzero]) <= 0.05) * 100 if np.any(test_nonzero) else 0.0
            
            metrics = {
                "model": "SVM",
                "train_accuracy": float(train_accuracy),
                "accuracy": float(test_accuracy),
                "train_rmse": float(train_rmse),
                "rmse": float(test_rmse),
                "train_mae": float(train_mae),
                "mae": float(test_mae),
                "train_mape": float(train_mape),
                "mape": float(test_mape),
                "train_r2": float(train_r2),
                "r2_score": float(test_r2),
                "training_samples": int(len(y_train)),
                "test_samples": int(len(y_test)),
                "trained_at": datetime.now().isoformat()
            }
            
            logger.info(f"✓ SVM Training Complete!")
            logger.info(f"  Train Accuracy: {train_accuracy:.2f}% (within 5% tolerance)")
            logger.info(f"  Test Accuracy: {test_accuracy:.2f}% (within 5% tolerance)")
            logger.info(f"  Test MAPE: {test_mape:.2f}%")
            logger.info(f"  Test RMSE: {test_rmse:.2f}")
            logger.info(f"  Test R²: {test_r2:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training SVM: {e}", exc_info=True)
            raise
    
    async def train_arima_model(self) -> Dict[str, Any]:
        """Train ARIMA model on real data."""
        logger.info("=" * 80)
        logger.info("Training ARIMA Model (Real Data)")
        logger.info("=" * 80)
        
        try:
            # Use single stock for ARIMA (time series model)
            symbol = self.data_service.symbols[0]
            df = self.data_service.load_stock_data(symbol, cache=True)
            
            if df is None or len(df) < 100:
                raise ValueError(f"Insufficient data for ARIMA training")
            
            # Use Close prices
            prices = df['Close'].values
            
            # Train-test split
            train_size = int(len(prices) * 0.8)
            train_data = prices[:train_size]
            test_data = prices[train_size:]
            
            if ARIMA_AVAILABLE:
                logger.info("Training ARIMA with auto parameter selection...")
                # Auto ARIMA for parameter selection
                model = auto_arima(train_data, seasonal=False, stepwise=True, 
                                 suppress_warnings=True, max_order=5)
                
                # Forecast
                forecast = model.predict(n_periods=len(test_data))
                
                # Calculate metrics
                test_rmse = np.sqrt(mean_squared_error(test_data, forecast))
                test_mae = mean_absolute_error(test_data, forecast)
                test_r2 = r2_score(test_data, forecast)
                
                # Train metrics (in-sample)
                train_pred = model.predict_in_sample()
                train_rmse = np.sqrt(mean_squared_error(train_data, train_pred))
                train_mae = mean_absolute_error(train_data, train_pred)
                train_r2 = r2_score(train_data, train_pred)
                
            else:
                # Fallback: simple moving average
                logger.info("Using moving average fallback (training on REAL DATA)")
                window = 20
                train_pred = pd.Series(train_data).rolling(window=window).mean().fillna(train_data[0]).values
                forecast = np.full(len(test_data), train_data[-window:].mean())
                
                test_rmse = np.sqrt(mean_squared_error(test_data, forecast))
                test_mae = mean_absolute_error(test_data, forecast)
                test_r2 = r2_score(test_data, forecast)
                
                train_rmse = np.sqrt(mean_squared_error(train_data, train_pred))
                train_mae = mean_absolute_error(train_data, train_pred)
                train_r2 = r2_score(train_data, train_pred)
            
            # Calculate MAPE (Mean Absolute Percentage Error) - proper metric for time series
            # Avoid division by zero by using only non-zero values
            train_nonzero = train_data != 0
            test_nonzero = test_data != 0
            
            train_mape = np.mean(np.abs((train_data[train_nonzero] - train_pred[train_nonzero]) / train_data[train_nonzero])) * 100 if np.any(train_nonzero) else 0.0
            test_mape = np.mean(np.abs((test_data[test_nonzero] - forecast[test_nonzero]) / test_data[test_nonzero])) * 100 if np.any(test_nonzero) else 0.0
            
            # Convert MAPE to accuracy (100% - MAPE, capped at 0-100%)
            train_accuracy = max(0.0, min(100.0, 100.0 - train_mape))
            test_accuracy = max(0.0, min(100.0, 100.0 - test_mape))
            
            metrics = {
                "model": "ARIMA",
                "train_accuracy": float(train_accuracy),
                "accuracy": float(test_accuracy),
                "train_rmse": float(train_rmse),
                "rmse": float(test_rmse),
                "train_mae": float(train_mae),
                "mae": float(test_mae),
                "train_mape": float(train_mape),
                "mape": float(test_mape),
                "train_r2": float(train_r2),
                "r2_score": float(test_r2),
                "training_samples": int(len(train_data)),
                "test_samples": int(len(test_data)),
                "trained_at": datetime.now().isoformat()
            }
            
            logger.info(f"✓ ARIMA Training Complete!")
            logger.info(f"  Train Accuracy: {train_accuracy:.2f}% (MAPE: {train_mape:.2f}%)")
            logger.info(f"  Test Accuracy: {test_accuracy:.2f}% (MAPE: {test_mape:.2f}%)")
            logger.info(f"  Test RMSE: {test_rmse:.2f}")
            logger.info(f"  Test MAE: {test_mae:.2f}")
            logger.info(f"  Test R²: {test_r2:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training ARIMA: {e}", exc_info=True)
            raise
    
    async def train_all_models(self, force: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Train all models with real data. Use cache if available and valid.
        
        Args:
            force: If True, ignore cache and retrain all models
            
        Returns:
            Dictionary with model results
        """
        print("\n" + "=" * 80, flush=True)
        print("🚀 STARTING REAL MODEL TRAINING", flush=True)
        print("=" * 80, flush=True)
        print(f"⚙️  Force retrain: {force}", flush=True)
        print(f"📁 Cache directory: {self.cache_dir}", flush=True)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print("=" * 80 + "\n", flush=True)
        
        logger.info("=" * 80)
        logger.info("🚀 STARTING REAL MODEL TRAINING")
        logger.info("=" * 80)
        logger.info(f"⚙️  Force retrain: {force}")
        logger.info(f"📁 Cache directory: {self.cache_dir}")
        logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        self.training_status = {
            "status": "training",
            "progress": 0,
            "current_model": None,
            "models_completed": [],
            "error": None,
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        results = []
        model_trainers = [
            ("LSTM", self.train_lstm_model),
            ("Linear Regression", self.train_linear_regression),
            ("SVM", self.train_svm_model),
            ("ARIMA", self.train_arima_model)
        ]
        
        total_models = len(model_trainers)
        print(f"📊 Will train {total_models} models: {', '.join([m[0] for m in model_trainers])}\n", flush=True)
        logger.info(f"\n📊 Will train {total_models} models: {', '.join([m[0] for m in model_trainers])}\n")
        
        for idx, (model_name, trainer_func) in enumerate(model_trainers):
            try:
                # Check cache
                if not force and self.is_cache_valid(model_name):
                    print("=" * 80, flush=True)
                    print(f"💾 [{idx+1}/{total_models}] Loading {model_name} from cache...", flush=True)
                    print("=" * 80, flush=True)
                    
                    logger.info("=" * 80)
                    logger.info(f"💾 [{idx+1}/{total_models}] Loading {model_name} from cache...")
                    logger.info("=" * 80)
                    cached_data = self.load_cached_model(model_name)
                    if cached_data:
                        cached_data['status'] = 'cached'
                        results.append(cached_data)
                        self.training_status["models_completed"].append(model_name)
                        self.training_status["progress"] = int(((idx + 1) / total_models) * 100)
                        
                        print(f"✅ {model_name} loaded from cache successfully", flush=True)
                        print(f"📈 Progress: {self.training_status['progress']}%\n", flush=True)
                        
                        logger.info(f"✅ {model_name} loaded from cache successfully")
                        logger.info(f"📈 Progress: {self.training_status['progress']}%\n")
                        continue
                
                # Train model
                self.training_status["current_model"] = model_name
                self.training_status["progress"] = int((idx / total_models) * 100)
                
                print("=" * 80, flush=True)
                print(f"🔧 [{idx+1}/{total_models}] Training {model_name}", flush=True)
                print("=" * 80, flush=True)
                print(f"📈 Progress: {self.training_status['progress']}%", flush=True)
                print(f"⏳ Starting training... (this may take 10-30 seconds)", flush=True)
                
                logger.info("=" * 80)
                logger.info(f"🔧 [{idx+1}/{total_models}] Training {model_name}")
                logger.info("=" * 80)
                logger.info(f"📈 Progress: {self.training_status['progress']}%")
                logger.info(f"⏳ Starting training... (this may take 10-30 seconds)")
                
                metrics = await trainer_func()
                metrics['status'] = 'trained'
                
                # Save to cache
                print(f"💾 Saving {model_name} to cache...", flush=True)
                logger.info(f"💾 Saving {model_name} to cache...")
                self.save_model_cache(model_name, metrics)
                
                results.append(metrics)
                self.training_status["models_completed"].append(model_name)
                
                # Update progress
                self.training_status["progress"] = int(((idx + 1) / total_models) * 100)
                
                print(f"✅ {model_name} trained successfully!", flush=True)
                print(f"📊 Accuracy: {metrics.get('accuracy', 'N/A')}%", flush=True)
                print(f"📈 Overall Progress: {self.training_status['progress']}%", flush=True)
                print("", flush=True)
                
                logger.info(f"✅ {model_name} trained successfully!")
                logger.info(f"📊 Accuracy: {metrics.get('accuracy', 'N/A')}%")
                logger.info(f"📈 Overall Progress: {self.training_status['progress']}%")
                logger.info("")
                
            except Exception as e:
                print("=" * 80, flush=True)
                print(f"❌ Failed to train {model_name}: {e}", flush=True)
                print("=" * 80, flush=True)
                
                logger.error("=" * 80)
                logger.error(f"❌ Failed to train {model_name}: {e}")
                logger.error("=" * 80)
                logger.error("Full traceback:", exc_info=True)
                # Add error result
                results.append({
                    "model": model_name,
                    "error": str(e),
                    "status": "failed"
                })
        
        self.training_status["status"] = "completed"
        self.training_status["progress"] = 100
        self.training_status["completed_at"] = datetime.now().isoformat()
        self.training_status["current_model"] = None
        
        # Summary
        print("\n" + "=" * 80, flush=True)
        print("✅ ALL MODELS TRAINING COMPLETED", flush=True)
        print("=" * 80, flush=True)
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"✓ Models trained: {len([r for r in results if r.get('status') != 'failed'])}/{total_models}", flush=True)
        if any(r.get('status') == 'failed' for r in results):
            failed = [r['model'] for r in results if r.get('status') == 'failed']
            print(f"⚠️  Failed models: {', '.join(failed)}", flush=True)
        print("=" * 80 + "\n", flush=True)
        
        logger.info("=" * 80)
        logger.info("✅ ALL MODELS TRAINING COMPLETED")
        logger.info("=" * 80)
        logger.info(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"✓ Models trained: {len([r for r in results if r.get('status') != 'failed'])}/{total_models}")
        if any(r.get('status') == 'failed' for r in results):
            failed = [r['model'] for r in results if r.get('status') == 'failed']
            logger.warning(f"⚠️  Failed models: {', '.join(failed)}")
        logger.info("=" * 80)
        
        return {"models": results}
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status."""
        return self.training_status.copy()


# Global instance
_training_service = None

def get_training_service() -> MLTrainingService:
    """Get or create global training service instance."""
    global _training_service
    if _training_service is None:
        _training_service = MLTrainingService()
    return _training_service
