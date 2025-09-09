from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from pathlib import Path
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.routers import trading, portfolio, reports, data
from app.services.data_service import DataService
from app.utils.config import get_settings
from app.utils.json_encoder import clean_data_for_json, CustomJSONEncoder

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="QuantFin API",
    description="Quantitative Finance Platform with ML/DL Trading Algorithms",
    version="1.0.0"
)

# Custom middleware to handle JSON serialization
@app.middleware("http")
async def process_responses(request, call_next):
    response = await call_next(request)
    return response

# Custom JSON response class
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        cleaned_content = clean_data_for_json(content)
        return json.dumps(
            cleaned_content,
            cls=CustomJSONEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# Set default response class
app.default_response_class = CustomJSONResponse

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(data.router, prefix="/api/data", tags=["data"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize data service
        data_service = DataService()
        app.state.data_service = data_service
        print("✅ QuantFin API started successfully")
    except Exception as e:
        print(f"❌ Failed to start API: {e}")

@app.get("/")
async def root():
    return {"message": "QuantFin API - Advanced Quantitative Finance Platform"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "QuantFin API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )