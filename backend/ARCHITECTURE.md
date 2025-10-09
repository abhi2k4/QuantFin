# QuantFin AI-Driven ETF Backend Architecture

## 🏗️ System Overview

This is a production-ready FastAPI backend for an AI-driven ETF portfolio management system. The system uses local historical data (nifty50.csv + 48 individual stock CSVs) and does **NOT** call external market APIs.

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_loader.py         # Load & clean nifty50.csv + 48 CSVs
│   │   ├── features.py            # Technical indicators & feature engineering
│   │   └── persistence.py         # Model artifact management
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── linear_reg.py          # Ridge Regression for price prediction
│   │   ├── logreg.py              # Logistic Regression for direction
│   │   ├── svm_model.py           # SVM classifier
│   │   ├── arima_model.py         # ARIMA/SARIMA time-series
│   │   └── lstm_model.py          # LSTM neural network
│   ├── services/
│   │   ├── __init__.py
│   │   ├── trainer.py             # Orchestrate model training
│   │   ├── portfolio_builder.py   # Portfolio allocation strategies
│   │   └── backtester.py          # Walk-forward backtesting
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── stocks.py              # Stock data & indicators
│   │   ├── predict.py             # Prediction endpoints
│   │   └── performance.py         # Performance metrics
│   └── schemas.py                 # Pydantic models
├── data/
│   ├── *.csv                      # 48 individual stock CSVs
│   └── processed/                 # Parquet files with features
├── models/                        # Trained model artifacts
│   ├── linear_reg/
│   ├── logreg/
│   ├── svm/
│   ├── arima/
│   └── lstm/
├── scripts/
│   └── train_all.py               # CLI training script
├── tests/
│   └── test_*.py                  # Unit tests
├── requirements.txt
└── ARCHITECTURE.md                # This file
```

## 🔄 Data Pipeline

### 1. Data Loading (`core/data_loader.py`)
- Load `nifty50.csv` (multi-index: Date × Symbol × OHLCV)
- Load 48 individual CSVs from `backend/data/*.csv`
- Merge into unified DataFrame: `[Date, Symbol, Open, High, Low, Close, Adj Close, Volume]`
- Validate date alignment across symbols
- Handle missing data with forward-fill (max 5 days) and record imputation
- **Critical**: Ensure no future data leakage

### 2. Feature Engineering (`core/features.py`)
Compute per-symbol technical indicators:

**Price Features:**
- `adj_close`: Adjusted closing price
- `log_return_1d`: Daily log return
- `ret_5d`: 5-day return
- `ret_21d`: 21-day return (monthly)

**Moving Averages:**
- `SMA_10`, `SMA_50`, `SMA_200`
- `EMA_12`, `EMA_26`
- `MACD`: EMA_12 - EMA_26
- `MACD_signal`: 9-day EMA of MACD

**Momentum Indicators:**
- `RSI_14`: 14-day Relative Strength Index
- `BB_upper`, `BB_middle`, `BB_lower`: Bollinger Bands (20-day, 2σ)

**Volatility:**
- `vol_21`: 21-day rolling volatility
- `avg_volume_21`: 21-day average volume

**Lag Features:**
- `lag_1`, `lag_5`: Lagged returns for autocorrelation

### 3. Persistence (`core/persistence.py`)
- Save processed data to `backend/data/processed/{symbol}.parquet`
- Save/load model artifacts (joblib for sklearn, TensorFlow SavedModel)
- Version models with metadata: `{model_name}/{symbol}/v{timestamp}/`

## 🤖 ML Models

### Model 1: Ridge Regression (`ml/linear_reg.py`)
**Purpose**: Predict `future_price_21d` or `future_return_21d`

**Training**:
- Target: `future_return_21d` (21 days ahead)
- Features: All technical indicators + lag features
- Walk-forward CV: Train on expanding window, validate on next 21 days
- Hyperparameter: Ridge alpha (0.01, 0.1, 1.0, 10.0)

**Output**: `(expected_return, confidence_score)`

### Model 2: Logistic Regression (`ml/logreg.py`)
**Purpose**: Binary classification for price direction

**Training**:
- Target: `up_21d` (1 if return > 0.5%, else 0)
- Features: Same as Ridge
- Class balancing: Handle imbalanced classes
- Metrics: Precision, Recall, F1, AUC-ROC

**Output**: `(probability_up, confidence)`

### Model 3: SVM Classifier (`ml/svm_model.py`)
**Purpose**: Non-linear classification orthogonal to LogReg

**Training**:
- Target: `up_21d`
- Kernel: RBF or polynomial
- Grid search for C and gamma
- Probability calibration for confidence scores

**Output**: `(probability_up, confidence)`

### Model 4: ARIMA (`ml/arima_model.py`)
**Purpose**: Time-series forecasting on log-prices

**Training**:
- Per-symbol univariate ARIMA(p,d,q)
- Auto-select (p,d,q) using AIC/BIC
- Forecast 21 days ahead
- Confidence intervals from statsmodels

**Output**: `(expected_price, confidence_interval)`

### Model 5: LSTM (`ml/lstm_model.py`)
**Purpose**: Sequence-to-sequence deep learning

**Architecture**:
```python
Input: [batch, 60, n_features]  # 60-day window
├─ LSTM(128, return_sequences=True)
├─ Dropout(0.2)
├─ LSTM(64)
├─ Dropout(0.2)
├─ Dense(32, activation='relu')
└─ Dense(1)  # Predict next price
```

**Training**:
- Window size: 60 or 90 days
- Normalization: Per-window StandardScaler
- Early stopping: Patience=10, monitor val_loss
- Callbacks: ModelCheckpoint, ReduceLROnPlateau

**Output**: `(expected_price, model_confidence)`

## 🎯 Portfolio Construction

### Strategy 1: Model-Weighted (`services/portfolio_builder.py`)
```python
weight_i = (predicted_return_i * confidence_i) / Σ(predicted_return_j * confidence_j)
weight_i = min(weight_i, max_weight)  # Cap at 10%
```

### Strategy 2: Mean-Variance (Markowitz)
```python
Minimize: w^T Σ w  (portfolio variance)
Subject to:
  - w^T μ >= target_return
  - Σ w_i = 1
  - 0 <= w_i <= max_weight
```

Use `scipy.optimize.minimize` with SLSQP or `cvxpy`

### Strategy 3: Risk-Parity
```python
Allocate such that each asset contributes equally to portfolio risk:
risk_contribution_i = w_i * (Σw)_i / sqrt(w^T Σ w)
Solve: risk_contribution_i = 1/n for all i
```

### Rebalancing Logic
- Frequency: Monthly or Quarterly (configurable)
- Threshold: Only trade if |Δw_i| > 2%
- Transaction cost: 0.05% per trade
- Slippage: 0.1% for large orders

## 📊 Backtesting (`services/backtester.py`)

### Walk-Forward Simulation
```python
for rebalance_date in rebalance_dates:
    # Use only data up to rebalance_date
    predictions = predict_all_models(data[:rebalance_date])
    weights = portfolio_builder.allocate(predictions, strategy)
    
    # Simulate next period
    returns = data[rebalance_date:next_rebalance_date]
    portfolio_value = simulate_period(weights, returns, costs)
    
    nav_history.append(portfolio_value)
```

### Metrics
- **Returns**: Cumulative return, CAGR
- **Risk**: Annualized volatility, max drawdown, downside deviation
- **Risk-Adjusted**: Sharpe ratio, Sortino ratio, Calmar ratio
- **Turnover**: Average monthly turnover %
- **Benchmark**: Compare vs Nifty 50 equal-weighted

## 🌐 API Endpoints

### Health Check
```
GET /api/health
Response: {
  "status": "ok",
  "time": "2025-10-09T12:34:56Z",
  "models_loaded": ["linear_reg", "logreg", "svm", "arima", "lstm"],
  "data_last_updated": "2023-12-31"
}
```

### Stock List
```
GET /api/stocks
Response: [
  {
    "symbol": "RELIANCE",
    "sector": "Energy",
    "last_price": 2465.0,
    "change_1d": 0.012,
    "vol_21": 0.023,
    "rsi_14": 56.3,
    "macd": 12.5
  },
  ...
]
```

### Predictions
```
POST /api/predict
Request: {
  "symbols": ["RELIANCE", "TCS"],
  "date": "2023-12-31",
  "horizon": 21,
  "model": "LSTM"  // or "ensemble"
}

Response: {
  "predictions": [
    {
      "symbol": "RELIANCE",
      "model": "LSTM",
      "current_price": 2465.0,
      "expected_price": 2665.8,
      "expected_return": 0.081,
      "confidence": 0.66,
      "prediction_date": "2024-01-31"
    },
    ...
  ],
  "portfolio": {
    "strategy": "model_weighted",
    "weights": [
      {"symbol": "RELIANCE", "weight": 0.12},
      {"symbol": "TCS", "weight": 0.08},
      ...
    ],
    "cash": 0.02,
    "expected_return": 0.095,
    "expected_volatility": 0.18
  }
}
```

### Backtest
```
POST /api/backtest
Request: {
  "strategy": "mean_variance",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 1000000,
  "rebalance_frequency": "monthly"
}

Response: {
  "nav": [
    {"date": "2020-01-31", "value": 1005000},
    {"date": "2020-02-29", "value": 1012000},
    ...
  ],
  "metrics": {
    "total_return": 0.45,
    "cagr": 0.12,
    "annualized_vol": 0.16,
    "sharpe_ratio": 1.45,
    "sortino_ratio": 2.1,
    "max_drawdown": 0.18,
    "max_drawdown_date": "2020-03-23",
    "turnover": 0.25,
    "win_rate": 0.62
  },
  "vs_benchmark": {
    "nifty50_return": 0.38,
    "alpha": 0.07,
    "beta": 0.95,
    "information_ratio": 0.85
  }
}
```

### Performance Comparison
```
GET /api/performance
Response: {
  "models": [
    {
      "model": "linear_reg",
      "backtest_return": 0.42,
      "sharpe": 1.32,
      "max_dd": 0.21
    },
    {
      "model": "lstm",
      "backtest_return": 0.48,
      "sharpe": 1.52,
      "max_dd": 0.19
    },
    ...
  ],
  "ensemble": {
    "backtest_return": 0.51,
    "sharpe": 1.58,
    "max_dd": 0.17
  },
  "benchmark": {
    "nifty50": {
      "return": 0.38,
      "sharpe": 1.1,
      "max_dd": 0.22
    }
  }
}
```

## 🔐 Implementation Best Practices

1. **No Future Leakage**: Always use `.shift()` for targets
2. **Walk-Forward CV**: Never train on future data
3. **Model Versioning**: Save metadata with every model
4. **Logging**: Structured logs with timestamps
5. **Error Handling**: Graceful degradation, return 5xx only for server errors
6. **Validation**: Pydantic schemas for all I/O
7. **Testing**: Unit tests for core functions
8. **Performance**: Cache processed data, lazy-load models

## 📦 Dependencies (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
pandas==2.1.3
numpy==1.26.2
scipy==1.11.4
scikit-learn==1.3.2
xgboost==2.0.2
tensorflow==2.15.0
statsmodels==0.14.1
spacy==3.7.2
nltk==3.8.1
gensim==4.3.2
vaderSentiment==3.3.2
textblob==0.17.1
beautifulsoup4==4.12.2
pdfplumber==0.10.3
PyPDF2==3.0.1
requests==2.31.0
python-multipart==0.0.6
joblib==1.3.2
pyarrow==14.0.1  # For parquet
python-dateutil==2.8.2
```

## 🚀 Training Script

```bash
# Train all models
python backend/scripts/train_all.py --start-date 2013-01-01 --end-date 2023-12-31

# Train specific model
python backend/scripts/train_all.py --model lstm --symbols RELIANCE TCS
```

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Test specific module
pytest backend/tests/test_data_loader.py -v
```

## 🔄 Deployment

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

**Note**: This is a skeleton/architectural guide. Full implementation requires filling in the logic for each module as described above.
