import asyncio
import sys
sys.path.append('.')
from app.services.portfolio_service import PortfolioService

async def test_portfolio():
    service = PortfolioService()
    print('🧪 Testing portfolio backtest with notebook API...')
    
    result = await service.backtest_strategy(
        symbol='RELIANCE.NS', 
        strategy='XGBoost',
        start_date='2024-08-01', 
        end_date='2024-09-01'
    )
    
    print('📊 Backtest Results:')
    print(f'   • Final Value: ₹{result.get("final_value", 0):,.2f}')
    print(f'   • Total Return: {result.get("total_return_percent", 0):.2f}%')
    print(f'   • Sharpe Ratio: {result.get("sharpe_ratio", 0):.3f}')
    print(f'   • Success: {result.get("success", False)}')

asyncio.run(test_portfolio())
