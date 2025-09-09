import asyncio
from app.services.data_service import DataService

async def test():
    service = DataService()
    result = await service.get_stock_data('RELIANCE.NS', period='2y')
    print(f'📊 Total data points: {len(result.get("data", []))}')
    print(f'🔗 Data source: {result.get("data_source", "unknown")}')
    print(f'✅ Success: {result.get("success", False)}')
    print(f'💰 Current price: ₹{result.get("current_price", 0):.2f}')
    
    # Check date range  
    if result.get('data'):
        first_date = result['data'][0].get('Date', 'unknown')
        last_date = result['data'][-1].get('Date', 'unknown')
        print(f'📅 Date range: {first_date} to {last_date}')

asyncio.run(test())
