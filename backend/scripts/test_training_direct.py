"""
Test the training endpoint directly
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.ml_training_service import get_training_service


async def test_training():
    """Test training service directly."""
    print("\n" + "=" * 80)
    print("TESTING TRAINING SERVICE DIRECTLY")
    print("=" * 80)
    
    service = get_training_service()
    
    print("\nInitial status:")
    print(service.get_training_status())
    
    print("\n" + "=" * 80)
    print("STARTING TRAINING (force=True)...")
    print("=" * 80 + "\n")
    
    result = await service.train_all_models(force=True)
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETED")
    print("=" * 80)
    
    print("\nFinal status:")
    print(service.get_training_status())
    
    print(f"\nTrained {len(result.get('models', []))} models")
    
    return result


if __name__ == "__main__":
    asyncio.run(test_training())
