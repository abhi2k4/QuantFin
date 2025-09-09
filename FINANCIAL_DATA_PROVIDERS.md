# Alternative Financial Data Providers Setup Guide

## 🚀 **Quick Setup Instructions**

### 1. **Alpha Vantage** (Best for Indian Markets)
- **Sign up**: https://www.alphavantage.co/support/#api-key
- **Free tier**: 25 requests/day, 5 requests/minute
- **Indian stocks**: Supports BSE, NSE
- **Set environment variable**: `ALPHA_VANTAGE_API_KEY=your_key_here`

```bash
# Windows PowerShell
$env:ALPHA_VANTAGE_API_KEY="your_api_key_here"

# Linux/Mac
export ALPHA_VANTAGE_API_KEY="your_api_key_here"
```

### 2. **Twelve Data** (Most Generous Free Tier)
- **Sign up**: https://twelvedata.com/pricing
- **Free tier**: 800 requests/day, 8 requests/minute
- **Best for**: High-volume applications
- **Set environment variable**: `TWELVE_DATA_API_KEY=your_key_here`

### 3. **Financial Modeling Prep**
- **Sign up**: https://financialmodelingprep.com/developer/docs
- **Free tier**: 250 requests/day
- **Good for**: Financial ratios and company data
- **Set environment variable**: `FMP_API_KEY=your_key_here`

## 🔧 **Integration with Your Current Code**

To use the new multi-provider service, update your `data_service.py`:

```python
# In backend/app/services/data_service.py
from app.services.multi_provider_service import MultiProviderDataService

class DataService:
    def __init__(self):
        # ... existing code ...
        self.multi_provider = MultiProviderDataService()
    
    async def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict:
        """Fetch stock data with multi-provider fallback"""
        try:
            # First try the new multi-provider service
            result = await self.multi_provider.get_stock_data_with_fallback(symbol, period)
            
            if result and result.get('data'):
                # Add technical indicators
                df = pd.DataFrame(result["data"])
                if not df.empty:
                    df_with_indicators = self.calculate_technical_indicators(df)
                    result["data"] = clean_data_for_json(df_with_indicators.to_dict('records'))
                
                return clean_data_for_json(result)
            
        except Exception as e:
            print(f"Multi-provider failed for {symbol}: {str(e)}")
        
        # Fallback to existing Yahoo Finance + mock data
        return await self.get_stock_data_yahoo_fallback(symbol, period, interval)
```

## 🏆 **Recommended Provider Priority**

1. **Twelve Data** - Best free tier (800 requests/day)
2. **Alpha Vantage** - Best for Indian markets
3. **Financial Modeling Prep** - Good for company fundamentals
4. **Yahoo Finance** - Backup (current implementation)
5. **Mock Data** - Final fallback

## 💡 **Pro Tips**

### **For Production Use:**
- Set up multiple API keys for redundancy
- Implement caching to reduce API calls
- Monitor daily usage limits
- Consider paid plans for higher limits

### **For Development:**
- Use demo keys initially
- Implement rate limiting on your end
- Cache responses for repeated requests
- Add retry logic with exponential backoff

### **Cost Comparison:**
- **Twelve Data Pro**: $30/month (100k requests/day)
- **Alpha Vantage Premium**: $50/month (unlimited requests)
- **FMP Professional**: $20/month (unlimited requests)

## 🛠 **Quick Test Script**

```python
# test_providers.py
import asyncio
from app.services.multi_provider_service import MultiProviderDataService

async def test_providers():
    service = MultiProviderDataService()
    
    # Test with an Indian stock
    result = await service.get_stock_data_with_fallback('RELIANCE.NS', '5d')
    
    print(f"Data source: {result['data_source']}")
    print(f"Records count: {len(result['data'])}")
    print(f"Latest price: {result['data'][0]['Close'] if result['data'] else 'No data'}")

# Run the test
asyncio.run(test_providers())
```

## 🎯 **Next Steps**

1. **Sign up for Twelve Data** (highest free tier)
2. **Get Alpha Vantage key** (best Indian market coverage)
3. **Set environment variables**
4. **Test the multi-provider service**
5. **Monitor usage and upgrade as needed**

This setup will eliminate the Yahoo Finance dependency and provide much more reliable data access! 🚀
