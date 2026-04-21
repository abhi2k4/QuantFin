# QuantFin — Project Context (Presentation Hand-off)

## 1) What this project is
QuantFin is a **full‑stack quantitative finance platform** that combines:
- **Market data + technical indicators**
- **ML/DL price/return prediction** (classic ML + time-series + deep learning)
- **Backtesting** to evaluate strategies on historical data
- **Portfolio construction/allocation** (risk/return + forecasting)
- **(Optional) sentiment/news NLP** capabilities (libraries present; depends on which routes/services are used)

The intent is to demonstrate an “end‑to‑end quant workflow”:
1) ingest historical data → 2) engineer features/indicators → 3) train/use models → 4) generate signals/predictions → 5) backtest → 6) allocate a portfolio → 7) visualize results in a web UI.

## 2) Tech stack (what to say on a slide)
**Frontend**
- React + TypeScript (Vite)
- TailwindCSS + shadcn/ui components
- Routing: `react-router-dom`
- Charts: Plotly (`plotly.js`, `react-plotly.js`) and Recharts (installed)
- Auth: Clerk (`@clerk/clerk-react`), requires `VITE_CLERK_PUBLISHABLE_KEY`

**Backend**
- Python + FastAPI
- Uvicorn ASGI server
- Data & ML: pandas, numpy, scikit-learn, xgboost, statsmodels (ARIMA), tensorflow (LSTM)
- Finance data: yfinance
- NLP toolchain (available): nltk, textblob, vaderSentiment, beautifulsoup4, feedparser

## 3) High-level architecture
The repo is a single workspace with:
- `src/` → React frontend
- `backend/` → FastAPI backend
- `data/` → local CSV price data (Nifty 50 constituents)
- `models/` / `model_cache/` → trained model artifacts (e.g., `.h5` LSTM models; plus per-model folders)

Backend entrypoint:
- `backend/main.py` registers routers:
  - `app.routers.portfolio`
  - `app.routers.analytics`
  - `app.routers.backtest` (prefixed in the router)
  - `app.routers.predictions` (prefixed in the router)

Backend services (core logic lives here):
- `backend/app/services/data_preprocessor.py` → loading & preparing symbol data
- `backend/app/services/feature_engineer.py` → features/indicators
- `backend/app/services/ml_model_service.py` / `ml_training_service.py` → model management & training
- `backend/app/services/predict_service.py` → prediction interface
- `backend/app/services/backtester.py` → backtesting logic
- `backend/app/services/portfolio_allocator.py` / `portfolio_manager.py` → portfolio construction
- `backend/app/services/real_data_service.py` → live/real fetching (when used)

Frontend entrypoints:
- `src/main.tsx` sets up Router + ThemeProvider + Clerk.
- `src/App.tsx` defines routes and the top navigation.

## 4) Key product capabilities (demo-friendly)
### A) Predictions / models
- Multiple modeling approaches are supported by dependencies and the service layout:
  - Regression/classification style models (scikit-learn, xgboost)
  - Time-series forecasting (statsmodels ARIMA)
  - Deep learning forecasting (tensorflow LSTM)
- The repo also includes trained artifacts under `models/` (example: `models/*_lstm.h5`).

### B) Backtesting
- The API exposes backtesting endpoints via the `backtest` router.
- Backtesting is used to compare strategy performance using historical data.

### C) Portfolio optimization / allocation
- Portfolio endpoints are grouped under the `portfolio` router.
- The goal is “smart allocation” based on forecasted returns and risk constraints.

### D) Analytics dashboard
- `analytics` router supports dashboard-like metrics and summaries.

### E) UI/UX
- App presents a modern dashboard-style navigation (Dashboard / Models / Backtest / Solutions / Technology).
- Dark theme is the default with a theme toggle.
- Clerk auth is wired in; signed-in users get a user menu.

## 5) Data context
- Local datasets exist in `data/` for many Nifty 50 tickers (CSV per symbol).
- There is also `nifty50.csv` at the repo root.
- Model training/results artifacts exist in `backend/training_results.json`, `backend/training_summary.json`, and validation outputs.

Practical note for a presenter:
- Because the repo includes local CSVs + cached models, it can be demoed **without requiring external APIs** (as long as the backend services are pointed at local data).

## 6) API surface (what a backend slide might include)
Backend runs with FastAPI docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The root endpoint `GET /` returns a small JSON manifest including major route prefixes.

Routers registered:
- `/api/portfolio` (portfolio construction/management)
- `/api/analytics` (dashboard analytics)
- `/api/backtest` (backtesting)
- `/api/predictions` (model predictions)

(Exact endpoint names are defined inside the router files under `backend/app/routers/`.)

## 7) How to run (developer + demo)
### Backend
From repo root:
```bash
cd backend
pip install -r requirements.txt
python run.py
```
Server:
- `http://localhost:8000`
- Health: `http://localhost:8000/health`

### Frontend
From repo root:
```bash
npm install
npm run dev
```
App:
- Vite typically serves at `http://localhost:5173`

Environment requirement (frontend auth):
- Create a `.env` file in the repo root containing:
  - `VITE_CLERK_PUBLISHABLE_KEY=...`

If you don’t want auth for a presentation demo, you can still show the UI structure/screens, but the app will throw at startup if the key is missing (see `src/main.tsx`).

## 8) Suggested presentation flow (5–8 minutes)
1) **Problem**: retail/institutional quant workflows are fragmented.
2) **Solution**: QuantFin unifies data → modeling → backtesting → allocation → visualization.
3) **Architecture**: React UI + FastAPI + local datasets + model cache.
4) **Demo**:
   - Open `http://localhost:5173` → show Dashboard.
   - Open `http://localhost:8000/docs` → show the API schema.
   - Run a prediction/backtest endpoint and show response + chart.
5) **What’s next**: real-time feeds, more strategies, execution integration.

## 9) Important repo files (for quick orientation)
- `README.md` → feature overview
- `backend/main.py` and `backend/run.py` → backend entry
- `backend/app/routers/` → API endpoints
- `backend/app/services/` → ML/backtest/portfolio logic
- `src/App.tsx` → frontend routes/navigation
- `src/pages/` → presentation screens (Dashboard, Models, Backtest, etc.)
- `data/` → ticker CSVs
- `models/` → trained model artifacts

---
