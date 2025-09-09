import asyncio
import requests
import json

def test_portfolio():
    print('🧪 Testing Portfolio API...')
    try:
        response = requests.get('http://localhost:8000/api/portfolio/nifty50-optimization?investment_amount=100000')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Portfolio API response structure:')
            print(f'   • Investment Amount: ₹{data.get("investment_amount", 0):,}')
            print(f'   • Total Allocated: ₹{data.get("total_allocated", 0):,}')
            print(f'   • Predicted Value (1Y): ₹{data.get("predicted_value_1y", 0):,}')
            print(f'   • Expected Return (1Y): {data.get("expected_return_1y", 0):.2f}%')
            print(f'   • Holdings Count: {len(data.get("holdings", []))}')
            
            if data.get('holdings'):
                print('   • Sample holding:')
                holding = data['holdings'][0]
                print(f'     - Symbol: {holding.get("index", "unknown")}')
                print(f'     - Weight: {(holding.get("weight", 0) * 100):.2f}%')
                print(f'     - Allocation: ₹{holding.get("allocation", 0):,.0f}')
                print(f'     - Current Price: ₹{holding.get("current_price", 0):.2f}')
                print(f'     - Predicted Price: ₹{holding.get("predicted_price", 0):.2f}')
                print(f'     - Expected Return: {(holding.get("expected_return", 0) * 100):.2f}%')
        else:
            print(f'❌ Error: {response.text}')
    except Exception as e:
        print(f'❌ Test failed: {e}')

if __name__ == "__main__":
    test_portfolio()
