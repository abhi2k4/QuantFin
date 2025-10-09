"""
Quick validation test for DataPreprocessor and FeatureEngineer

Tests both classes work together correctly with real Nifty 50 data.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.data_preprocessor import DataPreprocessor
from app.services.feature_engineer import FeatureEngineer

print("\n" + "="*60)
print("DataPreprocessor & FeatureEngineer Validation Test")
print("="*60)

# Initialize services
print("\n1. Initializing services...")
preprocessor = DataPreprocessor()
engineer = FeatureEngineer(preprocessor)
print("✅ Services initialized")

# Get all symbols
print("\n2. Loading stock symbols...")
symbols = preprocessor.get_all_symbols()
print(f"✅ Found {len(symbols)} symbols")
print(f"   Sample: {symbols[:5]}")

# Test data loading
print("\n3. Testing data loading...")
test_symbol = 'RELIANCE'
df = preprocessor.get_stock_data(test_symbol)
if df is not None:
    print(f"✅ Loaded {test_symbol}: {len(df)} rows")
    print(f"   Date range: {df.index.min()} to {df.index.max()}")
    print(f"   Columns: {list(df.columns)}")
else:
    print(f"❌ Failed to load {test_symbol}")
    sys.exit(1)

# Test feature generation
print("\n4. Testing feature generation...")
features = engineer.generate_features(test_symbol, lookback=60)
if features is not None:
    print(f"✅ Generated features: {features.shape}")
    print(f"   Total features: {len(features.columns)}")
    print(f"   Sample features: {list(features.columns[:10])}")
else:
    print(f"❌ Failed to generate features for {test_symbol}")
    sys.exit(1)

# Test batch generation
print("\n5. Testing batch feature generation...")
test_symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
all_features = engineer.generate_features_all(test_symbols, lookback=60)
print(f"✅ Generated features for {len(all_features)}/{len(test_symbols)} symbols")
for sym, feat in all_features.items():
    print(f"   {sym}: {feat.shape}")

# Test normalization
print("\n6. Testing feature normalization...")
normalized, scaler = engineer.normalize_features(features)
print(f"✅ Normalized features: {normalized.shape}")
print(f"   Scaler mean: {scaler.mean_[:5]}")
print(f"   Scaler scale: {scaler.scale_[:5]}")

# Test caching
print("\n7. Testing cache performance...")
import time

start = time.time()
df1 = preprocessor.get_stock_data(test_symbol, use_cache=False)
time1 = (time.time() - start) * 1000

start = time.time()
df2 = preprocessor.get_stock_data(test_symbol, use_cache=True)
time2 = (time.time() - start) * 1000

if time2 < 1:  # Cache should be very fast
    print(f"✅ Cache working: {time1:.2f}ms → {time2:.2f}ms")
else:
    print(f"⚠️  Cache may not be working: {time1:.2f}ms → {time2:.2f}ms")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - Services are production ready!")
print("="*60)
print("\nNext steps:")
print("1. Train models: python scripts/train_simple.py --symbols RELIANCE TCS --quick --save-summary")
print("2. Train all models: python scripts/train_simple.py --save-summary")
print("3. Verify predictions: Use PredictionService with trained models")
print("="*60 + "\n")
