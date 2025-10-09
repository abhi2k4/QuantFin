"""
Quick start script for QuantFin ETF Portfolio API.

This script runs the FastAPI server with optimal settings for development.
"""

import uvicorn
import sys
import os

if __name__ == "__main__":
    print("=" * 70)
    print("  QuantFin ETF Portfolio API - Starting Server")
    print("=" * 70)
    print()
    print("  📍 API URL:       http://localhost:8000")
    print("  📚 API Docs:      http://localhost:8000/docs")
    print("  📖 ReDoc:         http://localhost:8000/redoc")
    print("  ❤️  Health Check: http://localhost:8000/health")
    print()
    print("=" * 70)
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error starting server: {e}")
        sys.exit(1)
