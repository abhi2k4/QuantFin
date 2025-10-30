"""
Backtest Metrics - Professional Financial Metrics

This module provides helper functions for calculating:
- CAGR (Compound Annual Growth Rate)
- Sharpe Ratio (Risk-adjusted return)
- Maximum Drawdown (Worst peak-to-trough decline)
- Sortino Ratio (Downside risk-adjusted return)

Author: QuantFin Team
Date: 2025-10-31
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_cagr(portfolio_values: List[float], years: float) -> float:
    """
    Calculate Compound Annual Growth Rate.
    
    CAGR = (Ending Value / Beginning Value)^(1/years) - 1
    
    Args:
        portfolio_values: List of portfolio values over time
        years: Number of years in the period
        
    Returns:
        CAGR as percentage (e.g., 15.5 for 15.5%)
    """
    if len(portfolio_values) < 2 or years <= 0:
        return 0.0
    
    beginning_value = portfolio_values[0]
    ending_value = portfolio_values[-1]
    
    if beginning_value <= 0:
        return 0.0
    
    total_return = ending_value / beginning_value
    cagr = (total_return ** (1 / years)) - 1
    
    return cagr * 100  # Return as percentage


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.05,
    periods_per_year: int = 12
) -> float:
    """
    Calculate Sharpe Ratio (risk-adjusted return).
    
    Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns
    
    Args:
        returns: List of period returns (e.g., monthly returns)
        risk_free_rate: Annual risk-free rate (default 5%)
        periods_per_year: Number of periods per year (12 for monthly)
        
    Returns:
        Annualized Sharpe Ratio
    """
    if len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    
    # Calculate excess returns (subtract risk-free rate per period)
    risk_free_per_period = risk_free_rate / periods_per_year
    excess_returns = returns_array - risk_free_per_period
    
    # Calculate mean and std of excess returns
    mean_excess = np.mean(excess_returns)
    std_excess = np.std(excess_returns, ddof=1)  # Sample std dev
    
    if std_excess == 0:
        return 0.0
    
    # Annualize Sharpe ratio
    sharpe = (mean_excess / std_excess) * np.sqrt(periods_per_year)
    
    return sharpe


def calculate_sortino_ratio(
    returns: List[float],
    risk_free_rate: float = 0.05,
    periods_per_year: int = 12
) -> float:
    """
    Calculate Sortino Ratio (downside risk-adjusted return).
    
    Similar to Sharpe but only considers downside volatility.
    
    Args:
        returns: List of period returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year
        
    Returns:
        Annualized Sortino Ratio
    """
    if len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    risk_free_per_period = risk_free_rate / periods_per_year
    excess_returns = returns_array - risk_free_per_period
    
    mean_excess = np.mean(excess_returns)
    
    # Downside deviation (only negative returns)
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return 0.0
    
    downside_std = np.std(downside_returns, ddof=1)
    
    if downside_std == 0:
        return 0.0
    
    sortino = (mean_excess / downside_std) * np.sqrt(periods_per_year)
    
    return sortino


def calculate_max_drawdown(portfolio_values: List[float]) -> float:
    """
    Calculate Maximum Drawdown (worst peak-to-trough decline).
    
    Max Drawdown = (Trough Value - Peak Value) / Peak Value
    
    Args:
        portfolio_values: List of portfolio values over time
        
    Returns:
        Max drawdown as percentage (negative value, e.g., -15.5 for 15.5% loss)
    """
    if len(portfolio_values) < 2:
        return 0.0
    
    values = np.array(portfolio_values)
    
    # Calculate running maximum (peak)
    running_max = np.maximum.accumulate(values)
    
    # Calculate drawdown at each point
    drawdown = (values - running_max) / running_max
    
    # Maximum drawdown (most negative value)
    max_dd = np.min(drawdown)
    
    return max_dd * 100  # Return as percentage


def calculate_calmar_ratio(
    portfolio_values: List[float],
    years: float
) -> float:
    """
    Calculate Calmar Ratio (return / max drawdown).
    
    Calmar Ratio = CAGR / |Max Drawdown|
    
    Args:
        portfolio_values: List of portfolio values over time
        years: Number of years in the period
        
    Returns:
        Calmar Ratio
    """
    cagr = calculate_cagr(portfolio_values, years)
    max_dd = calculate_max_drawdown(portfolio_values)
    
    if max_dd >= 0:  # No drawdown
        return 0.0
    
    calmar = cagr / abs(max_dd)
    
    return calmar


def calculate_win_rate(returns: List[float]) -> float:
    """
    Calculate win rate (percentage of positive returns).
    
    Args:
        returns: List of period returns
        
    Returns:
        Win rate as percentage (e.g., 55.5 for 55.5%)
    """
    if len(returns) == 0:
        return 0.0
    
    returns_array = np.array(returns)
    winning_periods = np.sum(returns_array > 0)
    win_rate = (winning_periods / len(returns_array)) * 100
    
    return win_rate


def calculate_volatility(
    returns: List[float],
    periods_per_year: int = 12
) -> float:
    """
    Calculate annualized volatility.
    
    Args:
        returns: List of period returns
        periods_per_year: Number of periods per year
        
    Returns:
        Annualized volatility as percentage
    """
    if len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    std = np.std(returns_array, ddof=1)
    annualized_vol = std * np.sqrt(periods_per_year) * 100
    
    return annualized_vol


def calculate_returns_from_values(portfolio_values: List[float]) -> List[float]:
    """
    Calculate period returns from portfolio values.
    
    Args:
        portfolio_values: List of portfolio values over time
        
    Returns:
        List of returns (e.g., [0.05, -0.02, 0.03] for 5%, -2%, 3%)
    """
    if len(portfolio_values) < 2:
        return []
    
    values = np.array(portfolio_values)
    returns = np.diff(values) / values[:-1]
    
    return returns.tolist()


def calculate_all_metrics(
    portfolio_values: List[float],
    years: float,
    risk_free_rate: float = 0.05
) -> Dict[str, float]:
    """
    Calculate all backtest metrics at once.
    
    Args:
        portfolio_values: List of portfolio values over time
        years: Number of years in the period
        risk_free_rate: Annual risk-free rate
        
    Returns:
        Dictionary with all metrics
    """
    returns = calculate_returns_from_values(portfolio_values)
    
    metrics = {
        'cagr': calculate_cagr(portfolio_values, years),
        'sharpe_ratio': calculate_sharpe_ratio(returns, risk_free_rate),
        'sortino_ratio': calculate_sortino_ratio(returns, risk_free_rate),
        'max_drawdown': calculate_max_drawdown(portfolio_values),
        'calmar_ratio': calculate_calmar_ratio(portfolio_values, years),
        'volatility': calculate_volatility(returns),
        'win_rate': calculate_win_rate(returns),
        'total_return': ((portfolio_values[-1] / portfolio_values[0]) - 1) * 100 if len(portfolio_values) > 1 else 0.0
    }
    
    return metrics


def format_metrics(metrics: Dict[str, float]) -> Dict[str, str]:
    """
    Format metrics for display.
    
    Args:
        metrics: Dictionary of metric values
        
    Returns:
        Dictionary of formatted metric strings
    """
    formatted = {}
    
    for key, value in metrics.items():
        if key in ['cagr', 'max_drawdown', 'total_return', 'volatility', 'win_rate']:
            formatted[key] = f"{value:.2f}%"
        else:
            formatted[key] = f"{value:.2f}"
    
    return formatted
