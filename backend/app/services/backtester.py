"""
Backtester Module for QuantFin Portfolio Strategies

This module simulates historical portfolio performance using trained ML models
and evaluates different portfolio allocation strategies.

Author: QuantFin Team
Date: 2025-10-09
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
import json

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


class Backtester:
    """
    Backtester for historical portfolio performance simulation.
    
    Simulates trading strategies using trained ML models on historical data
    and evaluates portfolio performance with multiple allocation strategies.
    """
    
    def __init__(
        self,
        models_dir: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategy: str = "model_weighted",
        rebalance_freq: int = 21,
        initial_capital: float = 100000.0,
        transaction_cost: float = 0.001,
        results_dir: str = "backend/results"
    ):
        """
        Initialize the Backtester.
        
        Args:
            models_dir (str): Directory containing trained models
            symbols (List[str]): List of stock symbols to trade
            start_date (str): Start date for backtest (YYYY-MM-DD)
            end_date (str): End date for backtest (YYYY-MM-DD)
            strategy (str): Portfolio strategy ('model_weighted', 'mean_variance', 'risk_parity')
            rebalance_freq (int): Rebalancing frequency in trading days
            initial_capital (float): Initial portfolio capital
            transaction_cost (float): Transaction cost as fraction (e.g., 0.001 = 0.1%)
            results_dir (str): Directory to save results
        """
        self.models_dir = Path(models_dir)
        self.symbols = symbols
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.strategy = strategy
        self.rebalance_freq = rebalance_freq
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Results storage
        self.daily_returns: List[float] = []
        self.daily_values: List[float] = []
        self.daily_dates: List[pd.Timestamp] = []
        self.daily_weights: List[Dict] = []
        self.trade_log: List[Dict] = []
        
        # Historical price data
        self.price_data: Dict[str, pd.DataFrame] = {}
        
        # Loaded models
        self.loaded_models: Dict[str, Dict] = {}
        
        logger.info(f"Backtester initialized: {start_date} to {end_date}, Strategy: {strategy}")
    
    def _load_historical_data(self) -> None:
        """Load historical price data for all symbols."""
        logger.info(f"Loading historical data for {len(self.symbols)} symbols...")
        
        # Use absolute path from this file's location
        data_dir = Path(__file__).parent.parent.parent / "data"
        
        for symbol in self.symbols:
            try:
                csv_path = data_dir / f"{symbol}.csv"
                if not csv_path.exists():
                    logger.warning(f"Data file not found for {symbol}")
                    continue
                
                # Skip rows 1 (Ticker) and 2 (Date label)
                df = pd.read_csv(csv_path, skiprows=[1, 2])
                df = df.rename(columns={'Price': 'Date'})  # First column is Date
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
                df = df.sort_index()
                
                # Filter to backtest period
                df = df[(df.index >= self.start_date) & (df.index <= self.end_date)]
                
                if len(df) < 20:  # Reduced from 100 - need at least 20 trading days
                    logger.warning(f"Insufficient data for {symbol} in backtest period (only {len(df)} days)")
                    continue
                
                self.price_data[symbol] = df
                logger.debug(f"Loaded {len(df)} rows for {symbol}")
            
            except Exception as e:
                logger.error(f"Error loading data for {symbol}: {e}")
                continue
        
        logger.info(f"Successfully loaded data for {len(self.price_data)} symbols")
    
    def _load_models(self) -> None:
        """Load trained ML models for prediction."""
        logger.info(f"Loading models for {len(self.symbols)} symbols...")
        
        from app.ml_models.linear_reg import LinearRegModel
        
        for symbol in self.symbols:
            try:
                model_path = self.models_dir / "linear_reg" / symbol
                if model_path.exists():
                    model = LinearRegModel(symbol, models_dir=str(self.models_dir / "linear_reg"))
                    model.load_model()
                    if symbol not in self.loaded_models:
                        self.loaded_models[symbol] = {}
                    self.loaded_models[symbol]['linear_reg'] = model
                    logger.debug(f"Loaded linear_reg model for {symbol}")
            except Exception as e:
                logger.warning(f"Could not load model for {symbol}: {e}")
        
        logger.info(f"Loaded models for {len(self.loaded_models)} symbols")
    
    def _get_prediction_on_date(
        self,
        symbol: str,
        date: pd.Timestamp,
        lookback: int = 252
    ) -> Optional[Dict]:
        """
        Get model prediction using only data available up to given date.
        
        Args:
            symbol (str): Stock symbol
            date (pd.Timestamp): Prediction date
            lookback (int): Number of days to use for prediction
        
        Returns:
            Optional[Dict]: Prediction result or None
        """
        try:
            if symbol not in self.price_data:
                return None
            
            df = self.price_data[symbol]
            
            # Get data up to prediction date
            historical_df = df[df.index <= date].copy()
            
            if len(historical_df) < lookback:
                logger.debug(f"Insufficient history for {symbol} on {date}")
                return None
            
            # Use last 'lookback' days
            historical_df = historical_df.tail(lookback)
            
            # Simple prediction using linear model if available
            if symbol in self.loaded_models and 'linear_reg' in self.loaded_models[symbol]:
                model = self.loaded_models[symbol]['linear_reg']
                try:
                    result = model.predict(historical_df)
                    return {
                        'symbol': symbol,
                        'expected_return': result['expected_return'],
                        'confidence': result['confidence_score']
                    }
                except:
                    pass
            
            # Fallback: simple momentum-based prediction
            if len(historical_df) >= 21:
                recent_return = (historical_df['Close'].iloc[-1] / historical_df['Close'].iloc[-21]) - 1
                return {
                    'symbol': symbol,
                    'expected_return': recent_return * 0.5,  # Dampened momentum
                    'confidence': 0.5
                }
            
            return None
        
        except Exception as e:
            logger.debug(f"Error getting prediction for {symbol} on {date}: {e}")
            return None
    
    def _calculate_portfolio_weights(
        self,
        date: pd.Timestamp
    ) -> Dict[str, float]:
        """
        Calculate portfolio weights for given date based on strategy.
        
        Args:
            date (pd.Timestamp): Rebalancing date
        
        Returns:
            Dict[str, float]: Dictionary of symbol -> weight
        """
        logger.debug(f"Calculating portfolio weights for {date.date()} using {self.strategy} strategy")
        
        symbols = list(self.price_data.keys())
        
        # Strategy-specific weight calculation
        try:
            if self.strategy == "model_weighted":
                # Model-weighted strategy requires predictions
                weights = self._model_weighted_strategy(symbols, date)
            elif self.strategy == "mean_variance":
                # Mean-variance uses historical data only
                weights = self._mean_variance_strategy(symbols, date)
            elif self.strategy == "risk_parity":
                # Risk parity uses historical data only
                weights = self._risk_parity_strategy(symbols, date)
            else:
                # Equal weight fallback
                logger.warning(f"Unknown strategy '{self.strategy}', using equal weights")
                weights = np.ones(len(symbols)) / len(symbols)
            
            # Create weight dictionary
            weight_dict = {symbol: float(weight) for symbol, weight in zip(symbols, weights)}
            
            logger.debug(f"Portfolio weights calculated: {len(weight_dict)} positions")
            return weight_dict
        
        except Exception as e:
            logger.error(f"Error calculating weights: {e}", exc_info=True)
            return {}
    
    def _model_weighted_strategy(
        self,
        symbols: List[str],
        date: pd.Timestamp
    ) -> np.ndarray:
        """
        Model-weighted strategy using ML predictions.
        Falls back to momentum strategy if no predictions available.
        
        Args:
            symbols (List[str]): List of symbols
            date (pd.Timestamp): Current date
        
        Returns:
            np.ndarray: Portfolio weights
        """
        # Get predictions for all symbols
        predictions = {}
        for symbol in symbols:
            pred = self._get_prediction_on_date(symbol, date)
            if pred is not None:
                predictions[symbol] = pred
        
        if not predictions:
            logger.warning(f"No predictions available for {date.date()}, using momentum fallback")
            return self._momentum_fallback_strategy(symbols, date)
        
        # Filter symbols to only those with predictions
        pred_symbols = list(predictions.keys())
        returns = np.array([predictions[s]['expected_return'] for s in pred_symbols])
        confidences = np.array([predictions[s]['confidence'] for s in pred_symbols])
        
        # Calculate model-weighted allocation
        weights = self._model_weighted_allocation(returns, confidences)
        
        # Create full weight array (zero for symbols without predictions)
        full_weights = np.zeros(len(symbols))
        for i, symbol in enumerate(symbols):
            if symbol in pred_symbols:
                pred_idx = pred_symbols.index(symbol)
                full_weights[i] = weights[pred_idx]
        
        # Normalize to sum to 1
        if full_weights.sum() > 0:
            full_weights = full_weights / full_weights.sum()
        else:
            # Fallback if all weights are zero
            full_weights = self._momentum_fallback_strategy(symbols, date)
        
        return full_weights
    
    def _mean_variance_strategy(
        self,
        symbols: List[str],
        date: pd.Timestamp
    ) -> np.ndarray:
        """
        Mean-variance optimization strategy using historical data.
        
        Args:
            symbols (List[str]): List of symbols
            date (pd.Timestamp): Current date
        
        Returns:
            np.ndarray: Portfolio weights
        """
        # Calculate historical returns as expected returns
        returns = self._calculate_historical_returns(symbols, date, lookback=60)
        
        if returns is None:
            logger.warning("Insufficient historical data for mean-variance, using equal weights")
            return np.ones(len(symbols)) / len(symbols)
        
        return self._mean_variance_allocation(symbols, returns, date)
    
    def _risk_parity_strategy(
        self,
        symbols: List[str],
        date: pd.Timestamp
    ) -> np.ndarray:
        """
        Risk parity strategy using historical data.
        
        Args:
            symbols (List[str]): List of symbols
            date (pd.Timestamp): Current date
        
        Returns:
            np.ndarray: Portfolio weights
        """
        # Risk parity doesn't strictly need expected returns, but we pass dummy values
        # The actual optimization uses only the covariance matrix
        returns = np.zeros(len(symbols))  # Not used in risk parity
        
        return self._risk_parity_allocation(symbols, returns, date)
    
    def _momentum_fallback_strategy(
        self,
        symbols: List[str],
        date: pd.Timestamp,
        lookback: int = 60
    ) -> np.ndarray:
        """
        Momentum-based fallback strategy when predictions not available.
        Weights based on recent returns.
        
        Args:
            symbols (List[str]): List of symbols
            date (pd.Timestamp): Current date
            lookback (int): Lookback period in days
        
        Returns:
            np.ndarray: Portfolio weights
        """
        returns = self._calculate_historical_returns(symbols, date, lookback)
        
        if returns is None:
            # Ultimate fallback: equal weights
            return np.ones(len(symbols)) / len(symbols)
        
        # Positive momentum only
        positive_returns = np.maximum(returns, 0)
        
        if positive_returns.sum() == 0:
            # No positive momentum, equal weights
            return np.ones(len(symbols)) / len(symbols)
        
        # Weight by momentum with cap
        weights = positive_returns / positive_returns.sum()
        weights = np.minimum(weights, 0.25)  # 25% max per asset
        weights = weights / weights.sum()  # Renormalize
        
        return weights
    
    def _calculate_historical_returns(
        self,
        symbols: List[str],
        date: pd.Timestamp,
        lookback: int = 60
    ) -> Optional[np.ndarray]:
        """
        Calculate historical returns for symbols.
        
        Args:
            symbols (List[str]): List of symbols
            date (pd.Timestamp): Current date
            lookback (int): Lookback period
        
        Returns:
            Optional[np.ndarray]: Array of returns or None if insufficient data
        """
        returns = []
        
        for symbol in symbols:
            if symbol not in self.price_data:
                return None
            
            df = self.price_data[symbol]
            hist_data = df[df.index < date].tail(lookback)
            
            if len(hist_data) < lookback // 2:  # Need at least half the lookback period
                return None
            
            # Calculate return
            if len(hist_data) > 0:
                ret = (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0]
                returns.append(ret)
            else:
                return None
        
        return np.array(returns)
    
    def _model_weighted_allocation(
        self,
        returns: np.ndarray,
        confidences: np.ndarray,
        max_weight: float = 0.10
    ) -> np.ndarray:
        """
        Model-weighted portfolio allocation (momentum-based).
        
        Args:
            returns (np.ndarray): Expected returns
            confidences (np.ndarray): Model confidences
            max_weight (float): Maximum weight per asset
        
        Returns:
            np.ndarray: Portfolio weights
        """
        # Weight by return * confidence
        scores = returns * confidences
        
        # Filter negative scores (don't short)
        scores = np.maximum(scores, 0)
        
        if scores.sum() == 0:
            return np.ones(len(scores)) / len(scores)
        
        # Normalize
        weights = scores / scores.sum()
        
        # Apply max weight constraint
        weights = np.minimum(weights, max_weight)
        
        # Renormalize
        if weights.sum() > 0:
            weights = weights / weights.sum()
        else:
            weights = np.ones(len(weights)) / len(weights)
        
        return weights
    
    def _mean_variance_allocation(
        self,
        symbols: List[str],
        returns: np.ndarray,
        date: pd.Timestamp,
        target_return: Optional[float] = None
    ) -> np.ndarray:
        """
        Mean-variance optimization (Markowitz).
        
        Args:
            symbols (List[str]): List of symbols
            returns (np.ndarray): Expected returns
            date (pd.Timestamp): Current date
            target_return (float, optional): Target portfolio return
        
        Returns:
            np.ndarray: Optimal portfolio weights
        """
        n_assets = len(symbols)
        
        # Estimate covariance matrix from historical data
        cov_matrix = self._estimate_covariance(symbols, date, lookback=252)
        
        if cov_matrix is None:
            # Fallback to equal weights
            return np.ones(n_assets) / n_assets
        
        # Set target return if not provided
        if target_return is None:
            target_return = np.mean(returns)
        
        # Optimization constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1
            {'type': 'ineq', 'fun': lambda w: np.dot(w, returns) - target_return}  # Meet target return
        ]
        
        # Bounds (no shorting)
        bounds = tuple((0, 0.15) for _ in range(n_assets))
        
        # Initial guess
        w0 = np.ones(n_assets) / n_assets
        
        # Objective: minimize portfolio variance
        def portfolio_variance(w):
            return np.dot(w.T, np.dot(cov_matrix, w))
        
        # Optimize
        result = minimize(
            portfolio_variance,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 500}
        )
        
        if result.success:
            weights = result.x
            # Ensure normalization
            weights = weights / weights.sum()
            return weights
        else:
            logger.warning("Mean-variance optimization failed, using equal weights")
            return np.ones(n_assets) / n_assets
    
    def _risk_parity_allocation(
        self,
        symbols: List[str],
        returns: np.ndarray,
        date: pd.Timestamp
    ) -> np.ndarray:
        """
        Risk parity portfolio allocation.
        
        Equal risk contribution from each asset.
        
        Args:
            symbols (List[str]): List of symbols
            returns (np.ndarray): Expected returns
            date (pd.Timestamp): Current date
        
        Returns:
            np.ndarray: Risk parity weights
        """
        n_assets = len(symbols)
        
        # Estimate covariance matrix
        cov_matrix = self._estimate_covariance(symbols, date, lookback=252)
        
        if cov_matrix is None:
            return np.ones(n_assets) / n_assets
        
        # Risk parity objective: minimize squared difference in risk contributions
        def risk_parity_objective(w):
            portfolio_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            marginal_contrib = np.dot(cov_matrix, w)
            risk_contrib = w * marginal_contrib / portfolio_vol
            target_risk = portfolio_vol / n_assets
            return np.sum((risk_contrib - target_risk) ** 2)
        
        # Constraints and bounds
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = tuple((0.01, 0.15) for _ in range(n_assets))
        w0 = np.ones(n_assets) / n_assets
        
        # Optimize
        result = minimize(
            risk_parity_objective,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 500}
        )
        
        if result.success:
            weights = result.x
            weights = weights / weights.sum()
            return weights
        else:
            logger.warning("Risk parity optimization failed, using equal weights")
            return np.ones(n_assets) / n_assets
    
    def _estimate_covariance(
        self,
        symbols: List[str],
        date: pd.Timestamp,
        lookback: int = 252
    ) -> Optional[np.ndarray]:
        """
        Estimate covariance matrix from historical returns.
        
        Args:
            symbols (List[str]): List of symbols
            date (pd.Timestamp): Current date
            lookback (int): Days to look back
        
        Returns:
            Optional[np.ndarray]: Covariance matrix or None
        """
        try:
            returns_df = pd.DataFrame()
            
            for symbol in symbols:
                if symbol not in self.price_data:
                    continue
                
                df = self.price_data[symbol]
                historical = df[df.index <= date].tail(lookback)
                
                if len(historical) < 50:
                    continue
                
                daily_returns = historical['Close'].pct_change().dropna()
                returns_df[symbol] = daily_returns
            
            if returns_df.empty or len(returns_df.columns) < 2:
                return None
            
            # Calculate covariance matrix
            cov_matrix = returns_df.cov().values
            
            # Ensure valid symbols match
            if cov_matrix.shape[0] != len(symbols):
                # Reindex to match input symbols
                available_symbols = [s for s in symbols if s in returns_df.columns]
                if len(available_symbols) != len(symbols):
                    return None
            
            return cov_matrix
        
        except Exception as e:
            logger.error(f"Error estimating covariance: {e}")
            return None
    
    def _get_prices_on_date(
        self,
        date: pd.Timestamp
    ) -> Dict[str, float]:
        """
        Get closing prices for all symbols on given date.
        
        Args:
            date (pd.Timestamp): Date to get prices
        
        Returns:
            Dict[str, float]: Symbol -> price mapping
        """
        prices = {}
        
        for symbol in self.price_data.keys():
            df = self.price_data[symbol]
            
            # Get price on or before date
            historical = df[df.index <= date]
            
            if len(historical) > 0:
                prices[symbol] = float(historical['Close'].iloc[-1])
        
        return prices
    
    def _calculate_portfolio_value(
        self,
        holdings: Dict[str, float],
        prices: Dict[str, float]
    ) -> float:
        """
        Calculate total portfolio value.
        
        Args:
            holdings (Dict[str, float]): Symbol -> shares mapping
            prices (Dict[str, float]): Symbol -> price mapping
        
        Returns:
            float: Total portfolio value
        """
        total = 0.0
        
        for symbol, shares in holdings.items():
            if symbol in prices:
                total += shares * prices[symbol]
        
        return total
    
    def _rebalance_portfolio(
        self,
        current_holdings: Dict[str, float],
        target_weights: Dict[str, float],
        prices: Dict[str, float],
        cash: float,
        date: pd.Timestamp
    ) -> Tuple[Dict[str, float], float, float]:
        """
        Rebalance portfolio to target weights.
        
        Args:
            current_holdings (Dict[str, float]): Current shares held
            target_weights (Dict[str, float]): Target portfolio weights
            prices (Dict[str, float]): Current prices
            cash (float): Available cash
            date (pd.Timestamp): Rebalancing date
        
        Returns:
            Tuple[Dict[str, float], float, float]: New holdings, new cash, transaction costs
        """
        # Calculate current portfolio value
        current_value = self._calculate_portfolio_value(current_holdings, prices)
        total_value = current_value + cash
        
        # Calculate target positions
        target_holdings = {}
        for symbol, weight in target_weights.items():
            if symbol in prices and weight > 0:
                target_value = total_value * weight
                target_shares = target_value / prices[symbol]
                target_holdings[symbol] = target_shares
        
        # Calculate trades and costs
        total_cost = 0.0
        new_holdings = {}
        
        # Sell positions
        for symbol, current_shares in current_holdings.items():
            target_shares = target_holdings.get(symbol, 0.0)
            
            if target_shares < current_shares:
                shares_to_sell = current_shares - target_shares
                if symbol in prices:
                    sale_value = shares_to_sell * prices[symbol]
                    cost = sale_value * self.transaction_cost
                    cash += sale_value - cost
                    total_cost += cost
                    
                    # Log trade
                    self.trade_log.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'SELL',
                        'shares': shares_to_sell,
                        'price': prices[symbol],
                        'value': sale_value,
                        'cost': cost
                    })
            
            if target_shares > 0:
                new_holdings[symbol] = target_shares
        
        # Buy new positions
        for symbol, target_shares in target_holdings.items():
            current_shares = current_holdings.get(symbol, 0.0)
            
            if target_shares > current_shares:
                shares_to_buy = target_shares - current_shares
                if symbol in prices:
                    purchase_value = shares_to_buy * prices[symbol]
                    cost = purchase_value * self.transaction_cost
                    
                    if cash >= (purchase_value + cost):
                        cash -= (purchase_value + cost)
                        total_cost += cost
                        new_holdings[symbol] = target_shares
                        
                        # Log trade
                        self.trade_log.append({
                            'date': date,
                            'symbol': symbol,
                            'action': 'BUY',
                            'shares': shares_to_buy,
                            'price': prices[symbol],
                            'value': purchase_value,
                            'cost': cost
                        })
                    else:
                        logger.warning(f"Insufficient cash to buy {symbol}")
        
        return new_holdings, cash, total_cost
    
    def run_backtest(self) -> Dict:
        """
        Run the backtest simulation.
        
        Returns:
            Dict: Backtest results
        """
        logger.info("Starting backtest...")
        start_time = datetime.now()
        
        # Load historical data
        self._load_historical_data()
        
        if not self.price_data:
            logger.error("No data loaded, cannot run backtest")
            return {}
        
        # Load models
        self._load_models()
        
        # Get all trading dates
        all_dates = sorted(set().union(*[set(df.index) for df in self.price_data.values()]))
        all_dates = [d for d in all_dates if self.start_date <= d <= self.end_date]
        
        if len(all_dates) < self.rebalance_freq:
            logger.error("Insufficient trading days for backtest")
            return {}
        
        logger.info(f"Backtesting over {len(all_dates)} trading days")
        
        # Initialize portfolio
        cash = self.initial_capital
        holdings = {}
        portfolio_value = self.initial_capital
        last_rebalance = 0
        
        # Track results
        self.daily_returns = []
        self.daily_values = [self.initial_capital]
        self.daily_dates = [all_dates[0]]
        self.daily_weights = [{}]
        self.trade_log = []
        
        # Run simulation
        for i, date in enumerate(all_dates):
            try:
                # Get current prices
                prices = self._get_prices_on_date(date)
                
                if not prices:
                    logger.debug(f"No prices available for {date.date()}")
                    continue
                
                # Rebalance if needed
                if i - last_rebalance >= self.rebalance_freq or i == 0:
                    logger.info(f"Rebalancing on {date.date()} (day {i+1}/{len(all_dates)})")
                    
                    target_weights = self._calculate_portfolio_weights(date)
                    
                    if target_weights:
                        holdings, cash, costs = self._rebalance_portfolio(
                            holdings, target_weights, prices, cash, date
                        )
                        last_rebalance = i
                        
                        self.daily_weights.append(target_weights)
                        logger.info(f"  Portfolio rebalanced: {len(target_weights)} positions, costs: ${costs:.2f}")
                    else:
                        self.daily_weights.append(self.daily_weights[-1] if self.daily_weights else {})
                else:
                    self.daily_weights.append(self.daily_weights[-1] if self.daily_weights else {})
                
                # Calculate portfolio value
                holdings_value = self._calculate_portfolio_value(holdings, prices)
                portfolio_value = holdings_value + cash
                
                # Calculate daily return
                if len(self.daily_values) > 0:
                    daily_return = (portfolio_value / self.daily_values[-1]) - 1.0
                    self.daily_returns.append(daily_return)
                
                # Store results
                self.daily_values.append(portfolio_value)
                self.daily_dates.append(date)
                
                if (i + 1) % 50 == 0:
                    logger.info(f"  Day {i+1}/{len(all_dates)}: Portfolio value: ${portfolio_value:,.2f}")
            
            except Exception as e:
                logger.error(f"Error on {date.date()}: {e}")
                continue
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Backtest completed in {elapsed_time:.2f}s")
        
        # Calculate metrics
        metrics = self.get_metrics()
        
        return {
            'metrics': metrics,
            'daily_values': self.daily_values,
            'daily_returns': self.daily_returns,
            'daily_dates': [d.strftime('%Y-%m-%d') for d in self.daily_dates],
            'trades': len(self.trade_log),
            'elapsed_time': elapsed_time
        }
    
    def get_metrics(self) -> Dict:
        """
        Calculate portfolio performance metrics.
        
        Returns:
            Dict: Performance metrics
        """
        if not self.daily_returns or not self.daily_values:
            return {}
        
        returns = np.array(self.daily_returns)
        
        # Basic metrics
        total_return = (self.daily_values[-1] / self.daily_values[0]) - 1.0
        
        # Annualized metrics (assuming 252 trading days)
        n_days = len(returns)
        years = n_days / 252.0
        annualized_return = (1 + total_return) ** (1 / years) - 1.0 if years > 0 else 0
        
        daily_volatility = np.std(returns)
        annualized_volatility = daily_volatility * np.sqrt(252)
        
        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = (annualized_return / annualized_volatility) if annualized_volatility > 0 else 0
        
        # Drawdown analysis
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Win rate
        winning_days = np.sum(returns > 0)
        win_rate = winning_days / len(returns) if len(returns) > 0 else 0
        
        metrics = {
            'total_return': round(total_return, 4),
            'annualized_return': round(annualized_return, 4),
            'annualized_volatility': round(annualized_volatility, 4),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 4),
            'win_rate': round(win_rate, 4),
            'total_trades': len(self.trade_log),
            'final_value': round(self.daily_values[-1], 2),
            'initial_value': round(self.daily_values[0], 2),
            'trading_days': len(returns),
            'years': round(years, 2)
        }
        
        logger.info(f"Performance Metrics: Return={metrics['annualized_return']:.2%}, "
                   f"Sharpe={metrics['sharpe_ratio']:.2f}, MaxDD={metrics['max_drawdown']:.2%}")
        
        return metrics
    
    def plot_performance(self, save_path: Optional[str] = None) -> None:
        """
        Plot cumulative returns and drawdowns.
        
        Args:
            save_path (str, optional): Path to save plot
        """
        if not self.daily_returns or not self.daily_dates:
            logger.warning("No data to plot")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Cumulative returns
        cumulative_returns = np.cumprod(1 + np.array(self.daily_returns)) - 1
        dates = self.daily_dates[1:]  # Exclude first date (no return)
        
        ax1.plot(dates, cumulative_returns * 100, linewidth=2, label=f'{self.strategy.upper()} Strategy')
        ax1.set_title('Cumulative Returns', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Return (%)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Drawdowns
        cumulative = np.cumprod(1 + np.array(self.daily_returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        ax2.fill_between(dates, drawdown * 100, 0, alpha=0.3, color='red')
        ax2.plot(dates, drawdown * 100, linewidth=2, color='red', label='Drawdown')
        ax2.set_title('Portfolio Drawdown', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Drawdown (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance plot saved to {save_path}")
        else:
            default_path = self.results_dir / f"backtest_{self.strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance plot saved to {default_path}")
        
        plt.close()
    
    def save_results(self, filename: Optional[str] = None) -> None:
        """
        Save backtest results to CSV and JSON.
        
        Args:
            filename (str, optional): Base filename (without extension)
        """
        if filename is None:
            filename = f"backtest_{self.strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save daily results to CSV
        results_df = pd.DataFrame({
            'date': [d.strftime('%Y-%m-%d') for d in self.daily_dates[1:]],
            'portfolio_value': self.daily_values[1:],
            'daily_return': self.daily_returns
        })
        
        csv_path = self.results_dir / f"{filename}.csv"
        results_df.to_csv(csv_path, index=False)
        logger.info(f"Daily results saved to {csv_path}")
        
        # Save trade log to CSV
        if self.trade_log:
            trades_df = pd.DataFrame(self.trade_log)
            trades_df['date'] = trades_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            trades_csv = self.results_dir / f"{filename}_trades.csv"
            trades_df.to_csv(trades_csv, index=False)
            logger.info(f"Trade log saved to {trades_csv}")
        
        # Save metrics to JSON
        metrics = self.get_metrics()
        summary = {
            'strategy': self.strategy,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'symbols': self.symbols,
            'rebalance_freq': self.rebalance_freq,
            'initial_capital': self.initial_capital,
            'transaction_cost': self.transaction_cost,
            'metrics': metrics
        }
        
        json_path = self.results_dir / f"{filename}_summary.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {json_path}")
        
        logger.info(f"All results saved with base filename: {filename}")
