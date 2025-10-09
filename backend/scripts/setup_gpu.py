"""
GPU Setup Script for TensorFlow with CUDA 12.9

This script helps set up TensorFlow with GPU support for NVIDIA RTX 3050.

For TensorFlow 2.15+ with CUDA 12.9, you need:
1. tensorflow (or tensorflow-gpu, they're the same now)
2. CUDA Toolkit 12.x (already installed - CUDA 12.9 detected)
3. cuDNN 8.x (install via pip)

Author: QuantFin Team
Date: 2025-10-10
"""

import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ NVIDIA GPU detected")
            print("\n" + result.stdout)
            return True
        else:
            logger.error("❌ nvidia-smi failed")
            return False
    except FileNotFoundError:
        logger.error("❌ nvidia-smi not found. Please install NVIDIA drivers.")
        return False

def check_current_tensorflow():
    """Check current TensorFlow installation"""
    try:
        import tensorflow as tf
        logger.info(f"Current TensorFlow version: {tf.__version__}")
        
        # Check for GPU
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"✅ TensorFlow detects {len(gpus)} GPU(s)")
            for gpu in gpus:
                logger.info(f"  - {gpu.name}")
            return True
        else:
            logger.warning("⚠️  TensorFlow does NOT detect GPU")
            logger.info("This usually means:")
            logger.info("  1. tensorflow-intel (CPU-only) is installed")
            logger.info("  2. Missing CUDA libraries")
            logger.info("  3. Incompatible CUDA/cuDNN versions")
            return False
    except ImportError:
        logger.error("❌ TensorFlow not installed")
        return False

def install_gpu_support():
    """Install TensorFlow GPU support"""
    logger.info("\n" + "="*60)
    logger.info("Installing TensorFlow GPU Support")
    logger.info("="*60)
    
    commands = [
        # Uninstall CPU-only versions
        [sys.executable, "-m", "pip", "uninstall", "-y", "tensorflow-intel"],
        [sys.executable, "-m", "pip", "uninstall", "-y", "tensorflow"],
        
        # Install TensorFlow with GPU support
        [sys.executable, "-m", "pip", "install", "tensorflow==2.15.0"],
        
        # Install CUDA and cuDNN via pip (for Windows, easier than manual installation)
        [sys.executable, "-m", "pip", "install", "nvidia-cudnn-cu12==8.9.7.29"],
        [sys.executable, "-m", "pip", "install", "nvidia-cublas-cu12"],
        [sys.executable, "-m", "pip", "install", "nvidia-cuda-runtime-cu12"],
    ]
    
    for cmd in commands:
        logger.info(f"\nRunning: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "not installed" not in result.stdout:
            logger.warning(f"Warning: {result.stderr}")
        else:
            logger.info("✅ Success")
    
    logger.info("\n" + "="*60)
    logger.info("Installation complete!")
    logger.info("="*60)

def verify_gpu_setup():
    """Verify GPU is working with TensorFlow"""
    logger.info("\n" + "="*60)
    logger.info("Verifying GPU Setup")
    logger.info("="*60)
    
    try:
        import tensorflow as tf
        logger.info(f"TensorFlow version: {tf.__version__}")
        
        # List devices
        logger.info("\nPhysical devices:")
        for device in tf.config.list_physical_devices():
            logger.info(f"  - {device}")
        
        # GPU-specific check
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"\n✅ SUCCESS! {len(gpus)} GPU(s) available:")
            for i, gpu in enumerate(gpus):
                logger.info(f"  GPU {i}: {gpu.name}")
                try:
                    details = tf.config.experimental.get_device_details(gpu)
                    if details:
                        logger.info(f"    Details: {details}")
                except:
                    pass
            
            # Test GPU with computation
            logger.info("\nTesting GPU with matrix multiplication...")
            with tf.device('/GPU:0'):
                a = tf.random.normal([1000, 1000])
                b = tf.random.normal([1000, 1000])
                c = tf.matmul(a, b)
            logger.info("✅ GPU computation successful!")
            
            return True
        else:
            logger.error("❌ No GPU detected by TensorFlow")
            logger.info("\nTroubleshooting:")
            logger.info("1. Restart your terminal/IDE")
            logger.info("2. Check CUDA installation: nvidia-smi")
            logger.info("3. Verify PATH includes CUDA bin directory")
            logger.info("4. Try: python -c \"import tensorflow as tf; print(tf.config.list_physical_devices())\"")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during verification: {e}")
        return False

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("TensorFlow GPU Setup for NVIDIA RTX 3050 (CUDA 12.9)")
    print("="*60)
    
    # Step 1: Check NVIDIA GPU
    if not check_nvidia_gpu():
        logger.error("Cannot proceed without NVIDIA GPU")
        return
    
    # Step 2: Check current TensorFlow
    has_gpu = check_current_tensorflow()
    
    if has_gpu:
        logger.info("\n✅ GPU is already working!")
        return
    
    # Step 3: Ask user to install
    print("\n" + "="*60)
    response = input("Do you want to install TensorFlow GPU support? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        logger.info("Setup cancelled")
        return
    
    # Step 4: Install GPU support
    install_gpu_support()
    
    # Step 5: Verify
    print("\n" + "="*60)
    input("Press Enter to verify GPU setup (this will reimport TensorFlow)...")
    
    # Need to restart Python to pick up new packages
    logger.info("\n⚠️  IMPORTANT: You need to restart Python/IDE for changes to take effect")
    logger.info("After restart, run this script again to verify")

if __name__ == "__main__":
    main()
