"""
Simple main.py to avoid import issues
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="QuantFin API",
    description="Quantitative Finance Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "QuantFin API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and include routers only if they work
try:
    from app.routers import trading, portfolio, reports, data
    app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    app.include_router(data.router, prefix="/api/data", tags=["data"])
    print("✅ All routers loaded successfully")
except Exception as e:
    print(f"❌ Error loading routers: {e}")
    
    # Load minimal routers
    from app.routers import trading
    app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
    print("✅ Loaded trading router only")
