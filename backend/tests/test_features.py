"""
Demo script to test feature engineering functionality.

This script demonstrates how to use the FeatureEngineer to compute
technical indicators and features for stocks and sectors.

Usage:
    python test_features.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.features import compute_features, get_feature_summary, get_stock_features


def main():
    """Main function to test feature engineering."""
    
    print("=" * 70)
    print("  QuantFin Feature Engineering Demo")
    print("=" * 70)
    print()
    
    # Compute all features
    print("Computing features for all stocks and sectors...")
    print("(This may take a few moments...)")
    print()
    
    features = compute_features()
    
    # Get summary
    summary = get_feature_summary()
    
    print("\n" + "=" * 70)
    print("  Feature Engineering Summary")
    print("=" * 70)
    print(f"✓ Stocks processed: {summary['num_stocks']}")
    print(f"✓ Sectors processed: {summary['num_sectors']}")
    print(f"✓ Features per asset: {summary.get('num_features', 'N/A')}")
    print(f"✓ Date range: {summary.get('date_range', {}).get('start')} to {summary.get('date_range', {}).get('end')}")
    print()
    
    # Show feature names
    print("=" * 70)
    print("  Computed Features")
    print("=" * 70)
    if 'feature_names' in summary:
        for i, feature in enumerate(summary['feature_names'], 1):
            print(f"{i:2d}. {feature}")
    print()
    
    # Show sample data for one stock
    print("=" * 70)
    print("  Sample: TCS Stock Features (Last 5 rows)")
    print("=" * 70)
    
    tcs_features = get_stock_features('TCS')
    if tcs_features is not None:
        # Select key columns for display
        display_cols = [
            'Date', 'Close', 'SMA_10', 'SMA_50', 'SMA_200', 
            'RSI_14', 'MACD', 'vol_21', 'returns'
        ]
        available_cols = [col for col in display_cols if col in tcs_features.columns]
        
        print(tcs_features[available_cols].tail().to_string(index=False))
    else:
        print("TCS features not available")
    
    print("\n" + "=" * 70)
    print("  Feature Engineering Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
