"""
ML Models Package for ETF Portfolio System

This package contains machine learning models for stock price prediction,
classification, and time series forecasting.

Author: QuantFin Team
Date: 2025-10-09
"""

from .linear_reg import LinearRegModel
from .logreg import LogisticRegModel
from .svm_model import SVMModel
from .arima_model import ARIMAModel
from .lstm_model import LSTMModel

__all__ = [
    'LinearRegModel',
    'LogisticRegModel',
    'SVMModel',
    'ARIMAModel',
    'LSTMModel'
]

__version__ = '1.0.0'
