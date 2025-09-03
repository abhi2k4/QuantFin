from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.services.data_service import DataService
import pandas as pd

router = APIRouter()
data_service = DataService()

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str, period: str = "1y", interval: str = "1d"):
    """Get historical stock data"""
    try:
        result = await data_service.get_stock_data(symbol, period, interval)
        
        # Add technical indicators
        df = pd.DataFrame(result["data"])
        if not df.empty:
            df_with_indicators = data_service.calculate_technical_indicators(df)
            result["data"] = df_with_indicators.to_dict('records')
        
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock data error: {str(e)}")

@router.get("/nifty50")
async def get_nifty50_data(period: str = "1y"):
    """Get Nifty 50 constituent data"""
    try:
        # Get data for top 10 stocks for demo
        top_symbols = data_service.nifty50_symbols[:10]
        result = await data_service.get_multiple_stocks(top_symbols, period)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-ratios/{symbol}")
async def get_financial_ratios(symbol: str):
    """Get financial ratios for a stock"""
    try:
        result = await data_service.get_financial_ratios(symbol)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial ratios error: {str(e)}")

@router.get("/ratios/{symbol}")
async def get_ratios_alias(symbol: str):
    """Alias for financial ratios endpoint"""
    return await get_financial_ratios(symbol)

@router.get("/comparison")
async def compare_stocks(symbols: str):
    """Compare multiple stocks"""
    try:
        symbol_list = symbols.split(",")
        comparison_data = []
        
        for symbol in symbol_list:
            ratios = await data_service.get_financial_ratios(symbol)
            stock_data = await data_service.get_stock_data(symbol, period="3mo")
            
            df = pd.DataFrame(stock_data["data"])
            if not df.empty:
                latest_price = df['Close'].iloc[-1]
                price_change_30d = ((latest_price - df['Close'].iloc[-30]) / df['Close'].iloc[-30]) * 100 if len(df) > 30 else 0
                
                comparison_data.append({
                    "symbol": symbol,
                    "current_price": latest_price,
                    "price_change_30d": round(price_change_30d, 2),
                    "pe_ratio": ratios["ratios"].get("pe_ratio"),
                    "market_cap": ratios["ratios"].get("market_cap"),
                    "dividend_yield": ratios["ratios"].get("dividend_yield")
                })
        
        return {"comparison": comparison_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-overview")
async def get_market_overview():
    """Get market overview with key indices"""
    try:
        indices = ["^NSEI", "^BSESN"]  # Nifty 50, BSE Sensex
        overview = {}
        
        for index in indices:
            try:
                data = await data_service.get_stock_data(index, period="5d", interval="1d")
                df = pd.DataFrame(data["data"])
                
                if not df.empty:
                    latest = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else latest
                    
                    change = latest['Close'] - prev['Close']
                    change_percent = (change / prev['Close']) * 100
                    
                    overview[index] = {
                        "value": round(latest['Close'], 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "high": round(latest['High'], 2),
                        "low": round(latest['Low'], 2),
                        "volume": latest['Volume']
                    }
            except:
                continue
        
        return {"market_overview": overview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))