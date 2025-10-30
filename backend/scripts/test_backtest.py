"""
Test script for backtest endpoint.

This script tests the walk-forward backtesting functionality.

Usage:
    python scripts/test_backtest.py
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import json
from datetime import datetime
from app.routers.backtest import run_backtest, BacktestRequest

async def test_backtest():
    """Test backtest endpoint"""
    
    print("=" * 60)
    print("TESTING BACKTEST ENDPOINT")
    print("=" * 60)
    print()
    
    # Create test request
    request = BacktestRequest(
        strategy="LINEAR",
        start_date="2023-01-01",
        end_date="2024-12-31",
        capital=100000,
        top_n=10,
        rebalance_frequency="monthly"
    )
    
    print(f"Request:")
    print(f"  Strategy: {request.strategy}")
    print(f"  Period: {request.start_date} to {request.end_date}")
    print(f"  Capital: Rs.{request.capital:,.0f}")
    print(f"  Top N: {request.top_n}")
    print(f"  Frequency: {request.rebalance_frequency}")
    print()
    
    print("Running backtest...")
    print()
    
    try:
        result = await run_backtest(request)
        
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print()
        
        print(f"Initial Capital: Rs.{result.initial_capital:,.2f}")
        print(f"Final Value: Rs.{result.final_value:,.2f}")
        print(f"Total Return: {((result.final_value / result.initial_capital) - 1) * 100:.2f}%")
        print()
        
        print("STRATEGY METRICS:")
        print(f"  CAGR: {result.strategy_cagr:.2f}%")
        print(f"  Sharpe Ratio: {result.strategy_sharpe:.2f}")
        print(f"  Sortino Ratio: {result.strategy_sortino:.2f}")
        print(f"  Max Drawdown: {result.strategy_max_drawdown:.2f}%")
        print(f"  Volatility: {result.strategy_volatility:.2f}%")
        print(f"  Calmar Ratio: {result.strategy_calmar:.2f}")
        print(f"  Win Rate: {result.strategy_win_rate:.2f}%")
        print()
        
        print("BENCHMARK METRICS (Equal-Weighted Nifty50):")
        print(f"  CAGR: {result.benchmark_cagr:.2f}%")
        print(f"  Sharpe Ratio: {result.benchmark_sharpe:.2f}")
        print(f"  Sortino Ratio: {result.benchmark_sortino:.2f}")
        print(f"  Max Drawdown: {result.benchmark_max_drawdown:.2f}%")
        print(f"  Volatility: {result.benchmark_volatility:.2f}%")
        print(f"  Calmar Ratio: {result.benchmark_calmar:.2f}")
        print(f"  Win Rate: {result.benchmark_win_rate:.2f}%")
        print()
        
        print(f"Number of Rebalances: {result.num_rebalances}")
        print(f"Total Periods: {result.total_periods}")
        print()
        
        print("=" * 60)
        print("COMPARISON")
        print("=" * 60)
        
        cagr_diff = result.strategy_cagr - result.benchmark_cagr
        sharpe_diff = result.strategy_sharpe - result.benchmark_sharpe
        
        print(f"CAGR Difference: {cagr_diff:+.2f}% " + ("[WIN]" if cagr_diff > 0 else "[LOSS]"))
        print(f"Sharpe Difference: {sharpe_diff:+.2f} " + ("[WIN]" if sharpe_diff > 0 else "[LOSS]"))
        print()
        
        if result.strategy_cagr > result.benchmark_cagr:
            print("[WIN] Strategy OUTPERFORMS benchmark")
        else:
            print("[LOSS] Strategy UNDERPERFORMS benchmark")
        print()
        
        # Sample time series data
        print("=" * 60)
        print("SAMPLE TIME SERIES (First 5 periods)")
        print("=" * 60)
        print()
        print(f"{'Date':<15} {'Portfolio':<15} {'Benchmark':<15} {'Ret %':<10}")
        print("-" * 60)
        
        for i in range(min(5, len(result.dates))):
            print(f"{result.dates[i]:<15} "
                  f"Rs.{result.portfolio_values[i]:<13,.0f} "
                  f"Rs.{result.benchmark_values[i]:<13,.0f} "
                  f"{result.monthly_returns[i] if i < len(result.monthly_returns) else 0:.2f}%")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Backtest completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_backtest())
