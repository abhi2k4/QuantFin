"""
Quick test of models endpoint with cached metrics
"""
import requests
import json
import time

print("Testing models endpoint...")
start = time.time()

try:
    response = requests.get('http://localhost:8000/api/analytics/models', timeout=5)
    elapsed = time.time() - start
    
    print(f"✅ Response received in {elapsed:.2f} seconds")
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"\nFound {len(data)} models:")
    for model in data:
        print(f"  - {model['model']}: {model['accuracy']:.2f}% accuracy")
        if 'status' in model:
            print(f"    Status: {model['status']}")
    
except requests.Timeout:
    print(f"❌ Timeout after {time.time() - start:.2f} seconds")
except Exception as e:
    print(f"❌ Error: {e}")
