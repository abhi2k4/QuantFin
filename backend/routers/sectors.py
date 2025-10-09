"""
Sectors Router for ETF Portfolio System

This module defines FastAPI endpoints for accessing sector and stock data.
It provides RESTful APIs for retrieving market data, sector information,
and stock-level details.

Author: QuantFin Team
Date: 2025-10-09
"""

from typing import List, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd

from ..services.preprocessing import (
    get_preprocessor,
    get_sector_data,
    get_stock_data,
    get_available_sectors,
    get_available_tickers
)

# Initialize router
router = APIRouter(
    prefix="/sectors",
    tags=["sectors"],
    responses={404: {"description": "Not found"}},
)


def dataframe_to_dict(df: pd.DataFrame) -> List[Dict]:
    """
    Convert DataFrame to list of dictionaries for JSON serialization.
    
    Args:
        df (pd.DataFrame): DataFrame to convert
    
    Returns:
        List[Dict]: List of records as dictionaries
    """
    # Convert datetime objects to ISO format strings
    df_copy = df.copy()
    
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
    
    return df_copy.to_dict(orient='records')


@router.get("/", response_model=Dict[str, List[str]])
async def list_sectors():
    """
    Get a list of all available sectors.
    
    Returns:
        Dict containing:
        - sectors: List of sector names
        - count: Number of sectors
    """
    try:
        sectors = get_available_sectors()
        
        return {
            "sectors": sectors,
            "count": len(sectors)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sectors: {str(e)}"
        )


@router.get("/{sector_name}/data")
async def get_sector_timeseries(
    sector_name: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, description="Limit number of records")
):
    """
    Get time series data for a specific sector.
    
    Args:
        sector_name (str): Name of the sector (e.g., 'Banking', 'IT')
        start_date (str, optional): Filter data from this date
        end_date (str, optional): Filter data until this date
        limit (int, optional): Limit number of records returned
    
    Returns:
        Dict containing:
        - sector: Sector name
        - data: List of OHLCV records
        - count: Number of records
        - date_range: Min and max dates in the data
    """
    try:
        # Get sector data
        df = get_sector_data(sector_name)
        
        if df is None:
            available_sectors = get_available_sectors()
            raise HTTPException(
                status_code=404,
                detail=f"Sector '{sector_name}' not found. Available sectors: {available_sectors}"
            )
        
        # Apply date filters if provided
        if start_date:
            try:
                start = pd.to_datetime(start_date)
                df = df[df['Date'] >= start]
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid start_date format. Use YYYY-MM-DD. Error: {str(e)}"
                )
        
        if end_date:
            try:
                end = pd.to_datetime(end_date)
                df = df[df['Date'] <= end]
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid end_date format. Use YYYY-MM-DD. Error: {str(e)}"
                )
        
        # Apply limit if provided
        if limit and limit > 0:
            df = df.tail(limit)
        
        # Get date range
        date_range = {
            "start": df['Date'].min().strftime('%Y-%m-%d'),
            "end": df['Date'].max().strftime('%Y-%m-%d')
        }
        
        # Convert to JSON-serializable format
        data = dataframe_to_dict(df)
        
        return {
            "sector": sector_name,
            "data": data,
            "count": len(data),
            "date_range": date_range
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sector data: {str(e)}"
        )


@router.get("/{sector_name}/summary")
async def get_sector_summary(sector_name: str):
    """
    Get summary statistics for a specific sector.
    
    Args:
        sector_name (str): Name of the sector
    
    Returns:
        Dict containing:
        - sector: Sector name
        - summary: Statistical summary of the data
        - latest_price: Most recent closing price
        - date_range: Data availability range
    """
    try:
        # Get sector data
        df = get_sector_data(sector_name)
        
        if df is None:
            available_sectors = get_available_sectors()
            raise HTTPException(
                status_code=404,
                detail=f"Sector '{sector_name}' not found. Available sectors: {available_sectors}"
            )
        
        # Calculate summary statistics
        summary = {
            "mean_close": float(df['Close'].mean()),
            "median_close": float(df['Close'].median()),
            "std_close": float(df['Close'].std()),
            "min_close": float(df['Close'].min()),
            "max_close": float(df['Close'].max()),
            "mean_volume": float(df['Volume'].mean()),
            "total_trading_days": len(df)
        }
        
        # Get latest price
        latest = df.iloc[-1]
        latest_price = {
            "date": latest['Date'].strftime('%Y-%m-%d'),
            "open": float(latest['Open']),
            "high": float(latest['High']),
            "low": float(latest['Low']),
            "close": float(latest['Close']),
            "volume": float(latest['Volume'])
        }
        
        # Get date range
        date_range = {
            "start": df['Date'].min().strftime('%Y-%m-%d'),
            "end": df['Date'].max().strftime('%Y-%m-%d')
        }
        
        return {
            "sector": sector_name,
            "summary": summary,
            "latest_price": latest_price,
            "date_range": date_range
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sector summary: {str(e)}"
        )


@router.get("/stocks/list")
async def list_stocks():
    """
    Get a list of all available stock tickers.
    
    Returns:
        Dict containing:
        - tickers: List of stock ticker symbols
        - count: Number of tickers
    """
    try:
        tickers = get_available_tickers()
        
        return {
            "tickers": sorted(tickers),
            "count": len(tickers)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stock list: {str(e)}"
        )


@router.get("/stocks/{ticker}/data")
async def get_stock_timeseries(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, description="Limit number of records")
):
    """
    Get time series data for a specific stock.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'TCS', 'RELIANCE')
        start_date (str, optional): Filter data from this date
        end_date (str, optional): Filter data until this date
        limit (int, optional): Limit number of records returned
    
    Returns:
        Dict containing:
        - ticker: Stock ticker symbol
        - data: List of OHLCV records
        - count: Number of records
        - date_range: Min and max dates in the data
    """
    try:
        # Get stock data
        df = get_stock_data(ticker)
        
        if df is None:
            raise HTTPException(
                status_code=404,
                detail=f"Stock ticker '{ticker}' not found"
            )
        
        # Apply date filters if provided
        if start_date:
            try:
                start = pd.to_datetime(start_date)
                df = df[df['Date'] >= start]
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid start_date format. Use YYYY-MM-DD. Error: {str(e)}"
                )
        
        if end_date:
            try:
                end = pd.to_datetime(end_date)
                df = df[df['Date'] <= end]
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid end_date format. Use YYYY-MM-DD. Error: {str(e)}"
                )
        
        # Apply limit if provided
        if limit and limit > 0:
            df = df.tail(limit)
        
        # Get date range
        date_range = {
            "start": df['Date'].min().strftime('%Y-%m-%d'),
            "end": df['Date'].max().strftime('%Y-%m-%d')
        }
        
        # Convert to JSON-serializable format
        data = dataframe_to_dict(df)
        
        return {
            "ticker": ticker,
            "data": data,
            "count": len(data),
            "date_range": date_range
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stock data: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify data preprocessing service.
    
    Returns:
        Dict containing service status and data statistics
    """
    try:
        preprocessor = get_preprocessor()
        
        # Get statistics
        sectors = preprocessor.get_available_sectors()
        tickers = preprocessor.get_available_tickers()
        date_range = preprocessor.get_date_range()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_sectors": len(sectors),
                "total_stocks": len(tickers),
                "date_range": {
                    "start": date_range[0].strftime('%Y-%m-%d') if date_range else None,
                    "end": date_range[1].strftime('%Y-%m-%d') if date_range else None
                }
            }
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )
