@echo off
echo Starting QuantFin Backend Server...
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo ERROR: Virtual environment not found at .venv
    echo Please create it with: python -m venv .venv
    pause
    exit /b 1
)

REM Start uvicorn server
echo Starting Uvicorn on http://localhost:8000...
echo API Docs: http://localhost:8000/docs
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
