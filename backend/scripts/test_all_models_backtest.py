"""
Test backtest with all available models (LINEAR, SVM, LSTM, ARIMA)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.routers.backtest import BacktestRequest, run_backtest


async def test_model_backtest(strategy: str):
    """Test backtest with a specific model."""
    print("\n" + "=" * 80)
    print(f"TESTING {strategy} MODEL BACKTEST")
    print("=" * 80)
    
    request = BacktestRequest(
        strategy=strategy,
        start_date="2023-01-01",
        end_date="2024-12-31",
        capital=100000,
        top_n=10,
        rebalance_frequency="monthly"
    )
    
    try:
        result = await run_backtest(request)
        
        print(f"\n{strategy} RESULTS:")
        print(f"  Strategy CAGR: {result.strategy_cagr:.2f}%")
        print(f"  Strategy Sharpe: {result.strategy_sharpe:.2f}")
        print(f"  Strategy Max Drawdown: {result.strategy_max_drawdown:.2f}%")
        print(f"  Strategy Volatility: {result.strategy_volatility:.2f}%")
        print(f"  Strategy Win Rate: {result.strategy_win_rate:.2f}%")
        print(f"\n  Benchmark CAGR: {result.benchmark_cagr:.2f}%")
        print(f"  Benchmark Sharpe: {result.benchmark_sharpe:.2f}")
        print(f"\n  Outperformance: {result.strategy_cagr - result.benchmark_cagr:.2f}%")
        
        if result.strategy_cagr > result.benchmark_cagr:
            print(f"  [WIN] {strategy} OUTPERFORMS benchmark")
        else:
            print(f"  [LOSS] {strategy} underperforms benchmark")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {strategy} backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Test all models."""
    print("\n" + "=" * 80)
    print("TESTING ALL ML MODELS FOR BACKTESTING")
    print("=" * 80)
    
    models = ["LINEAR", "SVM", "LSTM", "ARIMA"]
    results = {}
    
    for model in models:
        success = await test_model_backtest(model)
        results[model] = success
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for model, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{model}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[SUCCESS] All models can be backtested!")
    else:
        print("\n[WARNING] Some models failed backtesting")


if __name__ == "__main__":
    asyncio.run(main())
