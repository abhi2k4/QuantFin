"""
GPU Availability Check for TensorFlow

This script checks if GPU is available and provides setup instructions if needed.

Usage:
    python scripts/check_gpu.py

Author: QuantFin Team
Date: 2025-10-09
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_gpu():
    """Check GPU availability and provide setup instructions"""
    
    logger.info("="*60)
    logger.info("GPU AVAILABILITY CHECK")
    logger.info("="*60)
    
    try:
        import tensorflow as tf
        
        logger.info(f"TensorFlow version: {tf.__version__}")
        
        # Check for GPUs
        gpus = tf.config.list_physical_devices('GPU')
        
        if gpus:
            logger.info(f"✅ GPU DETECTED: {len(gpus)} device(s)")
            for i, gpu in enumerate(gpus):
                logger.info(f"  GPU {i}: {gpu.name}")
                
                # Get GPU details
                try:
                    gpu_details = tf.config.experimental.get_device_details(gpu)
                    logger.info(f"    Compute Capability: {gpu_details.get('compute_capability', 'N/A')}")
                except:
                    pass
            
            # Test GPU with simple operation
            logger.info("\nTesting GPU with simple operation...")
            with tf.device('/GPU:0'):
                a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
                b = tf.constant([[1.0, 1.0], [0.0, 1.0]])
                c = tf.matmul(a, b)
            
            logger.info("✅ GPU computation successful!")
            logger.info(f"Test result shape: {c.shape}")
            
            return True
            
        else:
            logger.warning("⚠️  NO GPU DETECTED - Using CPU")
            logger.info("\nTo enable GPU acceleration:")
            logger.info("1. Install NVIDIA GPU drivers")
            logger.info("2. Install CUDA Toolkit 11.8")
            logger.info("3. Install cuDNN 8.6")
            logger.info("4. Install tensorflow-gpu or tensorflow[and-cuda]")
            logger.info("\nFor TensorFlow 2.15.0:")
            logger.info("  - CUDA: 11.8")
            logger.info("  - cuDNN: 8.6")
            logger.info("\nDownload links:")
            logger.info("  - CUDA: https://developer.nvidia.com/cuda-11-8-0-download-archive")
            logger.info("  - cuDNN: https://developer.nvidia.com/cudnn")
            logger.info("\nInstall command:")
            logger.info("  pip install tensorflow[and-cuda]")
            
            return False
            
    except ImportError:
        logger.error("❌ TensorFlow not installed!")
        logger.info("Install with: pip install tensorflow")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking GPU: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    has_gpu = check_gpu()
    
    logger.info("\n" + "="*60)
    if has_gpu:
        logger.info("✅ GPU READY FOR TRAINING")
    else:
        logger.info("⚠️  CPU MODE - Training will be slower")
    logger.info("="*60)
    
    sys.exit(0 if has_gpu else 1)
