# 🎯 QuantFin Navigation Guide

## 📍 How to Access All Features

### From Dashboard:

When you're on the **Dashboard** (`/dashboard`), you'll see two prominent buttons in the top-right corner:

#### 1. **ML Analytics Button** (Purple gradient)
- Click this to go to the **Analytics page** (`/analytics`)
- Features:
  - 📊 ML Model Comparison (LSTM, Linear Regression, SVM, ARIMA)
  - 📈 Candlestick Charts with OHLCV data
  - 🎯 Detailed metrics tables
  - 🔄 Live model training
  - 📉 90-day price action analysis

#### 2. **Backtesting Button** (Green gradient)
- Click this to go to the **Backtesting page** (`/backtest`)
- Features:
  - 📊 Strategy comparison
  - 💰 Portfolio performance analysis
  - 📈 Historical backtesting results
  - 🎯 Risk-adjusted returns

### Direct URLs:

You can also navigate directly by typing these URLs in your browser:

```
http://localhost:5173/dashboard     → Portfolio Dashboard
http://localhost:5173/analytics     → ML Analytics & Charts
http://localhost:5173/backtest      → Backtesting Results
http://localhost:5173/models        → Model Insights
```

### What's on Each Page:

#### **Dashboard** (`/dashboard`)
✅ Real portfolio value (₹771,238)
✅ 4 stock holdings with real prices
✅ Performance graph (1M/3M/6M/1Y timeframes)
✅ Portfolio allocation pie chart
✅ Rebalance portfolio with ML strategies
✅ Positions table with sorting

#### **Analytics** (`/analytics`) - **NEW!**
✅ 4 ML model cards with accuracy metrics
✅ Model comparison bar chart
✅ Interactive candlestick charts for 6 stocks
✅ Switch between RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN
✅ 90-day high/low/volume statistics
✅ Detailed metrics comparison table
✅ Train models button (takes 30+ seconds)
✅ Best model highlighting with award icon

#### **Backtesting** (`/backtest`)
✅ Strategy performance comparison
✅ Historical returns analysis
✅ Risk metrics
✅ Drawdown charts

### Navigation Flow:

```
Landing Page
    ↓
  Sign Up / Login
    ↓
  Dashboard (Main hub)
    ↓
  ┌─────────┴─────────┐
  ↓                   ↓
Analytics         Backtesting
  ↓                   ↓
(ML Comparison)   (Strategy Results)
```

## 🎨 Visual Indicators:

- **Purple gradient button** → ML Analytics
- **Green gradient button** → Backtesting
- **Gray button with refresh icon** → Reload data

## 🚀 Quick Start:

1. Go to Dashboard: `http://localhost:5173/dashboard`
2. See your portfolio with real data
3. Click **"ML Analytics"** button (purple) in top-right
4. Explore candlestick charts and model comparison
5. Switch between stocks using the stock buttons
6. Go back to Dashboard
7. Click **"Backtesting"** button (green) in top-right
8. View strategy performance

## 💡 Pro Tips:

- **Analytics page** is perfect for:
  - Comparing ML model accuracies
  - Viewing stock price patterns
  - Analyzing OHLCV data
  - Training custom models

- **Dashboard** is perfect for:
  - Quick portfolio overview
  - Rebalancing with ML predictions
  - Checking daily changes
  - Viewing allocation

- **Backtesting** is perfect for:
  - Testing strategies historically
  - Comparing returns
  - Risk analysis
  - Performance validation

## 🎯 Current Status:

✅ **Dashboard** - Fully functional with real data
✅ **Analytics** - Fully functional with ML comparison & candlestick charts
✅ **Backtesting** - Available at `/backtest` route
✅ **Navigation** - Updated with correct routes

**All features are ready to use!** 🎉
