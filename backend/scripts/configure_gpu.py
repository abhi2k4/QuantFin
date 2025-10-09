"""
Configure GPU Environment for TensorFlow

This script sets up the environment variables needed for TensorFlow to detect
and use the NVIDIA GPU with CUDA libraries installed via pip.

Author: QuantFin Team  
Date: 2025-10-10
"""

import os
import sys
import site
from pathlib import Path

def configure_gpu_environment():
    """Configure environment variables for GPU support"""
    
    # Get the site-packages directory
    site_packages = site.getsitepackages()[0]
    
    # Paths to NVIDIA libraries installed via pip
    nvidia_paths = [
        os.path.join(site_packages, 'nvidia', 'cublas', 'bin'),
        os.path.join(site_packages, 'nvidia', 'cudnn', 'bin'),
        os.path.join(site_packages, 'nvidia', 'cuda_runtime', 'bin'),
        os.path.join(site_packages, 'nvidia', 'cuda_nvrtc', 'bin'),
    ]
    
    # Add to PATH
    current_path = os.environ.get('PATH', '')
    for nvidia_path in nvidia_paths:
        if os.path.exists(nvidia_path) and nvidia_path not in current_path:
            os.environ['PATH'] = nvidia_path + os.pathsep + current_path
            print(f"✅ Added to PATH: {nvidia_path}")
    
    # Set environment variables for TensorFlow
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
    
    print("\n✅ GPU environment configured")
    return True

def test_gpu():
    """Test if GPU is detected by TensorFlow"""
    print("\n" + "="*60)
    print("Testing GPU Detection")
    print("="*60)
    
    try:
        import tensorflow as tf
        
        print(f"\nTensorFlow version: {tf.__version__}")
        print(f"Built with CUDA: {tf.test.is_built_with_cuda()}")
        
        # List all devices
        print("\nAvailable devices:")
        for device in tf.config.list_physical_devices():
            print(f"  - {device}")
        
        # Check GPUs specifically
        gpus = tf.config.list_physical_devices('GPU')
        
        if gpus:
            print(f"\n✅ SUCCESS! {len(gpus)} GPU(s) detected:")
            for i, gpu in enumerate(gpus):
                print(f"  GPU {i}: {gpu.name}")
                
                # Enable memory growth
                try:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    print(f"    Memory growth: Enabled")
                except:
                    pass
            
            # Quick computation test
            print("\nTesting GPU computation...")
            with tf.device('/GPU:0'):
                a = tf.random.normal([1000, 1000])
                b = tf.random.normal([1000, 1000])
                c = tf.matmul(a, b)
                print(f"✅ Matrix multiplication successful: {c.shape}")
            
            return True
        else:
            print("\n❌ No GPU detected by TensorFlow")
            print("\nTroubleshooting:")
            print("1. Restart your IDE/terminal")
            print("2. Check: nvidia-smi")
            print("3. Reinstall: pip install nvidia-cudnn-cu12==8.9.7.29")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Configure environment first
    configure_gpu_environment()
    
    # Test GPU
    test_gpu()
