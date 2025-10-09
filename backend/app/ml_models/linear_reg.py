"""
Ridge Regression Model for Stock Return Prediction

This module implements Ridge Regression to predict 21-day future returns
using features from the FeatureEngineer.

Author: QuantFin Team
Date: 2025-10-09
"""

import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime
import pickle

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinearRegModel:
    """
    Ridge Regression model for predicting 21-day future returns.
    
    This model uses regularized linear regression to predict future returns
    based on technical indicators and features.
    """
    
    def __init__(self, symbol: str, models_dir: str = "models/linear_reg"):
        """
        Initialize the LinearRegModel.
        
        Args:
            symbol (str): Stock or sector symbol
            models_dir (str): Directory to save/load models
        """
        self.symbol = symbol
        self.models_dir = Path(models_dir)
        self.model_path = self.models_dir / symbol
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model: Optional[Ridge] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: Optional[list] = None
        self.training_metrics: Dict = {}
        
        logger.info(f"LinearRegModel initialized for {symbol}")
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and target variable from DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with features
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: Features (X) and target (y)
        """
        # Define feature columns (exclude non-feature columns)
        exclude_cols = ['Date', 'Ticker', 'Sector', 'returns', 'future_return_21']
        
        if self.feature_columns is None:
            self.feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        # Calculate 21-day future return as target
        if 'future_return_21' not in df.columns:
            df = df.copy()
            df['future_return_21'] = df['Close'].pct_change(periods=21).shift(-21)
        
        # Drop rows with NaN in target
        df_clean = df.dropna(subset=['future_return_21'])
        
        # Extract features and target
        X = df_clean[self.feature_columns].values
        y = df_clean['future_return_21'].values
        
        # Handle any remaining NaN in features
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        logger.debug(f"Prepared features shape: {X.shape}, target shape: {y.shape}")
        
        return X, y
    
    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        alpha_range: list = [0.01, 0.1, 1.0, 10.0, 100.0],
        cv: int = 5
    ) -> Dict:
        """
        Train the Ridge Regression model with hyperparameter tuning.
        
        Args:
            df (pd.DataFrame): DataFrame with features
            test_size (float): Proportion of data for testing
            alpha_range (list): Range of alpha values for GridSearchCV
            cv (int): Number of cross-validation folds
        
        Returns:
            Dict: Training metrics and results
        """
        logger.info(f"Starting training for {self.symbol}...")
        start_time = datetime.now()
        
        # Prepare features
        X, y = self._prepare_features(df)
        
        logger.info(f"Training data shape: X={X.shape}, y={y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False  # Time series, no shuffle
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Hyperparameter tuning
        logger.info("Performing hyperparameter tuning with GridSearchCV...")
        param_grid = {'alpha': alpha_range}
        
        ridge = Ridge(random_state=42)
        grid_search = GridSearchCV(
            ridge,
            param_grid,
            cv=cv,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        grid_search.fit(X_train_scaled, y_train)
        
        # Best model
        self.model = grid_search.best_estimator_
        best_alpha = grid_search.best_params_['alpha']
        
        logger.info(f"Best alpha: {best_alpha}")
        
        # Make predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Store metrics
        self.training_metrics = {
            'symbol': self.symbol,
            'best_alpha': best_alpha,
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'n_features': X.shape[1],
            'n_samples': X.shape[0],
            'training_time_seconds': training_time,
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"Training completed for {self.symbol}")
        logger.info(f"  Test MSE: {test_mse:.6f}")
        logger.info(f"  Test MAE: {test_mae:.6f}")
        logger.info(f"  Test R²: {test_r2:.4f}")
        logger.info(f"  Training time: {training_time:.2f}s")
        
        return self.training_metrics
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Predict 21-day future returns.
        
        Args:
            df (pd.DataFrame): DataFrame with features (usually last row for latest prediction)
        
        Returns:
            Dict: Prediction results with expected_return and confidence_score
        """
        if self.model is None or self.scaler is None:
            raise ValueError(f"Model not trained for {self.symbol}. Call train() first.")
        
        # Prepare features (use only the last row for prediction)
        X = df[self.feature_columns].iloc[-1:].values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        expected_return = self.model.predict(X_scaled)[0]
        
        # Calculate confidence score (based on model's R² and prediction magnitude)
        # Higher R² and lower predicted volatility = higher confidence
        base_confidence = max(0.0, self.training_metrics.get('test_r2', 0.5))
        
        # Adjust confidence based on prediction magnitude (more extreme = less confident)
        magnitude_penalty = min(1.0, 1.0 / (1.0 + abs(expected_return) * 10))
        confidence_score = base_confidence * magnitude_penalty
        
        # Ensure confidence is between 0 and 1
        confidence_score = np.clip(confidence_score, 0.0, 1.0)
        
        result = {
            'symbol': self.symbol,
            'expected_return': float(expected_return),
            'confidence_score': float(confidence_score),
            'prediction_date': datetime.now().isoformat(),
            'model_type': 'Ridge Regression',
            'test_r2': self.training_metrics.get('test_r2', None)
        }
        
        logger.debug(f"Prediction for {self.symbol}: return={expected_return:.4f}, confidence={confidence_score:.4f}")
        
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
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'training_metrics': self.training_metrics,
            'version': version
        }
        
        filename = f"model_{version}.pkl"
        filepath = self.model_path / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
        
        # Also save latest version
        latest_path = self.model_path / "model_latest.pkl"
        with open(latest_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        return str(filepath)
    
    def load_model(self, version: str = "latest") -> Dict:
        """
        Load a trained model from disk.
        
        Args:
            version (str): Version to load. Use "latest" for most recent.
        
        Returns:
            Dict: Training metrics of loaded model
        """
        if version == "latest":
            filepath = self.model_path / "model_latest.pkl"
        else:
            filepath = self.model_path / f"model_{version}.pkl"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.training_metrics = model_data['training_metrics']
        
        logger.info(f"Model loaded from {filepath}")
        logger.info(f"  Version: {model_data.get('version', 'unknown')}")
        logger.info(f"  Test R²: {self.training_metrics.get('test_r2', 'N/A')}")
        
        return self.training_metrics
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance (coefficients) from the model.
        
        Returns:
            pd.DataFrame: Feature names and their coefficients
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'coefficient': self.model.coef_
        })
        
        importance_df['abs_coefficient'] = importance_df['coefficient'].abs()
        importance_df = importance_df.sort_values('abs_coefficient', ascending=False)
        
        return importance_df
