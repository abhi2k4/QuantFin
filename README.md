# QuantFin - Advanced Quantitative Finance Platform

A comprehensive web application for quantitative finance featuring ML/DL algorithms for algorithmic trading, smart portfolio construction, and NLP-based financial report analysis.

## 🚀 Features

### Backend (FastAPI + Python)
- **Algorithmic Trading Predictions**: Multiple ML models (Linear Regression, XGBoost, SVM)
- **Smart Portfolio Construction**: ARIMA, LSTM, and regression-based optimization
- **NLP Financial Analysis**: News sentiment analysis with VADER and TextBlob
- **Real-time Data**: Integration with Yahoo Finance, Alpha Vantage, Twelve Data
- **Technical Indicators**: RSI, MACD, Bollinger Bands, EMA/SMA
- **Backtesting Engine**: Strategy performance analysis
- **Risk Management**: Portfolio optimization and risk metrics

### Frontend (React + TailwindCSS)
- **Responsive Dashboard**: Real-time market overview and sentiment
- **Trading Interface**: Live signals, backtesting, and strategy management
- **Portfolio Manager**: ML-based allocation and performance tracking
- **Reports & Analysis**: Fundamental analysis and news sentiment
- **Interactive Charts**: Candlestick charts with technical indicators
- **Dark Theme**: Professional financial application design

## 🏗️ Architecture

```
quantfin/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── routers/             # API endpoints
│   │   │   ├── trading.py       # Trading signals & backtesting
│   │   │   ├── portfolio.py     # Portfolio optimization
│   │   │   ├── reports.py       # News & fundamental analysis
│   │   │   └── data.py          # Market data endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── data_service.py  # Data fetching & processing
│   │   │   ├── ml_service.py    # Machine learning models
│   │   │   ├── portfolio_service.py # Portfolio management
│   │   │   └── news_service.py  # News analysis & NLP
│   │   └── utils/config.py      # Configuration
│   ├── ml_models/               # Trained ML models
│   ├── data/                    # Dataset storage
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/              # Main application pages
│   │   ├── services/api.js     # API client
│   │   └── utils/formatters.js # Data formatting utilities
│   └── package.json
└── README.md
```

## 🛠️ Setup & Installation

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
npm install
npm run dev
```

## 📊 ML Models & Algorithms

### Trading Strategies
- **EMA Crossover**: Exponential Moving Average signals
- **Linear Regression**: Price prediction using historical trends
- **XGBoost Classifier**: Direction prediction with feature engineering
- **SVM**: Support Vector Machine for market regime classification

### Portfolio Optimization
- **Risk-Return Optimization**: Modern Portfolio Theory implementation
- **ML-Based Allocation**: Expected return forecasting using multiple models
- **ARIMA Time Series**: Statistical forecasting for asset allocation
- **LSTM Neural Networks**: Deep learning for price prediction

### NLP Analysis
- **News Sentiment**: VADER + TextBlob sentiment analysis
- **Market Intelligence**: Real-time news aggregation and analysis
- **Fundamental Scoring**: Automated fundamental analysis scoring

## 🎯 API Endpoints

### Trading
- `GET /api/trading/signals/{symbol}` - Get trading signal
- `POST /api/trading/backtest` - Backtest strategy
- `GET /api/trading/predictions/{symbol}` - ML price prediction

### Portfolio
- `POST /api/portfolio/optimize` - Optimize portfolio allocation
- `GET /api/portfolio/performance` - Portfolio performance metrics
- `GET /api/portfolio/recommendations` - Investment recommendations

### Reports
- `GET /api/reports/news/{symbol}` - News sentiment analysis
- `GET /api/reports/market-sentiment` - Market sentiment overview
- `GET /api/reports/fundamental-analysis/{symbol}` - Fundamental analysis

### Data
- `GET /api/data/stock/{symbol}` - Historical stock data with indicators
- `GET /api/data/nifty50` - Nifty 50 constituent data
- `GET /api/data/market-overview` - Market indices overview

## 🚦 Getting Started

1. **Start Backend**: Run the FastAPI server
2. **Start Frontend**: Launch the React development server  
3. **Access Dashboard**: Navigate to `http://localhost:5173`
4. **Explore Features**: 
   - View real-time market data on Dashboard
   - Generate trading signals in Trading section
   - Optimize portfolios in Portfolio manager
   - Analyze news sentiment in Reports

## 📈 Key Features in Action

- **Real-time Trading Signals**: EMA crossover and ML-based predictions
- **Portfolio Optimization**: Top 10 Nifty stocks with ML forecasting
- **Backtesting**: Historical performance analysis for strategies
- **News Analysis**: Sentiment scoring for market intelligence
- **Technical Analysis**: RSI, MACD, Bollinger Bands integration
- **Risk Management**: Diversification and volatility analysis

## 🔮 Future Enhancements

- Real-time WebSocket data feeds
- Advanced options strategies
- Cryptocurrency integration
- Social sentiment analysis
- Automated trading execution
- Performance attribution analysis

Built with modern technologies for professional quantitative finance applications.