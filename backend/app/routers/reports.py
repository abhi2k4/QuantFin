from fastapi import APIRouter, HTTPException
from typing import List, Dict
import pandas as pd
import numpy as np
from datetime import datetime
from app.services.news_service import NewsService
from app.services.data_service import DataService

router = APIRouter()
news_service = NewsService()
data_service = DataService()

@router.get("/news/{symbol}")
async def get_stock_news(symbol: str):
    """Get news analysis for a specific stock"""
    try:
        clean_symbol = symbol.replace('.NS', '')
        articles = await news_service.fetch_google_news(f"{clean_symbol} stock", max_items=20)
        
        analyzed_news = []
        for article in articles:
            text = f"{article['title']} {article['summary']}"
            sentiment = await news_service.analyze_sentiment(text)
            
            analyzed_news.append({
                **article,
                "sentiment_score": sentiment['combined_score'],
                "sentiment_label": sentiment['sentiment_label'],
                "sentiment_details": sentiment
            })
        
        return {"symbol": symbol, "news": analyzed_news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-sentiment")
async def get_market_sentiment(symbols: str = "RELIANCE.NS,TCS.NS,HDFCBANK.NS,INFY.NS,ICICIBANK.NS"):
    """Get overall market sentiment analysis"""
    try:
        symbol_list = symbols.split(",")
        result = await news_service.analyze_market_sentiment(symbol_list)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fundamental-analysis/{symbol}")
async def get_fundamental_analysis(symbol: str):
    """Get comprehensive fundamental analysis"""
    try:
        # Get financial ratios
        ratios = await data_service.get_financial_ratios(symbol)
        
        # Get historical data for trend analysis
        stock_data = await data_service.get_stock_data(symbol, period="1y")
        df = pd.DataFrame(stock_data["data"])
        
        # Calculate trends
        latest_price = df['Close'].iloc[-1]
        price_30d_ago = df['Close'].iloc[-30] if len(df) > 30 else df['Close'].iloc[0]
        price_90d_ago = df['Close'].iloc[-90] if len(df) > 90 else df['Close'].iloc[0]
        
        trend_30d = ((latest_price - price_30d_ago) / price_30d_ago) * 100
        trend_90d = ((latest_price - price_90d_ago) / price_90d_ago) * 100
        
        # Calculate volatility
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
        
        return {
            "symbol": symbol,
            "current_price": latest_price,
            "price_trends": {
                "30_day_change": round(trend_30d, 2),
                "90_day_change": round(trend_90d, 2)
            },
            "volatility": round(volatility, 2),
            "financial_ratios": ratios["ratios"],
            "analysis_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector-analysis")
async def get_sector_analysis():
    """Get sector-wise analysis of Nifty 50 stocks"""
    try:
        sector_data = {}
        
        # Sample sector mapping (simplified)
        sector_stocks = {
            "Technology": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
            "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
            "Energy": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
            "Consumer": ["ITC.NS", "HINDUNILVR.NS", "BRITANNIA.NS", "NESTLEIND.NS"],
            "Auto": ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"]
        }
        
        for sector, symbols in sector_stocks.items():
            sector_performance = []
            
            for symbol in symbols[:3]:  # Limit for demo
                try:
                    ratios = await data_service.get_financial_ratios(symbol)
                    sector_performance.append({
                        "symbol": symbol,
                        "pe_ratio": ratios["ratios"].get("pe_ratio"),
                        "current_price": ratios["ratios"].get("current_price"),
                        "market_cap": ratios["ratios"].get("market_cap")
                    })
                except:
                    continue
            
            if sector_performance:
                sector_data[sector] = sector_performance
        
        return {"sector_analysis": sector_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))