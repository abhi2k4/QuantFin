"""
Prediction Service Module

This module orchestrates predictions from all ML models and provides ensemble
predictions with portfolio allocation strategies.

Author: QuantFin Team
Date: 2025-10-09
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings

import pandas as pd
import numpy as np
from scipy.optimize import minimize

from app.services.feature_engineer import FeatureEngineer
from app.ml_models.linear_reg import LinearRegModel
from app.ml_models.logreg import LogisticRegModel
from app.ml_models.svm_model import SVMModel
# from app.ml_models.arima_model import ARIMAModel  # TODO: ARIMA model not yet implemented
# from app.ml_models.lstm_model import LSTMModel  # Lazy load to avoid TensorFlow import issues

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


class PredictionService:
    """
    Service for orchestrating ML model predictions and portfolio allocation.
    
    Provides ensemble predictions and multiple portfolio optimization strategies.
    """
    
    def __init__(
        self,
        feature_engineer: FeatureEngineer,
        models_base_dir: str = "models"
    ):
        """
        Initialize the PredictionService.
        
        Args:
            feature_engineer (FeatureEngineer): Feature engineering service
            models_base_dir (str): Base directory for model storage
        """
        self.feature_engineer = feature_engineer
        self.models_base_dir = Path(models_base_dir)
        
        self.loaded_models: Dict[str, Dict] = {
            'linear_reg': {},
            'logreg': {},
            'svm': {},
            'arima': {},
            'lstm': {}
        }
        
        logger.info("PredictionService initialized")
    
    def load_models(
        self,
        symbols: List[str],
        models: List[str] = ["linear_reg", "logreg", "svm", "arima", "lstm"],
        version: str = "latest"
    ) -> Dict[str, int]:
        """
        Load trained models for specified symbols.
        
        Args:
            symbols (List[str]): List of stock/sector symbols
            models (List[str]): List of model types to load
            version (str): Model version to load
        
        Returns:
            Dict[str, int]: Number of models loaded per type
        """
        logger.info(f"Loading models for {len(symbols)} symbols...")
        
        load_stats = {model_type: 0 for model_type in models}
        
        for symbol in symbols:
            for model_type in models:
                try:
                    if model_type == 'linear_reg':
                        model = LinearRegModel(
                            symbol=symbol,
                            models_dir=str(self.models_base_dir / "linear_reg")
                        )
                        model.load_model(version)
                        self.loaded_models['linear_reg'][symbol] = model
                        load_stats['linear_reg'] += 1
                    
                    elif model_type == 'logreg':
                        model = LogisticRegModel(
                            symbol=symbol,
                            models_dir=str(self.models_base_dir / "logreg")
                        )
                        model.load_model(version)
                        self.loaded_models['logreg'][symbol] = model
                        load_stats['logreg'] += 1
                    
                    elif model_type == 'svm':
                        model = SVMModel(
                            symbol=symbol,
                            models_dir=str(self.models_base_dir / "svm")
                        )
                        model.load_model(version)
                        self.loaded_models['svm'][symbol] = model
                        load_stats['svm'] += 1
                    
                    # elif model_type == 'arima':
                    #     model = ARIMAModel(
                    #         symbol=symbol,
                    #         models_dir=str(self.models_base_dir / "arima")
                    #     )
                    #     model.load_model(version)
                    #     self.loaded_models['arima'][symbol] = model
                    #     load_stats['arima'] += 1
                    
                    elif model_type == 'lstm':
                        from app.ml_models.lstm_model import LSTMModel  # Lazy load
                        model = LSTMModel(
                            symbol=symbol,
                            models_dir=str(self.models_base_dir / "lstm")
                        )
                        model.load_model(version)
                        self.loaded_models['lstm'][symbol] = model
                        load_stats['lstm'] += 1
                
                except Exception as e:
                    logger.warning(f"Failed to load {model_type} for {symbol}: {e}")
                    continue
        
        logger.info(f"Models loaded: {load_stats}")
        return load_stats
    
    def _get_single_model_prediction(
        self,
        symbol: str,
        model_type: str,
        df: pd.DataFrame,
        horizon: int = 21
    ) -> Optional[Dict]:
        """
        Get prediction from a single model type.
        
        Args:
            symbol (str): Stock/sector symbol
            model_type (str): Type of model
            df (pd.DataFrame): DataFrame with features
            horizon (int): Prediction horizon in days
        
        Returns:
            Optional[Dict]: Prediction result or None if failed
        """
        try:
            if symbol not in self.loaded_models[model_type]:
                logger.warning(f"No {model_type} model loaded for {symbol}")
                return None
            
            model = self.loaded_models[model_type][symbol]
            
            current_price = float(df['Close'].iloc[-1])
            
            if model_type in ['linear_reg']:
                result = model.predict(df)
                expected_return = result['expected_return']
                expected_price = current_price * (1 + expected_return)
                confidence = result['confidence_score']
            
            elif model_type in ['logreg', 'svm']:
                result = model.predict(df)
                probability_up = result['probability_up']
                # Convert probability to expected return estimate
                # Assuming symmetric +/- 5% move
                expected_return = (probability_up - 0.5) * 0.10
                expected_price = current_price * (1 + expected_return)
                confidence = result['confidence']
            
            elif model_type == 'arima':
                result = model.forecast(steps=horizon)
                expected_prices = result['expected_price']
                expected_price = float(expected_prices[-1])
                expected_return = (expected_price / current_price) - 1
                confidence = result['model_confidence']
            
            elif model_type == 'lstm':
                result = model.predict(df)
                expected_price = result['expected_price']
                expected_return = (expected_price / current_price) - 1
                confidence = result['model_confidence']
            
            else:
                return None
            
            return {
                'symbol': symbol,
                'model': model_type.upper(),
                'current_price': round(current_price, 2),
                'expected_price': round(expected_price, 2),
                'expected_return': round(expected_return, 4),
                'confidence': round(confidence, 2),
                'prediction_date': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error in {model_type} prediction for {symbol}: {e}")
            return None
    
    def predict(
        self,
        symbols: List[str],
        date: Optional[str] = None,
        horizon: int = 21,
        model: str = "ensemble"
    ) -> Dict:
        """
        Generate predictions for multiple symbols.
        
        Args:
            symbols (List[str]): List of symbols to predict
            date (str, optional): Prediction date (defaults to today)
            horizon (int): Prediction horizon in days
            model (str): Model type or "ensemble" for all models
        
        Returns:
            Dict: Predictions and portfolio allocation
        """
        logger.info(f"Starting predictions for {len(symbols)} symbols using {model} model(s)...")
        start_time = datetime.now()
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        all_predictions = []
        
        # Determine which models to use
        if model == "ensemble":
            model_types = ['linear_reg', 'logreg', 'svm', 'arima', 'lstm']
        else:
            model_types = [model]
        
        # Generate predictions for each symbol
        for symbol in symbols:
            try:
                # Get feature-engineered data
                df = self.feature_engineer.compute_features(symbol)
                
                if df is None or len(df) < 100:
                    logger.warning(f"Insufficient data for {symbol}, skipping...")
                    continue
                
                symbol_predictions = []
                
                # Get predictions from each model type
                for model_type in model_types:
                    pred = self._get_single_model_prediction(
                        symbol=symbol,
                        model_type=model_type,
                        df=df,
                        horizon=horizon
                    )
                    
                    if pred is not None:
                        symbol_predictions.append(pred)
                
                # Add individual model predictions
                all_predictions.extend(symbol_predictions)
                
                # Create ensemble prediction if multiple models used
                if len(symbol_predictions) > 1:
                    ensemble_pred = self._create_ensemble_prediction(symbol_predictions)
                    all_predictions.append(ensemble_pred)
            
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        # Generate portfolio allocation
        portfolio = self._generate_portfolio_allocation(all_predictions, strategy="model_weighted")
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Predictions completed in {elapsed_time:.2f}s")
        
        return {
            'predictions': all_predictions,
            'portfolio': portfolio,
            'metadata': {
                'prediction_date': date,
                'horizon_days': horizon,
                'model_type': model,
                'symbols_processed': len(symbols),
                'predictions_generated': len(all_predictions),
                'processing_time_seconds': round(elapsed_time, 2)
            }
        }
    
    def _create_ensemble_prediction(self, predictions: List[Dict]) -> Dict:
        """
        Create an ensemble prediction from multiple model predictions.
        
        Args:
            predictions (List[Dict]): List of predictions from different models
        
        Returns:
            Dict: Ensemble prediction
        """
        if not predictions:
            return None
        
        symbol = predictions[0]['symbol']
        current_price = predictions[0]['current_price']
        
        # Weighted average based on confidence
        total_weight = sum(p['confidence'] for p in predictions)
        
        if total_weight == 0:
            # Fallback to simple average
            expected_return = np.mean([p['expected_return'] for p in predictions])
            confidence = np.mean([p['confidence'] for p in predictions])
        else:
            expected_return = sum(
                p['expected_return'] * p['confidence'] for p in predictions
            ) / total_weight
            confidence = total_weight / len(predictions)
        
        expected_price = current_price * (1 + expected_return)
        
        return {
            'symbol': symbol,
            'model': 'ENSEMBLE',
            'current_price': round(current_price, 2),
            'expected_price': round(expected_price, 2),
            'expected_return': round(expected_return, 4),
            'confidence': round(confidence, 2),
            'prediction_date': datetime.now().isoformat(),
            'models_used': [p['model'] for p in predictions]
        }
    
    def _generate_portfolio_allocation(
        self,
        predictions: List[Dict],
        strategy: str = "model_weighted"
    ) -> Dict:
        """
        Generate portfolio allocation from predictions.
        
        Args:
            predictions (List[Dict]): List of all predictions
            strategy (str): Allocation strategy
        
        Returns:
            Dict: Portfolio allocation
        """
        # Filter to get only ensemble or best predictions per symbol
        symbol_predictions = {}
        for pred in predictions:
            symbol = pred['symbol']
            if pred['model'] == 'ENSEMBLE':
                symbol_predictions[symbol] = pred
            elif symbol not in symbol_predictions:
                symbol_predictions[symbol] = pred
        
        if not symbol_predictions:
            return {
                'strategy': strategy,
                'weights': [],
                'cash': 1.0,
                'expected_return': 0.0,
                'expected_volatility': 0.0
            }
        
        # Convert to lists
        symbols = list(symbol_predictions.keys())
        returns = np.array([symbol_predictions[s]['expected_return'] for s in symbols])
        confidences = np.array([symbol_predictions[s]['confidence'] for s in symbols])
        
        # Generate weights based on strategy
        if strategy == "model_weighted":
            weights = self._model_weighted_allocation(symbols, returns, confidences)
        elif strategy == "mean_variance":
            weights = self._mean_variance_allocation(symbols, returns)
        elif strategy == "risk_parity":
            weights = self._risk_parity_allocation(symbols, returns)
        else:
            # Equal weight as fallback
            weights = np.ones(len(symbols)) / len(symbols)
        
        # Calculate portfolio metrics
        portfolio_return = np.sum(weights * returns)
        portfolio_volatility = self._estimate_portfolio_volatility(symbols, weights)
        
        # Format output
        weight_list = [
            {
                'symbol': symbol,
                'weight': round(float(weight), 4)
            }
            for symbol, weight in zip(symbols, weights)
            if weight > 0.001  # Filter out tiny weights
        ]
        
        # Sort by weight descending
        weight_list.sort(key=lambda x: x['weight'], reverse=True)
        
        total_invested = sum(w['weight'] for w in weight_list)
        cash = max(0.0, 1.0 - total_invested)
        
        return {
            'strategy': strategy,
            'weights': weight_list,
            'cash': round(cash, 4),
            'expected_return': round(float(portfolio_return), 4),
            'expected_volatility': round(float(portfolio_volatility), 4),
            'sharpe_ratio': round(
                float(portfolio_return / portfolio_volatility) if portfolio_volatility > 0 else 0,
                2
            )
        }
    
    def _model_weighted_allocation(
        self,
        symbols: List[str],
        returns: np.ndarray,
        confidences: np.ndarray,
        max_weight: float = 0.10
    ) -> np.ndarray:
        """
        Model-weighted allocation strategy.
        
        Weights proportional to (return * confidence), capped at max_weight.
        
        Args:
            symbols (List[str]): List of symbols
            returns (np.ndarray): Expected returns
            confidences (np.ndarray): Model confidences
            max_weight (float): Maximum weight per asset
        
        Returns:
            np.ndarray: Allocation weights
        """
        # Filter positive expected returns only
        positive_mask = returns > 0
        
        if not np.any(positive_mask):
            # No positive returns, return equal weight
            return np.ones(len(symbols)) / len(symbols)
        
        # Calculate scores
        scores = returns * confidences
        scores[~positive_mask] = 0  # Zero out negative returns
        
        if np.sum(scores) == 0:
            return np.ones(len(symbols)) / len(symbols)
        
        # Initial weights
        weights = scores / np.sum(scores)
        
        # Apply max weight constraint iteratively
        max_iterations = 10
        for _ in range(max_iterations):
            if np.max(weights) <= max_weight:
                break
            
            # Cap weights at max_weight
            excess = weights - max_weight
            excess[excess < 0] = 0
            
            weights = np.minimum(weights, max_weight)
            
            # Redistribute excess to uncapped positions
            uncapped_mask = weights < max_weight
            if np.any(uncapped_mask):
                redistribute = np.sum(excess) / np.sum(uncapped_mask)
                weights[uncapped_mask] += redistribute
        
        # Normalize to sum to 1
        weights = weights / np.sum(weights)
        
        logger.debug(f"Model-weighted allocation: {len(symbols)} assets, max_weight={np.max(weights):.4f}")
        
        return weights
    
    def _mean_variance_allocation(
        self,
        symbols: List[str],
        returns: np.ndarray,
        target_return: Optional[float] = None
    ) -> np.ndarray:
        """
        Mean-variance optimization (Markowitz).
        
        Minimizes portfolio variance subject to constraints.
        
        Args:
            symbols (List[str]): List of symbols
            returns (np.ndarray): Expected returns
            target_return (float, optional): Target portfolio return
        
        Returns:
            np.ndarray: Optimal allocation weights
        """
        n_assets = len(symbols)
        
        # Estimate covariance matrix (simplified - using historical vol estimates)
        # In production, compute from actual historical returns
        volatilities = np.full(n_assets, 0.20)  # Assume 20% annual vol
        correlation = 0.3  # Assume 30% correlation
        
        cov_matrix = np.outer(volatilities, volatilities) * correlation
        np.fill_diagonal(cov_matrix, volatilities ** 2)
        
        # Objective: minimize variance
        def portfolio_variance(weights):
            return weights.T @ cov_matrix @ weights
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Sum to 1
        ]
        
        if target_return is not None:
            constraints.append(
                {'type': 'eq', 'fun': lambda w: np.sum(w * returns) - target_return}
            )
        
        # Bounds: 0 <= w_i <= 0.15
        bounds = tuple((0, 0.15) for _ in range(n_assets))
        
        # Initial guess: equal weight
        w0 = np.ones(n_assets) / n_assets
        
        # Optimize
        result = minimize(
            portfolio_variance,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            weights = result.x
            logger.debug(f"Mean-variance optimization converged")
        else:
            logger.warning(f"Mean-variance optimization failed, using equal weight")
            weights = np.ones(n_assets) / n_assets
        
        return weights
    
    def _risk_parity_allocation(
        self,
        symbols: List[str],
        returns: np.ndarray
    ) -> np.ndarray:
        """
        Risk parity allocation strategy.
        
        Each asset contributes equally to portfolio risk.
        
        Args:
            symbols (List[str]): List of symbols
            returns (np.ndarray): Expected returns
        
        Returns:
            np.ndarray: Risk parity weights
        """
        n_assets = len(symbols)
        
        # Estimate volatilities (simplified)
        volatilities = np.full(n_assets, 0.20)  # Assume 20% vol
        correlation = 0.3
        
        cov_matrix = np.outer(volatilities, volatilities) * correlation
        np.fill_diagonal(cov_matrix, volatilities ** 2)
        
        # Objective: minimize sum of squared differences in risk contribution
        def risk_parity_objective(weights):
            portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
            
            # Marginal contribution to risk
            marginal_contrib = cov_matrix @ weights / portfolio_vol
            
            # Risk contribution
            risk_contrib = weights * marginal_contrib
            
            # Target: equal risk contribution
            target_risk = portfolio_vol / n_assets
            
            return np.sum((risk_contrib - target_risk) ** 2)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]
        
        # Bounds
        bounds = tuple((0, 0.20) for _ in range(n_assets))
        
        # Initial guess: inverse volatility
        w0 = (1 / volatilities) / np.sum(1 / volatilities)
        
        # Optimize
        result = minimize(
            risk_parity_objective,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            weights = result.x
            logger.debug(f"Risk parity allocation converged")
        else:
            logger.warning(f"Risk parity optimization failed, using inverse vol weights")
            weights = (1 / volatilities) / np.sum(1 / volatilities)
        
        return weights
    
    def _estimate_portfolio_volatility(
        self,
        symbols: List[str],
        weights: np.ndarray,
        annual_vol: float = 0.20,
        correlation: float = 0.30
    ) -> float:
        """
        Estimate portfolio volatility.
        
        Args:
            symbols (List[str]): List of symbols
            weights (np.ndarray): Portfolio weights
            annual_vol (float): Assumed annual volatility per asset
            correlation (float): Assumed correlation between assets
        
        Returns:
            float: Estimated portfolio volatility
        """
        n_assets = len(symbols)
        
        # Simplified covariance matrix
        volatilities = np.full(n_assets, annual_vol)
        cov_matrix = np.outer(volatilities, volatilities) * correlation
        np.fill_diagonal(cov_matrix, volatilities ** 2)
        
        portfolio_variance = weights.T @ cov_matrix @ weights
        portfolio_vol = np.sqrt(portfolio_variance)
        
        return portfolio_vol
