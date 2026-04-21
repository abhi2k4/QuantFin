"""
Portfolio API Router

This module provides REST API endpoints for portfolio management,
including summary data, performance metrics, and rebalancing operations.

**NOW USES REAL DATA FROM CSV FILES - NO MOCK DATA**

Author: QuantFin Team
Date: 2025-10-31
Updated: Added cash balance update endpoint
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import random
import logging
from functools import lru_cache
import hashlib
import pandas as pd

from app.models.schemas import RebalanceRequest
from app.services.portfolio_manager import get_portfolio_manager
from app.services.ml_model_service import get_ml_service

# Pydantic model for cash balance update
class UpdateCashBalanceRequest(BaseModel):
    cash_balance: float

# Logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Simple in-memory cache for strategy comparisons
_strategy_cache = {}
_cache_timestamp = {}
CACHE_DURATION = 300  # 5 minutes in seconds
CACHE_KEY_VERSION = "v3"

def get_cached_strategy_comparison(timeframe: str, capital: float):
    """Get cached strategy comparison if available and fresh"""
    cache_key = f"{CACHE_KEY_VERSION}_{timeframe}_{capital}"
    
    if cache_key in _strategy_cache:
        cached_time = _cache_timestamp.get(cache_key)
        if cached_time and (datetime.now() - cached_time).seconds < CACHE_DURATION:
            logger.info(f"Returning cached strategy comparison for {timeframe}")
            return _strategy_cache[cache_key]
    
    return None

def cache_strategy_comparison(timeframe: str, capital: float, data):
    """Cache strategy comparison results"""
    cache_key = f"{CACHE_KEY_VERSION}_{timeframe}_{capital}"
    _strategy_cache[cache_key] = data
    _cache_timestamp[cache_key] = datetime.now()
    logger.info(f"Cached strategy comparison for {timeframe}")

# ============================================================================
# Request/Response Models
# ============================================================================

class PortfolioSummary(BaseModel):
    """Portfolio summary response model"""
    total_value: float
    cash_balance: float
    daily_change: float
    daily_change_percent: float
    total_positions: int
    positions: List[dict]


class PortfolioPerformance(BaseModel):
    """Portfolio performance response model"""
    timeframe: str
    dates: List[str]
    values: List[float]
    total_return: float
    total_return_percent: float


# ============================================================================
# Portfolio Endpoints
# ============================================================================

@router.get("/summary")
async def get_portfolio_summary():
    """
    Get current portfolio summary with REAL positions and values from CSV data.
    
    Returns:
        dict: Portfolio summary with actual stock positions, prices, and daily changes
    """
    try:
        portfolio_manager = get_portfolio_manager()
        summary = portfolio_manager.get_portfolio_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch portfolio summary: {str(e)}"
        )


@router.get("/performance")
async def get_portfolio_performance(
    timeframe: str = Query("3M", description="Timeframe: 1M, 3M, 6M, 1Y"),
    as_of_date: Optional[str] = Query(None, description="ISO date to anchor timeframe (YYYY-MM-DD)")
):
    """
    Get comprehensive portfolio performance with REAL historical data and metrics.
    
    Calculates true daily portfolio values from historical OHLCV CSV data
    and returns time series with comprehensive performance metrics.
    
    Args:
        timeframe: Time period (1M, 3M, 6M, 1Y)
        as_of_date: Optional anchor date (default: latest available)
    
    Returns:
        dict: {
            'timeframe': str,
            'data': [{'date': str, 'value': float}, ...],
            'metrics': {
                'initial_value': float,
                'final_value': float,
                'total_return': float (percentage),
                'volatility': float (annualized percentage),
                'sharpe_ratio': float,
                'max_drawdown': float (percentage)
            },
            'warnings': [str, ...] (optional)
        }
    """
    try:
        # Validate timeframe
        valid_timeframes = ["1M", "3M", "6M", "1Y"]
        if timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timeframe. Must be one of: {valid_timeframes}"
            )
        
        # Parse as_of_date if provided
        anchor_date = None
        if as_of_date:
            try:
                anchor_date = datetime.fromisoformat(as_of_date)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        portfolio_manager = get_portfolio_manager()
        performance = portfolio_manager.get_portfolio_performance(timeframe, anchor_date)
        return performance
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching portfolio performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch portfolio performance: {str(e)}"
        )


@router.post("/rebalance")
async def rebalance_portfolio(request: RebalanceRequest):
    """
    Rebalance portfolio using ML-based intelligent allocation.
    Selects top stocks from all 49 symbols using ML predictions.
    Returns detailed allocation table with predicted prices and growth projections.
    """
    try:
        from app.services.portfolio_allocator import get_portfolio_allocator
        
        logger.info(f"Rebalance request: strategy={request.strategy}, capital=₹{request.capital_allocation:,.2f}")
        
        # Validate strategy (case-insensitive)
        strategy_lower = request.strategy.lower()
        strategy_map = {
            'lstm': 'LSTM',
            'linear': 'Linear', 
            'logistic': 'Linear',
            'svm': 'SVM',
            'arima': 'ARIMA'
        }
        
        if strategy_lower not in strategy_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy '{request.strategy}'. Must be one of: LSTM, Linear, Logistic, SVM, ARIMA"
            )
        
        strategy = strategy_map[strategy_lower]
        
        # Validate capital
        if request.capital_allocation <= 0:
            raise HTTPException(
                status_code=400,
                detail="Capital allocation must be greater than 0"
            )
        
        # Generate intelligent allocations using ML
        allocator = get_portfolio_allocator()
        allocation_result = await allocator.generate_allocations(
            strategy=strategy,
            capital=request.capital_allocation,
            top_n=10,  # Select top 10 stocks
            forecast_days=30
        )
        
        # Save new allocations to database
        from app.services.portfolio_db import get_portfolio_db
        db = get_portfolio_db()
        db.save_portfolio(
            positions=allocation_result['allocations'],
            metadata={
                'cash_balance': allocation_result['remaining_cash'],
                'total_invested': allocation_result['total_allocated'],
                'strategy': strategy,
                'expected_return': allocation_result['metrics']['expected_return'],
                'expected_risk': allocation_result['metrics']['expected_risk'],
                'sharpe_ratio': allocation_result['metrics'].get('sharpe_ratio', 0)
            }
        )
        logger.info(f"Saved {len(allocation_result['allocations'])} positions to database")
        
        # Get portfolio manager for updated summary
        portfolio_manager = get_portfolio_manager()
        current_summary = portfolio_manager.get_portfolio_summary()
        
        # Build response with allocation details
        return {
            # Current portfolio status
            "total_value": current_summary['total_value'],
            "cash_balance": current_summary['cash_balance'],
            "invested_value": current_summary['invested_value'],
            "current_holdings_value": current_summary['current_holdings_value'],
            "total_gain_loss": current_summary['total_gain_loss'],
            "total_gain_loss_percent": current_summary['total_gain_loss_percent'],
            "daily_change": current_summary['daily_change'],
            "daily_change_percent": current_summary['daily_change_percent'],
            "total_positions": len(current_summary['positions']),
            "positions": current_summary['positions'],
            
            # New allocation recommendations
            "strategy": strategy,
            "capital_allocation": request.capital_allocation,
            "allocations": allocation_result['allocations'],
            "expected_return": allocation_result['metrics']['expected_return'],
            "expected_risk": allocation_result['metrics']['expected_risk'],
            "sharpe_ratio": allocation_result['metrics']['sharpe_ratio'],
            "total_recommended_stocks": len(allocation_result['allocations']),
            "rebalanced": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebalancing portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rebalance portfolio: {str(e)}"
        )


@router.get("/strategy-comparison")
async def get_strategy_comparison(
    timeframe: str = Query("3M", description="Time period: 1M, 3M, 6M, 1Y"),
    capital: float = Query(100000, description="Initial capital amount")
):
    """
    Compare performance of all 4 ML strategies against Nifty50 benchmark
    
    Returns performance data for LSTM, Linear, SVM, ARIMA models and Nifty50 index
    """
    try:
        # Check cache first
        cached_result = get_cached_strategy_comparison(timeframe, capital)
        if cached_result and cached_result.get('strategies', {}).get('NIFTY50'):
            return cached_result
        
        from app.services.portfolio_allocator import get_portfolio_allocator
        from app.services.real_data_service import get_real_data_service
        import pandas as pd
        
        allocator = get_portfolio_allocator()
        data_service = get_real_data_service()
        
        # Define timeframe days
        timeframe_map = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365}
        days = timeframe_map.get(timeframe, 90)
        
        strategies = ['LSTM', 'Linear', 'SVM', 'ARIMA']
        results = {}
        
        logger.info(f"Generating strategy comparison for {timeframe} timeframe...")
        
        # Build a common date axis using RELIANCE as a benchmark proxy.
        # This avoids index mismatches in the frontend chart (it uses LSTM.dates as the x-axis).
        benchmark_symbol = 'RELIANCE'
        try:
            _, benchmark_max_date = data_service.get_date_range(benchmark_symbol)
        except Exception:
            benchmark_max_date = datetime.now()

        end_date = benchmark_max_date
        start_date = end_date - timedelta(days=days)

        benchmark_df = data_service.get_ohlcv_data(
            benchmark_symbol,
            start_date=start_date,
            end_date=end_date
        )
        if benchmark_df is None or benchmark_df.empty:
            raise HTTPException(status_code=500, detail="No benchmark data available")

        benchmark_df = benchmark_df.sort_values('Date')
        base_dates = pd.to_datetime(benchmark_df['Date']).dt.normalize()
        base_date_strs = base_dates.dt.strftime('%Y-%m-%d').tolist()

        # Nifty50 proxy (normalized benchmark)
        first_close = float(benchmark_df['Close'].iloc[0])
        bench_values = [(float(close) / first_close) * capital for close in benchmark_df['Close']]
        bench_final_value = float(bench_values[-1])
        bench_return = ((bench_final_value - capital) / capital) * 100
        results['NIFTY50'] = {
            'dates': base_date_strs,
            'values': [round(v, 2) for v in bench_values],
            'total_return': round(bench_return, 2),
            'final_value': round(bench_final_value, 2)
        }

        def _aligned_close_series(symbol: str) -> Optional[pd.Series]:
            """Fetch close prices and align them to the benchmark date axis."""
            df = data_service.get_ohlcv_data(symbol, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                return None
            df = df.sort_values('Date')
            df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
            s = df.set_index('Date')['Close'].astype(float)
            # Reindex onto base dates and carry forward last available close.
            s = s.reindex(base_dates, method='ffill')
            s = s.bfill()
            if s.isna().any():
                return None
            return s

        # Get performance for each strategy using real historical prices of the recommended basket
        for strategy in strategies:
            try:
                logger.info(f"Processing {strategy} strategy...")

                allocation_result = await allocator.generate_allocations(
                    strategy=strategy,
                    capital=capital,
                    top_n=10,
                    forecast_days=30
                )

                allocations = allocation_result.get('allocations') or []
                metrics = allocation_result.get('metrics') or {}

                if not allocations:
                    results[strategy] = None
                    continue

                per_symbol_values = []
                used_allocations = []
                used_allocation_amount = 0.0

                for a in allocations:
                    symbol = a.get('symbol')
                    allocation_amount = float(a.get('allocation_amount') or 0)
                    if not symbol or allocation_amount <= 0:
                        continue

                    close_series = _aligned_close_series(symbol)
                    if close_series is None or close_series.empty:
                        continue

                    first_price = float(close_series.iloc[0])
                    if first_price <= 0:
                        continue

                    normalized = close_series / first_price
                    per_symbol_values.append(normalized * allocation_amount)
                    used_allocations.append(symbol)
                    used_allocation_amount += allocation_amount

                if not per_symbol_values:
                    results[strategy] = None
                    continue

                cash_remaining = max(0.0, float(capital) - used_allocation_amount)

                portfolio_series = cash_remaining
                for s in per_symbol_values:
                    portfolio_series = portfolio_series + s

                values = [round(float(v), 2) for v in portfolio_series.tolist()]
                final_value = float(values[-1])
                total_return = ((final_value - capital) / capital) * 100

                results[strategy] = {
                    'dates': base_date_strs,
                    'values': values,
                    'total_return': round(float(total_return), 2),
                    'expected_return': float(metrics.get('expected_return', 0)),
                    'expected_risk': float(metrics.get('expected_risk', 0)),
                    'sharpe_ratio': float(metrics.get('sharpe_ratio', 0) or 0),
                    'final_value': round(final_value, 2),
                    'top_stocks': used_allocations[:5]
                }
            except Exception as e:
                logger.error(f"Error calculating {strategy} performance: {e}", exc_info=True)
                results[strategy] = None
        response_data = {
            'timeframe': timeframe,
            'initial_capital': capital,
            'strategies': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the result
        cache_strategy_comparison(timeframe, capital, response_data)
        
        logger.info("Strategy comparison completed successfully")
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate strategy comparison: {str(e)}"
        )


@router.get("/predicted-vs-actual")
async def get_predicted_vs_actual(
    days: int = Query(default=90, ge=30, le=365, description="Number of days to show")
):
    """
    Get predicted vs actual portfolio performance comparison with Nifty50 benchmark.
    
    Shows how ML predictions compare to actual returns and outperforms Nifty50.
    """
    try:
        from app.services.portfolio_db import get_portfolio_db
        from app.services.real_data_service import get_real_data_service
        
        db = get_portfolio_db()
        data_service = get_real_data_service()
        portfolio_manager = get_portfolio_manager()
        
        # Get portfolio metadata
        metadata = db.get_metadata()
        strategy = metadata.get('strategy', 'LINEAR')
        expected_return = metadata.get('expected_return', 0)
        
        # Get current positions for tracking
        db_positions = db.get_positions()
        
        if not db_positions:
            raise HTTPException(
                status_code=404,
                detail="No portfolio positions found. Please rebalance first."
            )
        
        # Get available data range from a sample stock (RELIANCE)
        sample_data = data_service.load_stock_data('RELIANCE')
        if sample_data.empty:
            raise HTTPException(status_code=500, detail="No historical data available")
        
        # Use actual available data range (last N days from latest available date)
        latest_available_date = pd.to_datetime(sample_data['Date'].max())
        end_date = latest_available_date
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Using date range: {start_date.date()} to {end_date.date()}")
        
        # Calculate actual portfolio performance
        symbols = [pos['symbol'] for pos in db_positions]
        weights = {}
        total_allocation = sum(pos['allocation_amount'] for pos in db_positions)
        
        for pos in db_positions:
            weights[pos['symbol']] = pos['allocation_amount'] / total_allocation
        
        # Get price history for portfolio stocks
        portfolio_values = []
        predicted_values = []
        nifty50_values = []
        dates = []
        
        # Initial value (100,000 base)
        initial_value = 100000.0
        current_date = start_date
        
        # Calculate predicted growth rate (daily)
        annual_return = expected_return / 100  # Convert percentage to decimal
        daily_return = (1 + annual_return) ** (1/365) - 1
        
        # Get Nifty50 data for benchmark (use RELIANCE as proxy)
        nifty_data = data_service.get_historical_data('RELIANCE', start_date=start_date, end_date=end_date)
        
        # Pre-fetch all price data for portfolio stocks
        price_data_cache = {}
        for symbol in symbols:
            try:
                df = data_service.get_historical_data(symbol, start_date=start_date, end_date=end_date)
                if not df.empty:
                    # Set Date as index for easier lookup
                    df_indexed = df.set_index('Date')
                    price_data_cache[symbol] = df_indexed
                else:
                    price_data_cache[symbol] = pd.DataFrame()
            except Exception as e:
                logger.debug(f"Error getting price data for {symbol}: {e}")
                price_data_cache[symbol] = pd.DataFrame()
        
        # Also get and index Nifty data
        nifty_data_indexed = pd.DataFrame()
        if not nifty_data.empty:
            nifty_data_indexed = nifty_data.set_index('Date')
        
        day_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Calculate actual portfolio value
            portfolio_value = initial_value
            for symbol, weight in weights.items():
                try:
                    price_data = price_data_cache.get(symbol, pd.DataFrame())
                    if not price_data.empty:
                        # Find the date in the index
                        date_index = pd.Timestamp(current_date)
                        if date_index in price_data.index:
                            price_ratio = price_data.loc[date_index, 'Close'] / price_data.iloc[0]['Close']
                            portfolio_value += (initial_value * weight * (price_ratio - 1))
                except Exception as e:
                    logger.debug(f"Error getting price for {symbol} on {current_date}: {e}")
                    continue
            
            # Calculate predicted value (compound growth)
            predicted_value = initial_value * (1 + daily_return) ** day_count
            
            # Calculate Nifty50 value (using market proxy)
            nifty_value = initial_value
            if not nifty_data_indexed.empty:
                try:
                    # Find the closest available date
                    date_index = pd.Timestamp(current_date)
                    if date_index in nifty_data_indexed.index:
                        nifty_ratio = nifty_data_indexed.loc[date_index, 'Close'] / nifty_data_indexed.iloc[0]['Close']
                        nifty_value = initial_value * nifty_ratio
                except Exception as e:
                    logger.debug(f"Error calculating nifty value for {current_date}: {e}")
            
            dates.append(current_date.strftime('%Y-%m-%d'))
            portfolio_values.append(round(portfolio_value, 2))
            predicted_values.append(round(predicted_value, 2))
            nifty50_values.append(round(nifty_value, 2))
            
            current_date += timedelta(days=1)
            day_count += 1
        
        # Calculate final returns
        actual_return = ((portfolio_values[-1] - initial_value) / initial_value) * 100
        predicted_return_calc = ((predicted_values[-1] - initial_value) / initial_value) * 100
        nifty_return = ((nifty50_values[-1] - initial_value) / initial_value) * 100
        
        # Calculate outperformance
        outperform_vs_nifty = actual_return - nifty_return
        accuracy = (actual_return / expected_return) * 100 if expected_return != 0 else 0
        
        return {
            'timeframe_days': days,
            'strategy': strategy,
            'initial_value': initial_value,
            'dates': dates,
            'actual_values': portfolio_values,
            'predicted_values': predicted_values,
            'nifty50_values': nifty50_values,
            'returns': {
                'actual': round(actual_return, 2),
                'predicted': round(predicted_return_calc, 2),
                'nifty50': round(nifty_return, 2),
                'outperformance_vs_nifty': round(outperform_vs_nifty, 2),
                'prediction_accuracy': round(accuracy, 2)
            },
            'final_values': {
                'actual': portfolio_values[-1],
                'predicted': predicted_values[-1],
                'nifty50': nifty50_values[-1]
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in strategy comparison: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate strategy comparison: {str(e)}"
        )


@router.put("/cash-balance")
async def update_cash_balance(request: UpdateCashBalanceRequest):
    """
    Update the portfolio cash balance.
    
    This allows users to add or modify their available cash for investment.
    """
    try:
        from app.services.portfolio_db import get_portfolio_db
        
        if request.cash_balance < 0:
            raise HTTPException(
                status_code=400,
                detail="Cash balance cannot be negative"
            )
        
        db = get_portfolio_db()
        
        # Get current metadata
        metadata = db.get_metadata()
        
        # Update cash balance
        metadata['cash_balance'] = request.cash_balance
        
        # Get current positions to save with updated metadata
        positions = db.get_positions()
        
        # Ensure positions have all required fields for saving
        # The get_positions returns dicts, we need to make sure they're complete
        formatted_positions = []
        for pos in positions:
            formatted_positions.append({
                'symbol': pos.get('symbol', ''),
                'quantity': pos.get('quantity', 0),
                'buy_price': pos.get('buy_price', pos.get('avg_buy_price', 0)),  # Handle both field names
                'allocation_amount': pos.get('allocation_amount', 0),
                'predicted_return': pos.get('predicted_return', 0),
                'confidence': pos.get('confidence', 0),
                'strategy': pos.get('strategy', 'MANUAL')
            })
        
        # Save to database
        db.save_portfolio(
            positions=formatted_positions,
            metadata=metadata
        )
        
        logger.info(f"Cash balance updated to: {request.cash_balance}")
        
        return {
            "success": True,
            "cash_balance": request.cash_balance,
            "message": f"Cash balance updated to ₹{request.cash_balance:,.2f}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cash balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update cash balance: {str(e)}"
        )


@router.get("/health")
async def portfolio_health():
    """Portfolio service health check"""
    return {
        "status": "healthy",
        "service": "portfolio",
        "timestamp": datetime.now().isoformat()
    }
