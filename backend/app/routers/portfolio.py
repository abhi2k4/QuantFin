from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.models.schemas import PortfolioOptimization, Portfolio
from app.services.portfolio_service import PortfolioService
from app.services.data_service import DataService

router = APIRouter()
portfolio_service = PortfolioService()
data_service = DataService()

@router.post("/optimize")
async def optimize_portfolio(request: PortfolioOptimization):
    """Optimize portfolio allocation using ML predictions"""
    try:
        result = await portfolio_service.optimize_portfolio(
            symbols=request.symbols,
            investment_amount=request.investment_amount
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nifty50-optimization")
async def optimize_nifty50_portfolio(investment_amount: float = 100000):
    """Optimize portfolio using Nifty 50 stocks"""
    try:
        result = await portfolio_service.optimize_portfolio(
            symbols=data_service.nifty50_symbols[:20],  # Top 20 for demo
            investment_amount=investment_amount
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_portfolio_performance(symbols: str, quantities: str, cost_prices: str):
    """Get portfolio performance metrics"""
    try:
        symbol_list = symbols.split(",")
        quantity_list = [float(q) for q in quantities.split(",")]
        cost_price_list = [float(p) for p in cost_prices.split(",")]
        
        if len(symbol_list) != len(quantity_list) or len(symbol_list) != len(cost_price_list):
            raise HTTPException(status_code=400, detail="Mismatched array lengths")
        
        holdings = []
        for i, symbol in enumerate(symbol_list):
            holdings.append({
                "symbol": symbol,
                "quantity": quantity_list[i],
                "cost_price": cost_price_list[i]
            })
        
        result = await portfolio_service.get_portfolio_performance(holdings)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{symbols}")
async def get_portfolio_recommendations(symbols: str):
    """Get portfolio recommendations based on ML analysis"""
    try:
        symbol_list = symbols.split(",")
        recommendations = []
        
        for symbol in symbol_list:
            # Get fundamental data
            ratios = await data_service.get_financial_ratios(symbol)
            
            # Generate recommendation
            pe_ratio = ratios["ratios"].get("pe_ratio", 0) or 0
            roe = ratios["ratios"].get("roe", 0) or 0
            
            # Simple scoring model
            score = 50  # Base score
            
            if 15 <= pe_ratio <= 25:
                score += 10
            elif pe_ratio < 15:
                score += 20
            elif pe_ratio > 30:
                score -= 20
            
            if roe > 15:
                score += 20
            elif roe > 10:
                score += 10
            
            # Generate recommendation
            if score >= 70:
                recommendation = "Strong Buy"
            elif score >= 60:
                recommendation = "Buy"
            elif score >= 50:
                recommendation = "Hold"
            elif score >= 40:
                recommendation = "Weak Hold"
            else:
                recommendation = "Sell"
            
            recommendations.append({
                "symbol": symbol,
                "recommendation": recommendation,
                "score": score,
                "pe_ratio": pe_ratio,
                "roe": roe,
                "ratios": ratios["ratios"]
            })
        
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))