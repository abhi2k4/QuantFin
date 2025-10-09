"""
API Router for Portfolio Backtesting

This module provides REST API endpoints for running historical portfolio
simulations using trained ML models and various allocation strategies.

Author: QuantFin Team
Date: 2025-10-09
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

from pydantic import BaseModel, Field, validator

from app.services.backtester import Backtester

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/backtest", tags=["backtest"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class BacktestRequest(BaseModel):
    """Request schema for running a backtest."""
    
    symbols: List[str] = Field(
        ...,
        description="List of stock symbols to include in portfolio",
        min_items=1,
        max_items=50,
        example=["RELIANCE", "TCS", "INFY", "HDFCBANK"]
    )
    start_date: str = Field(
        ...,
        description="Backtest start date (YYYY-MM-DD)",
        example="2024-01-01"
    )
    end_date: str = Field(
        ...,
        description="Backtest end date (YYYY-MM-DD)",
        example="2025-09-30"
    )
    strategy: str = Field(
        default="model_weighted",
        description="Portfolio allocation strategy",
        example="model_weighted"
    )
    rebalance_freq: int = Field(
        default=21,
        ge=1,
        le=252,
        description="Rebalancing frequency in trading days (21 = monthly)",
        example=21
    )
    initial_capital: float = Field(
        default=100000.0,
        gt=0,
        description="Initial portfolio capital in rupees",
        example=100000.0
    )
    transaction_cost: float = Field(
        default=0.001,
        ge=0,
        le=0.1,
        description="Transaction cost as decimal (0.001 = 0.1%)",
        example=0.001
    )
    models_dir: str = Field(
        default="models",
        description="Directory containing trained models",
        example="models"
    )
    
    @validator('strategy')
    def validate_strategy(cls, v):
        """Validate portfolio strategy."""
        allowed = ['model_weighted', 'mean_variance', 'risk_parity']
        if v not in allowed:
            raise ValueError(f"Strategy must be one of {allowed}")
        return v
    
    @validator('start_date', 'end_date')
    def validate_date(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate end date is after start date."""
        if 'start_date' in values:
            start = datetime.strptime(values['start_date'], '%Y-%m-%d')
            end = datetime.strptime(v, '%Y-%m-%d')
            if end <= start:
                raise ValueError("end_date must be after start_date")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "symbols": ["RELIANCE", "TCS", "INFY", "HDFCBANK"],
                "start_date": "2024-01-01",
                "end_date": "2025-09-30",
                "strategy": "model_weighted",
                "rebalance_freq": 21,
                "initial_capital": 100000.0,
                "transaction_cost": 0.001,
                "models_dir": "models"
            }
        }


class DailyResult(BaseModel):
    """Daily portfolio result."""
    date: str
    portfolio_value: float
    daily_return: float
    cash: float = 0.0


class MetricsResponse(BaseModel):
    """Portfolio performance metrics."""
    annualized_return: float = Field(..., description="Annualized portfolio return")
    annualized_volatility: float = Field(..., description="Annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio (risk-free rate = 0)")
    max_drawdown: float = Field(..., description="Maximum drawdown from peak")
    win_rate: float = Field(..., description="Percentage of profitable days")
    total_return: float = Field(..., description="Total cumulative return")
    final_value: float = Field(..., description="Final portfolio value")
    num_trades: int = Field(default=0, description="Number of rebalancing events")


