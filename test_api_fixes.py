"""
Simple test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test an API endpoint"""
    try:
        print(f"\n🧪 Testing {description}")
        print(f"   Endpoint: {endpoint}")
        
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success - Response keys: {list(data.keys())}")
            return True
        else:
            print(f"   ❌ Failed - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting QuantFin API Tests")
    print("=" * 50)
    
    tests = [
        ("/health", "Health Check"),
        ("/api/data/watchlist", "Watchlist (Previously 404)"),
        ("/api/data/market-overview", "Market Overview (Previously had JSON errors)"),
        ("/api/data/stock/RELIANCE.NS?period=5d", "Stock Data with Cleaned JSON"),
        ("/api/reports/market-sentiment", "Market Sentiment"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, description in tests:
        if test_endpoint(endpoint, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API fixes are working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above.")

if __name__ == "__main__":
    main()
