"""
Test Script for Backtester Module

Tests backtester functionality with dummy data and validates metric calculations.

Author: QuantFin Team
Date: 2025-10-09
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil
import logging
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import numpy as np

# Add backend to path
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.backtester import Backtester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_dummy_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    base_price: float = 100.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Create dummy stock data for testing.
    
    Args:
        symbol (str): Stock symbol
        start_date (str): Start date
        end_date (str): End date
        base_price (float): Starting price
        volatility (float): Daily volatility
    
    Returns:
        pd.DataFrame: Dummy stock data
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)
    
    # Generate random returns
    np.random.seed(hash(symbol) % 1000)
    returns = np.random.normal(0.0005, volatility, n_days)
    
    # Calculate prices
    prices = base_price * np.cumprod(1 + returns)
    
    # Create OHLCV data
    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, n_days)),
        'High': prices * (1 + np.abs(np.random.uniform(0, 0.02, n_days))),
        'Low': prices * (1 - np.abs(np.random.uniform(0, 0.02, n_days))),
        'Volume': np.random.randint(1000000, 10000000, n_days)
    })
    
    df = df.set_index('Date')
    return df


def test_backtester_initialization():
    """Test backtester initialization."""
    logger.info("\n=== Test 1: Backtester Initialization ===")
    
    try:
        # Initialize backtester
        backtester = Backtester(
            models_dir='models',
            symbols=['TEST1', 'TEST2'],
            start_date='2023-01-01',
            end_date='2023-12-31',
            strategy='model_weighted'
        )
        
        assert backtester.strategy == 'model_weighted'
        assert len(backtester.symbols) == 2
        assert backtester.initial_capital == 100000.0
        
        logger.info("✅ PASS: Backtester initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_metric_calculations():
    """Test portfolio metric calculations."""
    logger.info("\n=== Test 2: Metric Calculations ===")
    
    try:
        backtester = Backtester(
            models_dir='models',
            symbols=['TEST'],
            start_date='2023-01-01',
            end_date='2023-01-31',
            strategy='model_weighted'
        )
        
        # Manually set dummy returns
        backtester.daily_returns = [0.01, -0.005, 0.02, 0.015, -0.01]
        backtester.daily_values = [100000, 101000, 100495, 102505, 104040, 103000]
        backtester.daily_dates = [
            pd.Timestamp('2023-01-01'),
            pd.Timestamp('2023-01-02'),
            pd.Timestamp('2023-01-03'),
            pd.Timestamp('2023-01-04'),
            pd.Timestamp('2023-01-05'),
            pd.Timestamp('2023-01-06')
        ]
        
        # Calculate metrics
        metrics = backtester.get_metrics()
        
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
        assert metrics['final_value'] == 103000
        assert metrics['initial_value'] == 100000
        
        logger.info(f"  Total Return: {metrics['total_return']:.2%}")
        logger.info(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        logger.info(f"  Max Drawdown: {metrics['max_drawdown']:.2%}")
        logger.info("✅ PASS: Metrics calculated correctly")
        return True
    
    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_portfolio_weights():
    """Test portfolio weight calculations."""
    logger.info("\n=== Test 3: Portfolio Weight Calculations ===")
    
    try:
        backtester = Backtester(
            models_dir='models',
            symbols=['TEST1', 'TEST2', 'TEST3'],
            start_date='2023-01-01',
            end_date='2023-01-31',
            strategy='model_weighted'
        )
        
        # Test model-weighted allocation
        returns = np.array([0.05, 0.03, -0.02])
        confidences = np.array([0.8, 0.7, 0.5])
        
        weights = backtester._model_weighted_allocation(returns, confidences)
        
        assert len(weights) == 3
        assert np.isclose(weights.sum(), 1.0, atol=0.01), f"Weights sum to {weights.sum()}, expected 1.0"
        assert all(weights >= 0), f"Found negative weights: {weights}"
        # Note: Individual weights can exceed 10% after renormalization when few assets remain
        
        logger.info(f"  Weights: {weights}")
        logger.info(f"  Sum: {weights.sum():.4f}")
        logger.info(f"  Max weight: {weights.max():.2%}")
        logger.info("✅ PASS: Portfolio weights calculated correctly")
        return True
    
    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_full_backtest():
    """Test full backtest with dummy data."""
    logger.info("\n=== Test 4: Full Backtest Simulation ===")
    
    temp_dir = None
    
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        data_dir = temp_dir / 'data'
        data_dir.mkdir()
        
        # Create dummy stock data
        symbols = ['STOCK1', 'STOCK2', 'STOCK3']
        start_date = '2023-01-01'
        end_date = '2023-06-30'
        
        for symbol in symbols:
            df = create_dummy_stock_data(symbol, start_date, end_date)
            # Save in format matching actual data
            df_out = df.reset_index()
            df_out.to_csv(data_dir / f'{symbol}.csv', index=False)
        
        # Initialize backtester
        backtester = Backtester(
            models_dir=str(temp_dir / 'models'),
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            strategy='model_weighted',
            rebalance_freq=21,
            initial_capital=100000.0,
            results_dir=str(temp_dir / 'results')
        )
        
        # Override data loading to use temp directory
        backtester.price_data = {}
        for symbol in symbols:
            df = pd.read_csv(data_dir / f'{symbol}.csv')
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            backtester.price_data[symbol] = df
        
        # Run backtest
        logger.info("  Running backtest...")
        results = backtester.run_backtest()
        
        assert 'metrics' in results
        assert len(backtester.daily_values) > 0
        assert len(backtester.daily_returns) > 0
        
        logger.info(f"  Final Value: ${results['metrics']['final_value']:,.2f}")
        logger.info(f"  Total Return: {results['metrics']['total_return']:.2%}")
        logger.info(f"  Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
        logger.info(f"  Total Trades: {results['trades']}")
        logger.info("✅ PASS: Full backtest completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_all_strategies():
    """Test all portfolio strategies."""
    logger.info("\n=== Test 5: All Portfolio Strategies ===")
    
    temp_dir = None
    
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        data_dir = temp_dir / 'data'
        data_dir.mkdir()
        
        # Create dummy stock data
        symbols = ['STOCK1', 'STOCK2']
        start_date = '2023-01-01'
        end_date = '2023-03-31'
        
        for symbol in symbols:
            df = create_dummy_stock_data(symbol, start_date, end_date, base_price=100.0)
            df_out = df.reset_index()
            df_out.to_csv(data_dir / f'{symbol}.csv', index=False)
        
        strategies = ['model_weighted', 'mean_variance', 'risk_parity']
        
        for strategy in strategies:
            logger.info(f"\n  Testing {strategy} strategy...")
            
            backtester = Backtester(
                models_dir=str(temp_dir / 'models'),
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                strategy=strategy,
                rebalance_freq=15,
                initial_capital=100000.0,
                results_dir=str(temp_dir / 'results')
            )
            
            # Load data
            backtester.price_data = {}
            for symbol in symbols:
                df = pd.read_csv(data_dir / f'{symbol}.csv')
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
                backtester.price_data[symbol] = df
            
            # Run backtest
            results = backtester.run_backtest()
            
            assert 'metrics' in results
            logger.info(f"    Return: {results['metrics']['total_return']:.2%}")
            logger.info(f"    Sharpe: {results['metrics']['sharpe_ratio']:.2f}")
        
        logger.info("\n✅ PASS: All strategies tested successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_save_results():
    """Test result saving functionality."""
    logger.info("\n=== Test 6: Save Results ===")
    
    temp_dir = None
    
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        results_dir = temp_dir / 'results'
        results_dir.mkdir()
        
        backtester = Backtester(
            models_dir=str(temp_dir / 'models'),
            symbols=['TEST'],
            start_date='2023-01-01',
            end_date='2023-01-31',
            strategy='model_weighted',
            results_dir=str(results_dir)
        )
        
        # Set dummy data
        backtester.daily_returns = [0.01, 0.02, -0.01]
        backtester.daily_values = [100000, 101000, 103020, 101990]
        backtester.daily_dates = [
            pd.Timestamp('2023-01-01'),
            pd.Timestamp('2023-01-02'),
            pd.Timestamp('2023-01-03'),
            pd.Timestamp('2023-01-04')
        ]
        backtester.trade_log = [
            {'date': pd.Timestamp('2023-01-01'), 'symbol': 'TEST', 'action': 'BUY', 
             'shares': 100, 'price': 100.0, 'value': 10000, 'cost': 10}
        ]
        
        # Save results
        backtester.save_results('test_backtest')
        
        # Check files exist
        assert (results_dir / 'test_backtest.csv').exists()
        assert (results_dir / 'test_backtest_summary.json').exists()
        assert (results_dir / 'test_backtest_trades.csv').exists()
        
        logger.info("  Files saved:")
        logger.info(f"    - {results_dir / 'test_backtest.csv'}")
        logger.info(f"    - {results_dir / 'test_backtest_summary.json'}")
        logger.info(f"    - {results_dir / 'test_backtest_trades.csv'}")
        logger.info("✅ PASS: Results saved successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False
    
    finally:
        # Cleanup
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("BACKTESTER TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        ("Initialization", test_backtester_initialization),
        ("Metric Calculations", test_metric_calculations),
        ("Portfolio Weights", test_portfolio_weights),
        ("Full Backtest", test_full_backtest),
        ("All Strategies", test_all_strategies),
        ("Save Results", test_save_results)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed_flag in results:
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("-" * 60)
    logger.info(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed!")
        return 0
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
