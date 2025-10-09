"""
LSTM Deep Learning Model

This module implements LSTM (Long Short-Term Memory) neural networks for
time series price prediction with sequence learning.

Author: QuantFin Team
Date: 2025-10-09
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import pickle
import warnings

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')

# Configure GPU settings
try:
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        # Enable memory growth to prevent TensorFlow from allocating all GPU memory
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logger.info(f"✅ GPU enabled: {len(gpus)} device(s) available")
    else:
        logger.info("ℹ️  No GPU detected, using CPU")
except Exception as e:
    logger.warning(f"GPU configuration failed: {e}, falling back to CPU")


class LSTMModel:
    """
    LSTM neural network model for time series price prediction.
    
    Uses sequential window-based learning with multi-layer LSTM architecture.
    """
    
    def __init__(self, symbol: str, models_dir: str = "models/lstm"):
        """
        Initialize the LSTMModel.
        
        Args:
            symbol (str): Stock or sector symbol
            models_dir (str): Directory to save/load models
        """
        self.symbol = symbol
        self.models_dir = Path(models_dir)
        self.model_path = self.models_dir / symbol
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.scaler_X = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
        self.training_metrics: Dict = {}
        self.sequence_length: int = 60
        
        logger.info(f"LSTMModel initialized for {symbol}")
    
    def _create_sequences(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sequence_length: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequential windows for LSTM input.
        
        Args:
            X (np.ndarray): Feature matrix
            y (np.ndarray): Target values
            sequence_length (int): Length of each sequence window
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (X_sequences, y_sequences)
        """
        X_sequences, y_sequences = [], []
        
        for i in range(len(X) - sequence_length):
            X_sequences.append(X[i:i + sequence_length])
            y_sequences.append(y[i + sequence_length])
        
        return np.array(X_sequences), np.array(y_sequences)
    
    def _build_model(
        self,
        input_shape: Tuple,
        lstm_units_1: int = 128,
        lstm_units_2: int = 64,
        dropout_rate: float = 0.2,
        dense_units: int = 32
    ) -> Sequential:
        """
        Build LSTM neural network architecture.
        
        Args:
            input_shape (Tuple): Shape of input sequences (timesteps, features)
            lstm_units_1 (int): Units in first LSTM layer
            lstm_units_2 (int): Units in second LSTM layer
            dropout_rate (float): Dropout rate for regularization
            dense_units (int): Units in dense layer
        
        Returns:
            Sequential: Compiled Keras model
        """
        model = Sequential([
            LSTM(
                lstm_units_1,
                return_sequences=True,
                input_shape=input_shape,
                name='lstm_1'
            ),
            Dropout(dropout_rate, name='dropout_1'),
            
            LSTM(
                lstm_units_2,
                return_sequences=False,
                name='lstm_2'
            ),
            Dropout(dropout_rate, name='dropout_2'),
            
            Dense(dense_units, activation='relu', name='dense_1'),
            Dense(1, name='output')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        logger.debug(f"Built LSTM model with architecture: {lstm_units_1}-{lstm_units_2}-{dense_units}")
        
        return model
    
    def train(
        self,
        df: pd.DataFrame,
        sequence_length: int = 60,
        test_size: float = 0.2,
        epochs: int = 50,
        batch_size: int = 32,
        lstm_units_1: int = 128,
        lstm_units_2: int = 64,
        dropout_rate: float = 0.2,
        patience: int = 10
    ) -> Dict:
        """
        Train the LSTM model.
        
        Args:
            df (pd.DataFrame): DataFrame with features and 'Close' column
            sequence_length (int): Length of input sequences
            test_size (float): Proportion of data for testing
            epochs (int): Maximum training epochs
            batch_size (int): Batch size for training
            lstm_units_1 (int): Units in first LSTM layer
            lstm_units_2 (int): Units in second LSTM layer
            dropout_rate (float): Dropout rate
            patience (int): Early stopping patience
        
        Returns:
            Dict: Training metrics and results
        """
        logger.info(f"Starting LSTM training for {self.symbol}...")
        start_time = datetime.now()
        
        self.sequence_length = sequence_length
        
        # Select features
        feature_columns = [col for col in df.columns if col not in ['Date', 'Datetime']]
        if 'Close' not in feature_columns:
            raise ValueError("DataFrame must contain 'Close' column")
        
        # Prepare data
        data = df[feature_columns].values
        
        # Handle infinity values (critical for LSTM)
        if np.any(np.isinf(data)):
            logger.warning("Infinity values detected, replacing with NaN")
            data = np.where(np.isinf(data), np.nan, data)
        
        # Handle missing values
        if np.any(np.isnan(data)):
            logger.warning("NaN values detected, filling with forward-fill")
            df_temp = pd.DataFrame(data, columns=feature_columns)
            df_temp = df_temp.fillna(method='ffill').fillna(method='bfill')
            # If still NaN (all column is NaN), fill with 0
            df_temp = df_temp.fillna(0)
            data = df_temp.values
        
        # Final check for invalid values
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            logger.error("Still have NaN or infinity values after cleaning")
            raise ValueError("Data contains NaN or infinity after preprocessing")
        
        # Clip extreme outliers (values beyond 5 standard deviations)
        for i in range(data.shape[1]):
            col_data = data[:, i]
            mean_val = np.mean(col_data)
            std_val = np.std(col_data)
            if std_val > 0:
                data[:, i] = np.clip(col_data, mean_val - 5*std_val, mean_val + 5*std_val)
        
        logger.info("Data preprocessing complete - no NaN/inf values, outliers clipped")
        
        # Target is next-day close price
        target_idx = feature_columns.index('Close')
        X = data[:, :]
        y = data[:, target_idx]
        
        # Scale data
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Create sequences
        X_seq, y_seq = self._create_sequences(X_scaled, y_scaled, sequence_length)
        
        logger.info(f"Created {len(X_seq)} sequences of length {sequence_length}")
        
        # Split into train and test
        split_idx = int(len(X_seq) * (1 - test_size))
        X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
        y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]
        
        logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
        
        # Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self._build_model(
            input_shape=input_shape,
            lstm_units_1=lstm_units_1,
            lstm_units_2=lstm_units_2,
            dropout_rate=dropout_rate
        )
        
        logger.info("Model architecture:")
        self.model.summary(print_fn=logger.debug)
        
        # Callbacks
        checkpoint_path = str(self.model_path / f"checkpoint_{self.symbol}.h5")
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                checkpoint_path,
                monitor='val_loss',
                save_best_only=True,
                verbose=0
            )
        ]
        
        # Train model
        logger.info(f"Training LSTM for {epochs} epochs...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=0
        )
        
        # Evaluate on test set
        y_pred_scaled = self.model.predict(X_test, verbose=0).flatten()
        
        # Inverse transform predictions
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        y_test_actual = self.scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()
        
        # Calculate metrics
        mse = mean_squared_error(y_test_actual, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_actual, y_pred)
        r2 = r2_score(y_test_actual, y_pred)
        mape = np.mean(np.abs((y_test_actual - y_pred) / y_test_actual)) * 100
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Store metrics
        self.training_metrics = {
            'symbol': self.symbol,
            'sequence_length': sequence_length,
            'n_features': X.shape[1],
            'n_samples': len(X),
            'n_sequences': len(X_seq),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'epochs_run': len(history.history['loss']),
            'final_train_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'test_mse': float(mse),
            'test_rmse': float(rmse),
            'test_mae': float(mae),
            'test_r2': float(r2),
            'test_mape': float(mape),
            'lstm_units': [lstm_units_1, lstm_units_2],
            'dropout_rate': dropout_rate,
            'training_time_seconds': training_time,
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"LSTM training completed for {self.symbol}")
        logger.info(f"  Epochs: {len(history.history['loss'])}")
        logger.info(f"  Test RMSE: {rmse:.4f}")
        logger.info(f"  Test R²: {r2:.4f}")
        logger.info(f"  Test MAPE: {mape:.2f}%")
        logger.info(f"  Training time: {training_time:.2f}s")
        
        return self.training_metrics
    
    def predict(self, df: pd.DataFrame, steps: int = 1) -> Dict:
        """
        Make predictions using the trained LSTM model.
        
        Args:
            df (pd.DataFrame): DataFrame with features
            steps (int): Number of steps to predict (only 1 supported currently)
        
        Returns:
            Dict: Prediction results
        """
        if self.model is None:
            raise ValueError(f"Model not trained for {self.symbol}. Call train() first.")
        
        # Select features
        feature_columns = [col for col in df.columns if col not in ['Date', 'Datetime']]
        
        # Get last sequence_length rows
        if len(df) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} rows for prediction")
        
        data = df[feature_columns].iloc[-self.sequence_length:].values
        
        # Handle missing values
        if np.any(np.isnan(data)):
            data = pd.DataFrame(data).fillna(method='ffill').fillna(method='bfill').values
        
        # Scale data
        data_scaled = self.scaler_X.transform(data)
        
        # Reshape for LSTM input: (1, sequence_length, n_features)
        X_input = data_scaled.reshape(1, self.sequence_length, data_scaled.shape[1])
        
        # Predict
        y_pred_scaled = self.model.predict(X_input, verbose=0).flatten()
        
        # Inverse transform
        expected_price = float(self.scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()[0])
        
        # Calculate confidence based on training performance
        test_r2 = self.training_metrics.get('test_r2', 0.5)
        test_mape = self.training_metrics.get('test_mape', 10.0)
        
        # Confidence score: combine R² and inverse MAPE
        confidence = (test_r2 + (1 - min(test_mape / 100, 1))) / 2
        confidence = max(0.0, min(confidence, 1.0))
        
        result = {
            'symbol': self.symbol,
            'expected_price': expected_price,
            'model_confidence': float(confidence),
            'prediction_date': datetime.now().isoformat(),
            'model_type': 'LSTM',
            'sequence_length': self.sequence_length,
            'test_r2': self.training_metrics.get('test_r2'),
            'test_mape': self.training_metrics.get('test_mape')
        }
        
        logger.debug(f"LSTM prediction for {self.symbol}: price={expected_price:.2f}, confidence={confidence:.2f}")
        
        return result
    
    def save_model(self, version: Optional[str] = None) -> str:
        """
        Save the trained model to disk.
        
        Args:
            version (str, optional): Version string. If None, uses timestamp.
        
        Returns:
            str: Path to saved model
        """
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save Keras model
        model_filename = f"model_{version}.h5"
        model_filepath = self.model_path / model_filename
        self.model.save(str(model_filepath))
        
        # Save scalers and metadata
        metadata = {
            'scaler_X': self.scaler_X,
            'scaler_y': self.scaler_y,
            'training_metrics': self.training_metrics,
            'sequence_length': self.sequence_length,
            'version': version
        }
        
        metadata_filename = f"metadata_{version}.pkl"
        metadata_filepath = self.model_path / metadata_filename
        
        with open(metadata_filepath, 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Model saved to {model_filepath}")
        logger.info(f"Metadata saved to {metadata_filepath}")
        
        # Also save latest version
        latest_model_path = self.model_path / "model_latest.h5"
        latest_metadata_path = self.model_path / "metadata_latest.pkl"
        
        self.model.save(str(latest_model_path))
        with open(latest_metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        return str(model_filepath)
    
    def load_model(self, version: str = "latest") -> Dict:
        """
        Load a trained model from disk.
        
        Args:
            version (str): Version to load. Use "latest" for most recent.
        
        Returns:
            Dict: Training metrics of loaded model
        """
        if version == "latest":
            model_filepath = self.model_path / "model_latest.h5"
            metadata_filepath = self.model_path / "metadata_latest.pkl"
        else:
            model_filepath = self.model_path / f"model_{version}.h5"
            metadata_filepath = self.model_path / f"metadata_{version}.pkl"
        
        if not model_filepath.exists():
            raise FileNotFoundError(f"Model file not found: {model_filepath}")
        if not metadata_filepath.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_filepath}")
        
        # Load Keras model
        self.model = load_model(str(model_filepath))
        
        # Load metadata
        with open(metadata_filepath, 'rb') as f:
            metadata = pickle.load(f)
        
        self.scaler_X = metadata['scaler_X']
        self.scaler_y = metadata['scaler_y']
        self.training_metrics = metadata['training_metrics']
        self.sequence_length = metadata['sequence_length']
        
        logger.info(f"Model loaded from {model_filepath}")
        logger.info(f"  Version: {metadata.get('version', 'unknown')}")
        logger.info(f"  Test R²: {self.training_metrics.get('test_r2', 'N/A')}")
        logger.info(f"  Sequence length: {self.sequence_length}")
        
        return self.training_metrics
