"""
ARIMA/SARIMA Time Series Forecasting Model

This module implements ARIMA and SARIMA models for time series price forecasting
with automatic parameter selection using AIC/BIC.

Author: QuantFin Team
Date: 2025-10-09
"""

import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime
import pickle
import warnings

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import itertools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings from statsmodels
warnings.filterwarnings('ignore')


class ARIMAModel:
    """
    ARIMA/SARIMA model for time series price forecasting.
    
    Automatically selects optimal (p, d, q) parameters using AIC/BIC criteria.
    """
    
    def __init__(self, symbol: str, models_dir: str = "models/arima"):
        """
        Initialize the ARIMAModel.
        
        Args:
            symbol (str): Stock or sector symbol
            models_dir (str): Directory to save/load models
        """
        self.symbol = symbol
        self.models_dir = Path(models_dir)
        self.model_path = self.models_dir / symbol
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.model_fit = None
        self.best_order: Optional[Tuple] = None
        self.training_metrics: Dict = {}
        self.original_prices: Optional[pd.Series] = None
        
        logger.info(f"ARIMAModel initialized for {symbol}")
    
    def _check_stationarity(self, series: pd.Series) -> Tuple[bool, Dict]:
        """
        Check if time series is stationary using Augmented Dickey-Fuller test.
        
        Args:
            series (pd.Series): Time series data
        
        Returns:
            Tuple[bool, Dict]: (is_stationary, test_results)
        """
        result = adfuller(series.dropna())
        
        test_results = {
            'adf_statistic': result[0],
            'p_value': result[1],
            'n_lags': result[2],
            'n_obs': result[3],
            'critical_values': result[4]
        }
        
        is_stationary = result[1] < 0.05  # p-value < 0.05
        
        logger.debug(f"Stationarity test: p-value={result[1]:.4f}, stationary={is_stationary}")
        
        return is_stationary, test_results
    
    def _find_best_order(
        self,
        series: pd.Series,
        max_p: int = 5,
        max_d: int = 2,
        max_q: int = 5,
        criterion: str = 'aic'
    ) -> Tuple[int, int, int]:
        """
        Find the best ARIMA order using grid search and AIC/BIC.
        
        Args:
            series (pd.Series): Time series data
            max_p (int): Maximum AR order to try
            max_d (int): Maximum differencing order to try
            max_q (int): Maximum MA order to try
            criterion (str): 'aic' or 'bic'
        
        Returns:
            Tuple[int, int, int]: Best (p, d, q) order
        """
        logger.info("Searching for best ARIMA order...")
        
        best_score = np.inf
        best_order = None
        
        # Generate all combinations of p, d, q
        p_range = range(0, max_p + 1)
        d_range = range(0, max_d + 1)
        q_range = range(0, max_q + 1)
        
        total_combinations = (max_p + 1) * (max_d + 1) * (max_q + 1)
        logger.info(f"Testing {total_combinations} parameter combinations...")
        
        tested = 0
        for p, d, q in itertools.product(p_range, d_range, q_range):
            try:
                model = ARIMA(series, order=(p, d, q))
                model_fit = model.fit()
                
                score = model_fit.aic if criterion == 'aic' else model_fit.bic
                
                if score < best_score:
                    best_score = score
                    best_order = (p, d, q)
                
                tested += 1
                if tested % 20 == 0:
                    logger.debug(f"Tested {tested}/{total_combinations} combinations...")
                
            except Exception as e:
                continue
        
        if best_order is None:
            logger.warning("Could not find optimal order, using default (1, 1, 1)")
            best_order = (1, 1, 1)
        
        logger.info(f"Best order found: {best_order} with {criterion.upper()}={best_score:.2f}")
        
        return best_order
    
    def train(
        self,
        df: pd.DataFrame,
        auto_order: bool = True,
        order: Optional[Tuple] = None,
        max_p: int = 5,
        max_d: int = 2,
        max_q: int = 5,
        test_size: int = 21
    ) -> Dict:
        """
        Train the ARIMA model.
        
        Args:
            df (pd.DataFrame): DataFrame with Date and Close columns
            auto_order (bool): Automatically find best order
            order (Tuple, optional): Manual order (p, d, q) if auto_order=False
            max_p (int): Max AR order for auto search
            max_d (int): Max differencing order for auto search
            max_q (int): Max MA order for auto search
            test_size (int): Number of periods for validation
        
        Returns:
            Dict: Training metrics and results
        """
        logger.info(f"Starting ARIMA training for {self.symbol}...")
        start_time = datetime.now()
        
        # Extract price series
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
        
        # Use log prices for better stability
        prices = df['Close'].values
        log_prices = np.log(prices)
        self.original_prices = pd.Series(prices, index=df.index if hasattr(df, 'index') else range(len(prices)))
        
        series = pd.Series(log_prices)
        
        # Check stationarity
        is_stationary, stationarity_test = self._check_stationarity(series)
        logger.info(f"Series stationarity: {is_stationary} (p-value={stationarity_test['p_value']:.4f})")
        
        # Split into train and validation
        train_series = series[:-test_size]
        test_series = series[-test_size:]
        
        # Find best order
        if auto_order:
            self.best_order = self._find_best_order(
                train_series,
                max_p=max_p,
                max_d=max_d,
                max_q=max_q
            )
        else:
            self.best_order = order if order else (1, 1, 1)
        
        logger.info(f"Using order: {self.best_order}")
        
        # Fit model
        logger.info("Fitting ARIMA model...")
        self.model = ARIMA(train_series, order=self.best_order)
        self.model_fit = self.model.fit()
        
        # Make predictions on validation set
        forecast_result = self.model_fit.forecast(steps=test_size)
        forecast_log = forecast_result
        
        # Convert back from log space
        forecast_prices = np.exp(forecast_log)
        actual_prices = np.exp(test_series.values)
        
        # Calculate metrics
        mse = np.mean((forecast_prices - actual_prices) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(forecast_prices - actual_prices))
        mape = np.mean(np.abs((actual_prices - forecast_prices) / actual_prices)) * 100
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Store metrics
        self.training_metrics = {
            'symbol': self.symbol,
            'order': self.best_order,
            'aic': float(self.model_fit.aic),
            'bic': float(self.model_fit.bic),
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'is_stationary': is_stationary,
            'stationarity_p_value': stationarity_test['p_value'],
            'n_samples': len(series),
            'test_size': test_size,
            'training_time_seconds': training_time,
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"ARIMA training completed for {self.symbol}")
        logger.info(f"  Order: {self.best_order}")
        logger.info(f"  AIC: {self.model_fit.aic:.2f}")
        logger.info(f"  Test RMSE: {rmse:.4f}")
        logger.info(f"  Test MAPE: {mape:.2f}%")
        logger.info(f"  Training time: {training_time:.2f}s")
        
        return self.training_metrics
    
    def forecast(self, steps: int = 21, alpha: float = 0.05) -> Dict:
        """
        Forecast future prices with confidence intervals.
        
        Args:
            steps (int): Number of periods to forecast
            alpha (float): Significance level for confidence interval (default 0.05 for 95% CI)
        
        Returns:
            Dict: Forecast results with expected_price and confidence_interval
        """
        if self.model_fit is None:
            raise ValueError(f"Model not trained for {self.symbol}. Call train() first.")
        
        # Get forecast
        forecast_result = self.model_fit.get_forecast(steps=steps)
        
        # Extract forecast and confidence intervals (in log space)
        forecast_log = forecast_result.predicted_mean
        conf_int_log = forecast_result.conf_int(alpha=alpha)
        
        # Convert back from log space
        forecast_prices = np.exp(forecast_log.values)
        lower_bound = np.exp(conf_int_log.iloc[:, 0].values)
        upper_bound = np.exp(conf_int_log.iloc[:, 1].values)
        
        # Calculate confidence based on interval width
        interval_width = upper_bound - lower_bound
        avg_price = forecast_prices.mean()
        relative_width = interval_width / avg_price
        
        # Narrower interval = higher confidence
        confidence = 1.0 - np.clip(relative_width.mean(), 0, 1)
        
        result = {
            'symbol': self.symbol,
            'forecast_steps': steps,
            'expected_price': forecast_prices.tolist(),
            'lower_bound': lower_bound.tolist(),
            'upper_bound': upper_bound.tolist(),
            'confidence_interval': f"{int((1-alpha)*100)}%",
            'model_confidence': float(confidence.mean()) if hasattr(confidence, 'mean') else float(confidence),
            'prediction_date': datetime.now().isoformat(),
            'model_type': 'ARIMA',
            'order': self.best_order,
            'aic': self.training_metrics.get('aic', None)
        }
        
        logger.debug(f"ARIMA forecast for {self.symbol}: {steps} steps, avg_price={forecast_prices.mean():.2f}")
        
        return result
    
    def save_model(self, version: Optional[str] = None) -> str:
        """
        Save the trained model to disk.
        
        Args:
            version (str, optional): Version string. If None, uses timestamp.
        
        Returns:
            str: Path to saved model
        """
        if self.model_fit is None:
            raise ValueError("No model to save. Train the model first.")
        
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_data = {
            'model_fit': self.model_fit,
            'best_order': self.best_order,
            'training_metrics': self.training_metrics,
            'original_prices': self.original_prices,
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
        
        self.model_fit = model_data['model_fit']
        self.best_order = model_data['best_order']
        self.training_metrics = model_data['training_metrics']
        self.original_prices = model_data.get('original_prices')
        
        logger.info(f"Model loaded from {filepath}")
        logger.info(f"  Version: {model_data.get('version', 'unknown')}")
        logger.info(f"  Order: {self.best_order}")
        logger.info(f"  AIC: {self.training_metrics.get('aic', 'N/A')}")
        
        return self.training_metrics
