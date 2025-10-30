#!/usr/bin/env python3
"""Test the intelligent portfolio rebalance endpoint"""
import requests
import json

# Test rebalance with LSTM strategy
response = requests.post(
    'http://localhost:8000/api/portfolio/rebalance',
    json={
        'strategy': 'LSTM',
        'capital_allocation': 100000
    }
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    
    print(f"\n✅ SUCCESS!")
    print(f"Total Allocations: {len(result.get('allocations', []))}")
    print(f"Expected Return: {result.get('expected_return', 'N/A')}%")
    print(f"Expected Risk: {result.get('expected_risk', 'N/A')}%")
    print(f"Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
    
    print(f"\nTop 10 Stock Allocations:")
    print(f"{'Stock':<12} {'Weight':<8} {'Amount':<12} {'Qty':<6} {'Buy':<10} {'Predicted':<10} {'Return':<8}")
    print("=" * 85)
    
    for alloc in result.get('allocations', [])[:10]:
        print(f"{alloc['symbol']:<12} {alloc['weight_percent']:>6.2f}% "
              f"₹{alloc['allocation_amount']:>10,.2f} {alloc['quantity']:>5} "
              f"₹{alloc['buy_price']:>8,.2f} ₹{alloc['predicted_price']:>8,.2f} "
              f"{alloc['predicted_return']:>6.2f}%")
    
    print(f"\nTotal Capital Allocated: ₹{sum(a['allocation_amount'] for a in result.get('allocations', [])):,.2f}")
else:
    print(f"\n❌ ERROR: {response.text[:500]}")