class BacktestResponse(BaseModel):
    """Response schema for backtest results."""
    
    configuration: Dict[str, Any] = Field(..., description="Backtest configuration")
    daily_results: List[DailyResult] = Field(..., description="Daily portfolio values")
    cumulative_returns: List[float] = Field(..., description="Cumulative return series")
    drawdowns: List[float] = Field(..., description="Drawdown series from peak")
    metrics: MetricsResponse = Field(..., description="Performance metrics")
    warnings: List[str] = Field(default=[], description="Any warnings during backtest")
    
    class Config:
        schema_extra = {
            "example": {
                "configuration": {
                    "symbols": ["RELIANCE", "TCS"],
                    "strategy": "model_weighted",
                    "start_date": "2024-01-01",
                    "end_date": "2025-09-30"
                },
                "daily_results": [
                    {"date": "2024-01-01", "portfolio_value": 100000.0, "daily_return": 0.0},
                    {"date": "2024-01-02", "portfolio_value": 101234.5, "daily_return": 0.012345}
                ],
                "cumulative_returns": [0.0, 0.012345, 0.025678],
                "drawdowns": [0.0, 0.0, -0.002341],
                "metrics": {
                    "annualized_return": 0.152,
                    "annualized_volatility": 0.214,
                    "sharpe_ratio": 0.71,
                    "max_drawdown": -0.082,
                    "win_rate": 0.54,
                    "total_return": 0.15,
                    "final_value": 115000.0,
                    "num_trades": 24
                },
                "warnings": []
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: str
    models_available: bool = False
    data_available: bool = False


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for backtesting service.
    
    Returns:
        Service status and availability information
    """
    logger.info("Health check requested")
    
    # Check if models directory exists
    models_dir = Path("models")
    models_available = models_dir.exists() and any(models_dir.iterdir())
    
    # Check if data directory exists
    data_dir = Path("data")
    data_available = data_dir.exists() and any(data_dir.glob("*.csv"))
    
    return HealthResponse(
        status="healthy",
        service="backtesting",
        timestamp=datetime.now().isoformat(),
        models_available=models_available,
        data_available=data_available
    )


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest = Body(...)):
    """
    Run a historical portfolio backtest.
    
    This endpoint simulates trading a portfolio of stocks using trained ML models
    and evaluates performance with the specified allocation strategy.
    
    **Strategies:**
    - `model_weighted`: Weights based on predicted returns × confidence (momentum)
    - `mean_variance`: Markowitz optimization (minimize portfolio variance)
    - `risk_parity`: Equal risk contribution from each asset
    
    **Example Request:**
    ```json
    {
        "symbols": ["RELIANCE", "TCS", "INFY"],
        "start_date": "2024-01-01",
        "end_date": "2025-09-30",
        "strategy": "model_weighted",
        "rebalance_freq": 21
    }
    ```
    
    Args:
        request: Backtest configuration parameters
        
    Returns:
        Complete backtest results with daily values, metrics, and drawdowns
        
    Raises:
        HTTPException: If backtest fails or validation errors occur
    """
    logger.info(
        f"Starting backtest: symbols={request.symbols}, "
        f"strategy={request.strategy}, "
        f"period={request.start_date} to {request.end_date}"
    )
    
    warnings_list = []
    
    try:
        # Validate data availability
        data_dir = Path("data")
        if not data_dir.exists():
            raise HTTPException(
                status_code=500,
                detail="Data directory not found. Please ensure stock data is available."
            )
        
        # Check if requested symbols have data files
        missing_symbols = []
        for symbol in request.symbols:
            data_file = data_dir / f"{symbol}.csv"
            if not data_file.exists():
                missing_symbols.append(symbol)
                warnings_list.append(f"Data file not found for {symbol}")
        
        if missing_symbols:
            logger.warning(f"Missing data files for symbols: {missing_symbols}")
            if len(missing_symbols) == len(request.symbols):
                raise HTTPException(
                    status_code=404,
                    detail=f"No data files found for any requested symbols: {missing_symbols}"
                )
        
        # Initialize backtester
        logger.debug(f"Initializing backtester with {len(request.symbols)} symbols")
        backtester = Backtester(
            models_dir=request.models_dir,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy=request.strategy,
            rebalance_freq=request.rebalance_freq,
            initial_capital=request.initial_capital,
            transaction_cost=request.transaction_cost
        )
        
        # Run backtest
        logger.info(f"Executing backtest with {request.strategy} strategy")
        results = backtester.run_backtest()
        
        # Check if backtest was successful
        if not results or 'daily_values' not in results or not results['daily_values']:
            error_msg = "Backtest failed - no data available or no valid trading days found"
            logger.error(error_msg)
            raise HTTPException(
                status_code=404,
                detail=f"{error_msg}. Please check that CSV files exist in data/ directory for: {missing_symbols if missing_symbols else request.symbols}"
            )
        
        # Extract results
        portfolio_values = results['daily_values']
        dates = results['daily_dates']
        metrics = results['metrics']
        
        # Calculate daily returns
        daily_returns = []
        cumulative_returns = []
        drawdowns = []
        
        peak = portfolio_values[0]
        initial_value = portfolio_values[0]
        
        for i, value in enumerate(portfolio_values):
            # Daily return
            if i == 0:
                daily_return = 0.0
            else:
                daily_return = (value - portfolio_values[i-1]) / portfolio_values[i-1]
            daily_returns.append(daily_return)
            
            # Cumulative return
            cumulative_return = (value - initial_value) / initial_value
            cumulative_returns.append(cumulative_return)
            
            # Drawdown
            if value > peak:
                peak = value
            drawdown = (value - peak) / peak
            drawdowns.append(drawdown)
        
        # Build daily results
        daily_results_list = [
            DailyResult(
                date=str(dates[i]),
                portfolio_value=float(portfolio_values[i]),
                daily_return=float(daily_returns[i]),
                cash=0.0  # Cash tracking can be added if needed
            )
            for i in range(len(dates))
        ]
        
        # Build metrics response
        metrics_response = MetricsResponse(
            annualized_return=float(metrics['annualized_return']),
            annualized_volatility=float(metrics['annualized_volatility']),
            sharpe_ratio=float(metrics['sharpe_ratio']),
            max_drawdown=float(metrics['max_drawdown']),
            win_rate=float(metrics['win_rate']),
            total_return=float(cumulative_returns[-1]),
            final_value=float(portfolio_values[-1]),
            num_trades=results.get('trades', 0)  # Already an integer, not a list
        )
        
        # Build configuration summary
        config_summary = {
            "symbols": request.symbols,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "strategy": request.strategy,
            "rebalance_freq": request.rebalance_freq,
            "initial_capital": request.initial_capital,
            "transaction_cost": request.transaction_cost,
            "trading_days": len(dates)
        }
        
        logger.info(
            f"Backtest completed successfully: "
            f"return={metrics_response.annualized_return:.2%}, "
            f"sharpe={metrics_response.sharpe_ratio:.2f}"
        )
        
        # Return response
        return BacktestResponse(
            configuration=config_summary,
            daily_results=daily_results_list,
            cumulative_returns=cumulative_returns,
            drawdowns=drawdowns,
            metrics=metrics_response,
            warnings=warnings_list
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except ValueError as e:
        logger.error(f"Validation error in backtest: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input parameters: {str(e)}"
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found during backtest: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Required file not found: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during backtest: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Backtest execution failed: {str(e)}"
        )


@router.get("/strategies")
async def get_available_strategies():
    """
    Get list of available portfolio allocation strategies.
    
    Returns:
        Dictionary of strategies with descriptions
    """
    logger.debug("Retrieving available strategies")
    
    strategies = {
        "model_weighted": {
            "name": "Model-Weighted Allocation",
            "description": "Weights based on predicted returns × confidence scores with 10% cap per asset",
            "best_for": "Trend-following and momentum strategies",
            "risk_level": "High"
        },
        "mean_variance": {
            "name": "Mean-Variance Optimization",
            "description": "Markowitz portfolio optimization minimizing variance for expected returns",
            "best_for": "Risk minimization and diversification",
            "risk_level": "Low to Medium"
        },
        "risk_parity": {
            "name": "Risk Parity",
            "description": "Equal risk contribution from each asset (inversely proportional to volatility)",
            "best_for": "Balanced diversification across assets",
            "risk_level": "Medium"
        }
    }
    
    return {
        "strategies": strategies,
        "default": "model_weighted"
    }


@router.post("/compare")
async def compare_strategies(
    symbols: List[str] = Query(..., description="List of stock symbols"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    strategies: Optional[List[str]] = Query(
        default=None,
        description="Strategies to compare (defaults to all)"
    ),
    rebalance_freq: int = Query(default=21, description="Rebalancing frequency")
):
    """
    Compare performance of multiple portfolio strategies side-by-side.
    
    Runs backtests for all specified strategies and returns comparative metrics.
    
    Args:
        symbols: Stock symbols to include
        start_date: Backtest start date
        end_date: Backtest end date
        strategies: List of strategies to compare (defaults to all)
        rebalance_freq: Rebalancing frequency
        
    Returns:
        Comparison of metrics across strategies
    """
    try:
        logger.info(f"Comparing strategies for symbols: {symbols}")
        
        # Default to all strategies if not specified or empty
        # Handle case where FastAPI might pass Query object
        if strategies is None or (isinstance(strategies, list) and len(strategies) == 0):
            strategies = ['mean_variance', 'risk_parity']  # Exclude model_weighted by default since it needs trained models
        
        results = {}
        
        for strategy in strategies:
            try:
                request = BacktestRequest(
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    strategy=strategy,
                    rebalance_freq=rebalance_freq
                )
                
                # Run backtest
                backtest_result = await run_backtest(request)
                
                # Extract key metrics
                results[strategy] = {
                    "annualized_return": backtest_result.metrics.annualized_return,
                    "volatility": backtest_result.metrics.annualized_volatility,
                    "sharpe_ratio": backtest_result.metrics.sharpe_ratio,
                    "max_drawdown": backtest_result.metrics.max_drawdown,
                    "win_rate": backtest_result.metrics.win_rate,
                    "final_value": backtest_result.metrics.final_value
                }
                
                logger.info(f"{strategy}: Sharpe={backtest_result.metrics.sharpe_ratio:.2f}")
                
            except HTTPException as e:
                logger.warning(f"HTTP error running {strategy}: {e.detail}")
                results[strategy] = {"error": e.detail}
            except Exception as e:
                logger.error(f"Error running {strategy}: {str(e)}")
                results[strategy] = {"error": str(e)}
        
        # Find best strategy by Sharpe ratio
        best_strategy = None
        best_sharpe = float('-inf')
        
        for strategy, metrics in results.items():
            if 'error' not in metrics:
                sharpe = metrics.get('sharpe_ratio', float('-inf'))
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_strategy = strategy
        
        return {
            "comparison": results,
            "best_strategy": best_strategy,
            "best_sharpe_ratio": best_sharpe,
            "configuration": {
                "symbols": symbols,
                "start_date": start_date,
                "end_date": end_date,
                "rebalance_freq": rebalance_freq
            }
        }
    
    except Exception as e:
        logger.error(f"Strategy comparison failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Strategy comparison failed: {str(e)}"
        )
