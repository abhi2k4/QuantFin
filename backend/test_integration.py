#!/usr/bin/env python3
"""Test the integrated notebook API with comprehensive logging"""

import asyncio
import sys
sys.path.append('.')
from app.services.portfolio_service import PortfolioService
from app.services.data_service import DataService

async def test_data_service():
    """Test the DataService with notebook API"""
    print("🧪 Testing DataService with notebook API integration...")
    
    service = DataService()
    
    # Test multiple stocks
    test_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        try:
            result = await service.get_stock_data(symbol, period="1mo")
            
            print(f"   ✅ Success: {result.get('success', False)}")
            print(f"   📈 Data Points: {len(result.get('data', []))}")
            print(f"   🔗 Data Source: {result.get('data_source', 'unknown')}")
            print(f"   💰 Current Price: ₹{result.get('current_price', 0):.2f}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def test_portfolio_service():
    """Test the PortfolioService with integrated data"""
    print("\n🧪 Testing PortfolioService with notebook API...")
    
    service = PortfolioService()
    
    try:
        result = await service.backtest_strategy(
            symbol='RELIANCE.NS', 
            strategy='xgboost_enhanced',
            start_date='2024-08-01', 
            end_date='2024-09-01'
        )
        
        print(f"📊 Backtest Results:")
        print(f"   💰 Final Value: ₹{result.get('final_value', 0):,.2f}")
        print(f"   📈 Total Return: {result.get('total_return_percent', 0):.2f}%")
        print(f"   📊 Sharpe Ratio: {result.get('sharpe_ratio', 0):.3f}")
        print(f"   🔗 Data Source: {result.get('data_source', 'unknown')}")
        print(f"   ✅ Success: {result.get('success', False)}")
        
    except Exception as e:
        print(f"   ❌ Portfolio test error: {str(e)}")

async def main():
    """Run all integration tests"""
    print("🚀 Starting comprehensive integration tests...\n")
    
    await test_data_service()
    await test_portfolio_service()
    
    print("\n🏁 Integration tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
