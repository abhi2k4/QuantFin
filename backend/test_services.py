"""
Simple test to check if services initialize correctly
"""

import sys
sys.path.insert(0, 'C:\\Users\\DELL\\Desktop\\AvanishCodes\\MajorProject\\QuantFin\\backend')

print("Testing service initialization...")

try:
    print("\n1. Testing RealDataService...")
    from app.services.real_data_service import get_real_data_service
    data_service = get_real_data_service()
    print(f"✅ RealDataService initialized - {len(data_service.symbols)} symbols found")
    
    print("\n2. Testing latest prices...")
    prices = data_service.get_latest_prices(['RELIANCE', 'TCS'])
    print(f"✅ Got prices: {prices}")
    
    print("\n3. Testing PortfolioManager...")
    from app.services.portfolio_manager import get_portfolio_manager
    pm = get_portfolio_manager()
    print("✅ PortfolioManager initialized")
    
    print("\n4. Testing portfolio summary...")
    summary = pm.get_portfolio_summary()
    print(f"✅ Portfolio summary generated")
    print(f"   Total value: ₹{summary['total_value']:,.2f}")
    print(f"   Positions: {summary['total_positions']}")
    
    print("\n✅ ALL TESTS PASSED!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
