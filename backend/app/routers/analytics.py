"""
API Router for Analytics and Model Performance

This module provides REST API endpoints for accessing ML model performance
metrics, training status, and candlestick data with REAL DATA integration.

Author: QuantFin Team
Date: 2025-10-30
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from pathlib import Path
import logging
import asyncio
import multiprocessing

from app.services.ml_training_service import get_training_service
from app.services.real_data_service import RealDataService
from app.services.training_state import save_training_state

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Get training service
training_service = get_training_service()


def run_training_sync(force: bool):
    """Synchronous wrapper to run async training in a worker process."""
    import sys
    
    try:
        # Print to console immediately (bypasses logging buffer)
        print("\n" + "=" * 80, flush=True)
        print(f"🚀 STARTING MODEL TRAINING (force={force})", flush=True)
        print("=" * 80 + "\n", flush=True)
        
        logger.info("=" * 80)
        logger.info(f"🚀 STARTING MODEL TRAINING (force={force})")
        logger.info("=" * 80)
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("📊 Training service initialized", flush=True)
        print(f"🔄 Force retrain: {force}", flush=True)
        print("⏳ This will take 30-60 seconds...", flush=True)
        print("", flush=True)
        
        logger.info("📊 Training service initialized")
        logger.info(f"🔄 Force retrain: {force}")
        logger.info("⏳ This will take 30-60 seconds...")
        logger.info("")
        
        result = loop.run_until_complete(training_service.train_all_models(force))
        loop.close()
        
        print("", flush=True)
        print("=" * 80, flush=True)
        print("✅ MODEL TRAINING COMPLETED SUCCESSFULLY", flush=True)
        print("=" * 80 + "\n", flush=True)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ MODEL TRAINING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        return result
    except Exception as e:
        error_msg = f"❌ TRAINING FAILED: {e}"
        print("\n" + "=" * 80, flush=True)
        print(error_msg, flush=True)
        print("=" * 80 + "\n", flush=True)
        
        logger.error("=" * 80)
        logger.error(error_msg)
        logger.error("=" * 80)
        logger.error("Full error:", exc_info=True)
        training_service.training_status['status'] = 'failed'
        training_service.training_status['error'] = str(e)
        raise


@router.post("/models/train")
async def train_models(
    force: bool = Query(False, description="Force retrain even if cache exists")
):
    """
    Start training all ML models in the background.
    
    This endpoint initiates real model training with actual stock data.
    Training runs asynchronously and takes 30-60 seconds.
    Use GET /models/training-status to check progress.
    
    Args:
        force: If True, ignore cache and retrain all models
    
    Returns:
        Training job status
    """
    try:
        # Check if already training
        status = training_service.get_training_status()
        if status['status'] == 'training':
            return {
                "message": "Training already in progress",
                "status": status
            }
        
        # Mark training state immediately so polling starts returning progress.
        save_training_state({
            "status": "training",
            "progress": 0,
            "current_model": None,
            "models_completed": [],
            "error": None,
            "started_at": None,
            "completed_at": None,
        })

        # Start training in a separate process so the API worker stays responsive.
        process = multiprocessing.Process(target=run_training_sync, args=(force,), daemon=True)
        process.start()
        
        logger.info(f"Queued background training task (force={force})")
        
        return {
            "message": "Model training started",
            "status": "training",
            "estimated_time_seconds": 45
        }
        
    except Exception as e:
        logger.error(f"Error starting training: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/training-status")
async def get_training_status():
    """
    Get current training status and progress.
    
    Returns:
        Training status including progress percentage and current model
    """
    try:
        status = training_service.get_training_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_model_performance():
    """
    Get ML model performance metrics from cache or return cached results.
    
    If models haven't been trained, use POST /models/train to train them first.
    
    Returns:
        List of model performance metrics including accuracy, RMSE, MAE, R² score
    
    Example:
        GET /api/analytics/models
    """
    try:
        # Check for cached models
        model_names = ["LSTM", "Linear Regression", "SVM", "ARIMA"]
        models_data = []
        
        for model_name in model_names:
            if training_service.is_cache_valid(model_name):
                cached = training_service.load_cached_model(model_name)
                if cached:
                    models_data.append(cached)
        
        if models_data:
            logger.info(f"Returning {len(models_data)} cached models")
            return {"models": models_data}
        
        # No cached models - return empty with message
        logger.warning("No trained models found. Client should call POST /models/train")
        return {
            "models": [],
            "message": "No trained models available. Please train models first using POST /api/analytics/models/train"
        }
    
    except Exception as e:
        logger.error(f"Error fetching model performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model performance: {str(e)}"
        )


@router.get("/candlestick/{symbol}")
async def get_candlestick_data(
    symbol: str,
    days: int = Query(90, ge=1, le=365, description="Number of days of data")
):
    """
    Get candlestick (OHLCV) data for a specific symbol.
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        days: Number of days of historical data (default 90)
    
    Returns:
        OHLCV data with statistics
    
    Example:
        GET /api/analytics/candlestick/RELIANCE?days=90
    """
    try:
        data_service = RealDataService()
        
        # Get OHLCV data as DataFrame
        df = data_service.get_ohlcv_data(symbol, last_n_days=days)
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for symbol: {symbol}"
            )
        
        # Rename columns to lowercase for frontend compatibility
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Convert DataFrame to list of dicts
        candlestick_data = df.to_dict('records')
        
        # Calculate statistics from DataFrame
        stats = {
            "high": float(df['high'].max()),
            "low": float(df['low'].min()),
            "avg_volume": int(df['volume'].mean()),
            "total_days": len(df)
        }
        
        return {
            "symbol": symbol,
            "data": candlestick_data,
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candlestick data for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving candlestick data: {str(e)}"
        )


@router.get("/kpis")
async def get_analytics_kpis():
    """
    Get key performance indicators for the portfolio.
    
    Returns:
        Portfolio KPIs including return, risk, volatility, sharpe ratio
    """
    try:
        from app.services.portfolio_manager import get_portfolio_manager

        portfolio_manager = get_portfolio_manager()

        # Use real computed performance metrics from historical portfolio data
        perf_1y = portfolio_manager.get_portfolio_performance("1Y")
        summary = portfolio_manager.get_portfolio_summary()

        metrics = perf_1y.get("metrics", {})
        total_return = float(metrics.get("total_return", 0.0))
        volatility = float(metrics.get("volatility", 0.0))
        sharpe_ratio = float(metrics.get("sharpe_ratio", 0.0))

        # Simple risk score proxy from volatility (percentage -> decimal)
        risk_metric = round(max(0.0, min(1.0, volatility / 100.0)), 4)

        return {
            "portfolio_return": round(total_return / 100.0, 4),
            "risk_metric": risk_metric,
            "volatility": round(volatility / 100.0, 4),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "total_value": float(summary.get("total_value", 0.0)),
            "cash_balance": float(summary.get("cash_balance", 0.0))
        }
    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating KPIs: {str(e)}"
        )
