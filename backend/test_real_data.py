"""
Test script to verify all real data endpoints are working.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, url):
    """Test an API endpoint and print results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ SUCCESS - Status: {response.status_code}")
        print(f"\nResponse preview:")
        print(json.dumps(data, indent=2)[:500] + "...")
        return True
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False

def main():
    """Run all endpoint tests."""
    print("\n" + "="*60)
    print("QUANTFIN REAL DATA ENDPOINT TESTS")
    print("="*60)
    
    tests = [
        ("Portfolio Summary", f"{BASE_URL}/api/portfolio/summary"),
        ("Portfolio Performance (3M)", f"{BASE_URL}/api/portfolio/performance?timeframe=3M"),
        ("Analytics KPIs", f"{BASE_URL}/api/analytics/kpis"),
        ("Candlestick Data (RELIANCE)", f"{BASE_URL}/api/analytics/candlestick/RELIANCE?days=30"),
        ("ML Models Training", f"{BASE_URL}/api/analytics/models"),  # This will train models!
    ]
    
    results = []
    for name, url in tests:
        success = test_endpoint(name, url)
        results.append((name, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
