#!/usr/bin/env python3
"""
Quick test to verify ARIMA accuracy fix
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.ml_training_service import get_training_service

async def test_arima():
    print("\n" + "="*60)
    print("Testing ARIMA Accuracy Fix")
    print("="*60)
    
    service = get_training_service()
    
    print("\n[1/2] Training ARIMA model for RELIANCE...")
    metrics = await service.train_arima_model()
    
    print("\n" + "="*60)
    print("ARIMA METRICS (After Fix)")
    print("="*60)
    print(f"Train Accuracy: {metrics['train_accuracy']:.2f}%")
    print(f"Test Accuracy:  {metrics['accuracy']:.2f}%")
    print(f"Train MAPE:     {metrics['train_mape']:.2f}%")
    print(f"Test MAPE:      {metrics['mape']:.2f}%")
    print(f"Test RMSE:      {metrics['rmse']:.2f}")
    print(f"Test MAE:       {metrics['mae']:.2f}")
    print(f"Test R²:        {metrics['r2_score']:.3f}")
    print("="*60)
    
    if metrics['accuracy'] > 0:
        print("\n✅ SUCCESS: ARIMA accuracy is no longer 0%!")
    else:
        print("\n❌ ISSUE: ARIMA accuracy is still 0%")
    
    print()

if __name__ == "__main__":
    asyncio.run(test_arima())
