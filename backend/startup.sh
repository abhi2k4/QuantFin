#!/bin/bash
# Azure App Service Startup Script for QuantFin Backend

echo "=== Starting QuantFin Backend ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Use PORT env var if set by Azure, otherwise default to 8000
PORT=${PORT:-8000}

# Use the pre-built antenv if available (deployed with artifact),
# otherwise fall back to system gunicorn
if [ -f "/home/site/wwwroot/antenv/bin/gunicorn" ]; then
    GUNICORN="/home/site/wwwroot/antenv/bin/gunicorn"
    echo "Using pre-built antenv gunicorn"
elif [ -f "antenv/bin/gunicorn" ]; then
    GUNICORN="antenv/bin/gunicorn"
    echo "Using relative antenv gunicorn"
else
    GUNICORN="gunicorn"
    echo "Using system gunicorn"
fi

echo "Starting gunicorn on port $PORT..."

exec $GUNICORN \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    main:app
