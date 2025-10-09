# QuantFin Backend - Quick Start Script
# Run this from the backend directory

Write-Host "🚀 Starting QuantFin Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "❌ Virtual environment not found at .\.venv" -ForegroundColor Red
    Write-Host "Please create it with: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Check if main.py exists
if (-Not (Test-Path ".\main.py")) {
    Write-Host "❌ main.py not found in current directory" -ForegroundColor Red
    Write-Host "Please run this script from the backend directory" -ForegroundColor Yellow
    exit 1
}

# Start uvicorn server
Write-Host "✓ Starting Uvicorn server on http://localhost:8000..." -ForegroundColor Green
Write-Host ""
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📖 Alternative Docs: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
