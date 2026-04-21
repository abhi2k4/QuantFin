"""
API Router for ML Predictions and Portfolio Recommendations

This module provides REST API endpoints for accessing ML model predictions
and portfolio allocation recommendations.

Author: QuantFin Team
Date: 2025-10-09
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.services.predict_service import PredictionService
from app.services.feature_engineer import FeatureEngineer
from app.services.data_preprocessor import DataPreprocessor

# Create router
router = APIRouter(prefix="/api/predictions", tags=["predictions"])

# Global instances (initialized on startup)
preprocessor: Optional[DataPreprocessor] = None
feature_engineer: Optional[FeatureEngineer] = None
prediction_service: Optional[PredictionService] = None


def initialize_prediction_services():
    """Initialize prediction services on application startup."""
    global preprocessor, feature_engineer, prediction_service
    
    preprocessor = DataPreprocessor()
    
    feature_engineer = FeatureEngineer(preprocessor)
    prediction_service = PredictionService(feature_engineer)


def ensure_prediction_services_initialized():
    """Lazy-initialize prediction services if not already initialized."""
    global prediction_service
    if prediction_service is None:
        initialize_prediction_services()


@router.get("/symbols")
async def get_available_symbols():
    """
    Get list of symbols with trained models.
    
    Returns:
        Dict with available symbols per model type
    """
    try:
        ensure_prediction_services_initialized()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Prediction service not initialized: {str(e)}")
    
    # Check which models are available for which symbols
    available_models = {
        'linear_reg': [],
        'logreg': [],
        'svm': [],
        'arima': [],
        'lstm': []
    }
    
    # TODO: Scan models directory to find available models
    # For now, return empty lists
    
    return {
        'available_models': available_models,
        'total_symbols': len(preprocessor.get_stock_list()) if preprocessor else 0
    }


@router.post("/predict")
async def predict_symbols(
    symbols: List[str] = Query(..., description="List of stock symbols"),
    model: str = Query("ensemble", description="Model type or 'ensemble'"),
    horizon: int = Query(21, ge=1, le=252, description="Prediction horizon in days"),
    date: Optional[str] = Query(None, description="Prediction date (YYYY-MM-DD)")
):
    """
    Generate predictions for specified symbols.
    
    Args:
        symbols: List of stock symbols to predict
        model: Model type ('ensemble', 'linear_reg', 'logreg', 'svm', 'arima', 'lstm')
        horizon: Prediction horizon in trading days (1-252)
        date: Optional prediction date
    
    Returns:
        Predictions with portfolio allocation
    
    Example:
        POST /api/predictions/predict?symbols=RELIANCE&symbols=TCS&model=ensemble&horizon=21
    """
    try:
        ensure_prediction_services_initialized()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Prediction service not initialized: {str(e)}")
    
    # Validate symbols
    if not symbols:
        raise HTTPException(status_code=400, detail="At least one symbol required")
    
    # Validate model type
    valid_models = ['ensemble', 'linear_reg', 'logreg', 'svm', 'arima', 'lstm']
    if model not in valid_models:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model type. Must be one of: {valid_models}"
        )
    
    try:
        # Load models for requested symbols
        load_stats = prediction_service.load_models(
            symbols=symbols,
            models=['linear_reg', 'logreg', 'svm', 'arima', 'lstm'] if model == 'ensemble' else [model]
        )
        
        # Generate predictions
        results = prediction_service.predict(
            symbols=symbols,
            date=date,
            horizon=horizon,
            model=model
        )
        
        return {
            'success': True,
            'models_loaded': load_stats,
            'data': results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/portfolio")
async def generate_portfolio(
    symbols: List[str] = Query(..., description="List of stock symbols"),
    strategy: str = Query("model_weighted", description="Portfolio strategy"),
    model: str = Query("ensemble", description="Model type or 'ensemble'"),
    horizon: int = Query(21, description="Prediction horizon in days")
):
    """
    Generate portfolio allocation for specified symbols.
    
    Args:
        symbols: List of stock symbols
        strategy: Portfolio strategy ('model_weighted', 'mean_variance', 'risk_parity')
        model: Model type for predictions
        horizon: Prediction horizon
    
    Returns:
        Portfolio weights and expected metrics
    
    Example:
        POST /api/predictions/portfolio?symbols=RELIANCE&symbols=TCS&strategy=model_weighted
    """
    try:
        ensure_prediction_services_initialized()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Prediction service not initialized: {str(e)}")
    
    # Validate strategy
    valid_strategies = ['model_weighted', 'mean_variance', 'risk_parity']
    if strategy not in valid_strategies:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Must be one of: {valid_strategies}"
        )
    
    try:
        # Load models and generate predictions
        prediction_service.load_models(symbols=symbols)
        results = prediction_service.predict(
            symbols=symbols,
            horizon=horizon,
            model=model
        )
        
        # Generate portfolio with specified strategy
        portfolio = prediction_service._generate_portfolio_allocation(
            predictions=results['predictions'],
            strategy=strategy
        )
        
        return {
            'success': True,
            'portfolio': portfolio,
            'predictions_used': len(results['predictions'])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio generation failed: {str(e)}")


@router.get("/model/{symbol}/{model_type}")
async def get_model_info(
    symbol: str,
    model_type: str
):
    """
    Get information about a specific trained model.
    
    Args:
        symbol: Stock symbol
        model_type: Model type
    
    Returns:
        Model training metrics and metadata
    """
    valid_models = ['linear_reg', 'logreg', 'svm', 'arima', 'lstm']
    if model_type not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model type")
    
    try:
        # Load model to get metrics
        if model_type == 'linear_reg':
            from app.ml_models.linear_reg import LinearRegModel
            model = LinearRegModel(symbol)
        elif model_type == 'logreg':
            from app.ml_models.logreg import LogisticRegModel
            model = LogisticRegModel(symbol)
        elif model_type == 'svm':
            from app.ml_models.svm_model import SVMModel
            model = SVMModel(symbol)
        # elif model_type == 'arima':
        #     from app.ml_models.arima_model import ARIMAModel
        #     model = ARIMAModel(symbol)
        elif model_type == 'lstm':
            from app.ml_models.lstm_model import LSTMModel
            model = LSTMModel(symbol)
        
        metrics = model.load_model("latest")
        
        return {
            'success': True,
            'symbol': symbol,
            'model_type': model_type,
            'metrics': metrics
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Model not found for {symbol}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.get("/backtest/{symbol}")
async def backtest_predictions(
    symbol: str,
    model: str = Query("ensemble", description="Model type"),
    start_date: Optional[str] = Query(None, description="Backtest start date"),
    end_date: Optional[str] = Query(None, description="Backtest end date")
):
    """
    Backtest model predictions against historical data.
    
    Args:
        symbol: Stock symbol
        model: Model type
        start_date: Start date for backtest
        end_date: End date for backtest
    
    Returns:
        Backtest results with performance metrics
    """
    # TODO: Implement backtesting logic
    raise HTTPException(status_code=501, detail="Backtesting not yet implemented")


@router.get("/health")
async def prediction_service_health():
    """
    Check health status of prediction service.
    
    Returns:
        Service health status
    """
    try:
        ensure_prediction_services_initialized()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Prediction service not initialized: {str(e)}")

    status = {
        'service': 'predictions',
        'status': 'healthy' if prediction_service is not None else 'unhealthy',
        'preprocessor_loaded': preprocessor is not None,
        'feature_engineer_loaded': feature_engineer is not None,
        'prediction_service_loaded': prediction_service is not None,
        'timestamp': datetime.now().isoformat()
    }
    
    if status['status'] == 'unhealthy':
        raise HTTPException(status_code=503, detail="Prediction service not initialized")
    
    return status
