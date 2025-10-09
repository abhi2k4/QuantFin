"""
Logistic Regression Model for Price Direction Classification

This module implements Logistic Regression to predict whether the price
will go up or down in the next period.

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
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogisticRegModel:
    """
    Logistic Regression model for price direction classification.
    
    Predicts whether the price will increase (1) or decrease (0) in the future.
    """
    
    def __init__(self, symbol: str, models_dir: str = "models/logreg"):
        """
        Initialize the LogisticRegModel.
        
        Args:
            symbol (str): Stock or sector symbol
            models_dir (str): Directory to save/load models
        """
        self.symbol = symbol
        self.models_dir = Path(models_dir)
        self.model_path = self.models_dir / symbol
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model: Optional[LogisticRegression] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: Optional[list] = None
        self.training_metrics: Dict = {}
        
        logger.info(f"LogisticRegModel initialized for {symbol}")
    
    def _prepare_features(self, df: pd.DataFrame, horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and target variable from DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with features
            horizon (int): Number of periods ahead to predict
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: Features (X) and target (y)
        """
        # Define feature columns
        exclude_cols = ['Date', 'Ticker', 'Sector', 'returns', 'price_direction']
        
        if self.feature_columns is None:
            self.feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        # Create binary target: 1 if price goes up, 0 if down
        df = df.copy()
        df['price_direction'] = (df['Close'].shift(-horizon) > df['Close']).astype(int)
        
        # Drop rows with NaN in target
        df_clean = df.dropna(subset=['price_direction'])
        
        # Extract features and target
        X = df_clean[self.feature_columns].values
        y = df_clean['price_direction'].values
        
        # Handle any remaining NaN in features
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        logger.debug(f"Prepared features shape: {X.shape}, target shape: {y.shape}")
        logger.debug(f"Class distribution: {np.bincount(y)}")
        
        return X, y
    
    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        C_range: list = [0.01, 0.1, 1.0, 10.0, 100.0],
        cv: int = 5,
        horizon: int = 1
    ) -> Dict:
        """
        Train the Logistic Regression model with hyperparameter tuning.
        
        Args:
            df (pd.DataFrame): DataFrame with features
            test_size (float): Proportion of data for testing
            C_range (list): Range of C values (inverse regularization) for GridSearchCV
            cv (int): Number of cross-validation folds
            horizon (int): Number of periods ahead to predict
        
        Returns:
            Dict: Training metrics and results
        """
        logger.info(f"Starting training for {self.symbol}...")
        start_time = datetime.now()
        
        # Prepare features
        X, y = self._prepare_features(df, horizon=horizon)
        
        logger.info(f"Training data shape: X={X.shape}, y={y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, stratify=None  # Time series
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Hyperparameter tuning
        logger.info("Performing hyperparameter tuning with GridSearchCV...")
        param_grid = {
            'C': C_range,
            'penalty': ['l2'],
            'solver': ['lbfgs'],
            'max_iter': [1000]
        }
        
        logreg = LogisticRegression(random_state=42, class_weight='balanced')
        grid_search = GridSearchCV(
            logreg,
            param_grid,
            cv=cv,
            scoring='roc_auc',
            n_jobs=-1
        )
        
        grid_search.fit(X_train_scaled, y_train)
        
        # Best model
        self.model = grid_search.best_estimator_
        best_C = grid_search.best_params_['C']
        
        logger.info(f"Best C: {best_C}")
        
        # Make predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        y_train_proba = self.model.predict_proba(X_train_scaled)[:, 1]
        y_test_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        train_precision = precision_score(y_train, y_train_pred, zero_division=0)
        test_precision = precision_score(y_test, y_test_pred, zero_division=0)
        
        train_recall = recall_score(y_train, y_train_pred, zero_division=0)
        test_recall = recall_score(y_test, y_test_pred, zero_division=0)
        
        train_f1 = f1_score(y_train, y_train_pred, zero_division=0)
        test_f1 = f1_score(y_test, y_test_pred, zero_division=0)
        
        train_auc = roc_auc_score(y_train, y_train_proba)
        test_auc = roc_auc_score(y_test, y_test_proba)
        
        conf_matrix = confusion_matrix(y_test, y_test_pred)
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Store metrics
        self.training_metrics = {
            'symbol': self.symbol,
            'best_C': best_C,
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'train_precision': train_precision,
            'test_precision': test_precision,
            'train_recall': train_recall,
            'test_recall': test_recall,
            'train_f1': train_f1,
            'test_f1': test_f1,
            'train_auc': train_auc,
            'test_auc': test_auc,
            'confusion_matrix': conf_matrix.tolist(),
            'n_features': X.shape[1],
            'n_samples': X.shape[0],
            'training_time_seconds': training_time,
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"Training completed for {self.symbol}")
        logger.info(f"  Test Accuracy: {test_accuracy:.4f}")
        logger.info(f"  Test Precision: {test_precision:.4f}")
        logger.info(f"  Test Recall: {test_recall:.4f}")
        logger.info(f"  Test F1: {test_f1:.4f}")
        logger.info(f"  Test AUC: {test_auc:.4f}")
        logger.info(f"  Training time: {training_time:.2f}s")
        
        return self.training_metrics
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Predict price direction (up/down).
        
        Args:
            df (pd.DataFrame): DataFrame with features (usually last row for latest prediction)
        
        Returns:
            Dict: Prediction results with probability_up and confidence
        """
        if self.model is None or self.scaler is None:
            raise ValueError(f"Model not trained for {self.symbol}. Call train() first.")
        
        # Prepare features (use only the last row for prediction)
        X = df[self.feature_columns].iloc[-1:].values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict probability
        proba = self.model.predict_proba(X_scaled)[0]
        probability_down = proba[0]
        probability_up = proba[1]
        
        # Predict class
        prediction = self.model.predict(X_scaled)[0]
        direction = "UP" if prediction == 1 else "DOWN"
        
        # Calculate confidence (distance from 0.5, scaled to 0-1)
        # Higher confidence when probability is closer to 0 or 1
        confidence = abs(probability_up - 0.5) * 2
        
        # Adjust confidence based on model performance
        base_confidence = self.training_metrics.get('test_auc', 0.5)
        adjusted_confidence = confidence * base_confidence
        
        result = {
            'symbol': self.symbol,
            'direction': direction,
            'probability_up': float(probability_up),
            'probability_down': float(probability_down),
            'confidence': float(adjusted_confidence),
            'raw_confidence': float(confidence),
            'prediction_date': datetime.now().isoformat(),
            'model_type': 'Logistic Regression',
            'test_auc': self.training_metrics.get('test_auc', None)
        }
        
        logger.debug(f"Prediction for {self.symbol}: {direction}, prob_up={probability_up:.4f}, confidence={adjusted_confidence:.4f}")
        
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
        logger.info(f"  Test AUC: {self.training_metrics.get('test_auc', 'N/A')}")
        
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
            'coefficient': self.model.coef_[0]
        })
        
        importance_df['abs_coefficient'] = importance_df['coefficient'].abs()
        importance_df = importance_df.sort_values('abs_coefficient', ascending=False)
        
        return importance_df
