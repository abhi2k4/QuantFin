#!/bin/bash
# Azure App Service Startup Script for QuantFin Backend

echo "=== Starting QuantFin Backend ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Use PORT env var if set by Azure, otherwise default to 8000
PORT=${PORT:-8000}

echo "Starting gunicorn on port $PORT..."

exec gunicorn \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    main:app
