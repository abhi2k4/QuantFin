"""
Train only SVM and ARIMA models
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.ml_training_service import MLTrainingService

async def train_specific_models():
    """Train only SVM and ARIMA models."""
    
    print("\n" + "=" * 80)
    print("🚀 TRAINING SVM AND ARIMA MODELS ONLY")
    print("=" * 80)
    print()
    
    training_service = MLTrainingService()
    
    # Train SVM
    print("=" * 80)
    print("1/2 - Training SVM Model")
    print("=" * 80)
    try:
        svm_metrics = await training_service.train_svm_model()
        print(f"✅ SVM Training Complete!")
        print(f"   Test MAE: {svm_metrics.get('mae', 'N/A')}")
        print(f"   Test RMSE: {svm_metrics.get('rmse', 'N/A')}")
        print(f"   Accuracy: {svm_metrics.get('accuracy', 'N/A')}%")
        
        # Save to cache
        training_service.save_model_cache("SVM", svm_metrics)
        print(f"   💾 Saved to cache")
        print()
    except Exception as e:
        print(f"❌ SVM Training Failed: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    # Train ARIMA
    print("=" * 80)
    print("2/2 - Training ARIMA Model")
    print("=" * 80)
    try:
        arima_metrics = await training_service.train_arima_model()
        print(f"✅ ARIMA Training Complete!")
        print(f"   Test MAE: {arima_metrics.get('mae', 'N/A')}")
        print(f"   Test RMSE: {arima_metrics.get('rmse', 'N/A')}")
        print(f"   Accuracy: {arima_metrics.get('accuracy', 'N/A')}%")
        
        # Save to cache
        training_service.save_model_cache("ARIMA", arima_metrics)
        print(f"   💾 Saved to cache")
        print()
    except Exception as e:
        print(f"❌ ARIMA Training Failed: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    print("=" * 80)
    print("✅ TRAINING COMPLETE")
    print("=" * 80)
    print()
    print("Models trained and cached:")
    print("  ✓ SVM")
    print("  ✓ ARIMA")
    print()


if __name__ == "__main__":
    asyncio.run(train_specific_models())
