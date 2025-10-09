"""
Main FastAPI Application for ETF Portfolio System

This is the entry point for the AI-driven ETF portfolio management system.
It initializes the FastAPI application, configures middleware, and registers
all routers.

Author: QuantFin Team
Date: 2025-10-09
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import time

from routers import sectors
from app.routers import backtest, predictions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="QuantFin ETF Portfolio API",
    description="AI-driven ETF portfolio management system with sector-based analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add processing time to response headers.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# Register routers
app.include_router(sectors.router, prefix="/api")
app.include_router(backtest.router)  # Already has /api/backtest prefix
app.include_router(predictions.router)  # Already has /api/predictions prefix


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "name": "QuantFin ETF Portfolio API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "documentation": "/docs",
        "endpoints": {
            "sectors": "/api/sectors",
            "backtest": "/api/backtest",
            "predictions": "/api/predictions",
            "health": "/health"
        }
    }


# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "QuantFin ETF Portfolio API"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Executed when the application starts.
    Initializes data preprocessing and loads data.
    """
    logger.info("=" * 60)
    logger.info("Starting QuantFin ETF Portfolio API")
    logger.info("=" * 60)
    
    try:
        # Trigger data loading by accessing the preprocessor
        from services.preprocessing import get_preprocessor
        preprocessor = get_preprocessor()
        
        logger.info(f"Loaded {len(preprocessor.stock_data)} stocks")
        logger.info(f"Created {len(preprocessor.sector_data)} sector aggregations")
        
        date_range = preprocessor.get_date_range()
        if date_range:
            logger.info(f"Data range: {date_range[0].date()} to {date_range[1].date()}")
        
        logger.info("Data preprocessing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        logger.warning("API will start but data may not be available")
    
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Executed when the application shuts down.
    Cleanup operations can be performed here.
    """
    logger.info("=" * 60)
    logger.info("Shutting down QuantFin ETF Portfolio API")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
