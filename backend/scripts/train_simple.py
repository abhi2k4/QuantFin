"""
Simple Model Training Script for Testing

This script trains ML models on real stock data from CSV files.
Simplified version without complex dependencies.

Usage:
    python scripts/train_simple.py --symbols RELIANCE TCS --models linear_reg logreg

Author: QuantFin Team
Date: 2025-10-09
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import logging
import argparse
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm

# Configure GPU before importing TensorFlow models
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

try:
    import tensorflow as tf
    # Enable GPU memory growth
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"✅ GPU Training Enabled: {len(gpus)} GPU(s) detected")
    else:
        print("ℹ️  CPU Training Mode: No GPU detected")
except Exception as e:
    print(f"⚠️  GPU configuration failed: {e}")


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

# Import ML models
from app.ml_models.linear_reg import LinearRegModel
from app.ml_models.logreg import LogisticRegModel
from app.ml_models.svm_model import SVMModel
from app.ml_models.arima_model import ARIMAModel
from app.ml_models.lstm_model import LSTMModel

# Import data processing services
from app.services.data_preprocessor import DataPreprocessor
from app.services.feature_engineer import FeatureEngineer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleTrainer:
    """Simple trainer using DataPreprocessor and FeatureEngineer"""
    
    def __init__(self, data_dir: str = "data", quick: bool = False):
        """
        Initialize trainer
        
        Args:
            data_dir: Directory containing CSV files
            quick: Use quick mode (fewer epochs)
        """
        self.quick = quick
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'models_trained': [],
            'errors': [],
            'summary': {}
        }
        
        # Initialize data services
        logger.info("Initializing DataPreprocessor...")
        self.preprocessor = DataPreprocessor(data_dir)
        
        logger.info("Initializing FeatureEngineer...")
        self.engineer = FeatureEngineer(self.preprocessor)
        
        # Get list of available stocks
        self.available_symbols = self.preprocessor.get_all_symbols()
        logger.info(f"Found {len(self.available_symbols)} stock symbols")
    
    def train_linear_regression(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train Linear Regression model"""
        try:
            logger.info(f"  Training Linear Regression...")
            model = LinearRegModel(symbol=symbol)
            metrics = model.train(features)
            model.save_model()
            return {
                'status': 'success',
                'model_type': 'linear_reg',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ Linear Regression failed: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'linear_reg',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_logistic_regression(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train Logistic Regression model"""
        try:
            logger.info(f"  Training Logistic Regression...")
            model = LogisticRegModel(symbol=symbol)
            metrics = model.train(features)
            model.save_model()
            return {
                'status': 'success',
                'model_type': 'logreg',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ Logistic Regression failed: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'logreg',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_svm(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train SVM model"""
        try:
            logger.info(f"  Training SVM...")
            model = SVMModel(symbol=symbol)
            metrics = model.train(features)
            model.save_model()
            return {
                'status': 'success',
                'model_type': 'svm',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ SVM failed: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'svm',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_arima(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train ARIMA model"""
        try:
            logger.info(f"  Training ARIMA...")
            model = ARIMAModel(symbol=symbol)
            metrics = model.train(features)
            model.save_model()
            return {
                'status': 'success',
                'model_type': 'arima',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ ARIMA failed: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'arima',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_lstm(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train LSTM model"""
        try:
            logger.info(f"  Training LSTM...")
            epochs = 5 if self.quick else 50
            model = LSTMModel(symbol=symbol)
            metrics = model.train(features, epochs=epochs)
            model.save_model()
            return {
                'status': 'success',
                'model_type': 'lstm',
                'symbol': symbol,
                'metrics': metrics,
                'epochs': epochs
            }
        except Exception as e:
            logger.error(f"❌ LSTM failed: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'lstm',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_symbol(self, symbol: str, models: List[str]) -> List[Dict]:
        """Train all specified models for one symbol"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {symbol}")
        logger.info(f"{'='*60}")
        
        # Generate features using FeatureEngineer
        try:
            features = self.engineer.generate_features(symbol, lookback=60)
            if features is None:
                error = {'status': 'error', 'symbol': symbol, 'error': 'Failed to generate features'}
                self.results['errors'].append(error)
                return [error]
            
            logger.info(f"  Generated {len(features)} rows with {len(features.columns)} features")
        except Exception as e:
            logger.error(f"Failed to generate features: {str(e)}")
            error = {'status': 'error', 'symbol': symbol, 'error': f'Feature generation failed: {str(e)}'}
            self.results['errors'].append(error)
            return [error]
        
        # Train models
        results = []
        model_trainers = {
            'linear_reg': self.train_linear_regression,
            'logreg': self.train_logistic_regression,
            'svm': self.train_svm,
            'arima': self.train_arima,
            'lstm': self.train_lstm
        }
        
        for model_name in models:
            if model_name not in model_trainers:
                logger.warning(f"Unknown model: {model_name}")
                continue
            
            result = model_trainers[model_name](symbol, features)
            results.append(result)
            
            if result['status'] == 'success':
                self.results['models_trained'].append(result)
                logger.info(f"✅ {model_name} completed")
            else:
                self.results['errors'].append(result)
        
        return results
    
    def train_all(self, symbols: Optional[List[str]] = None, models: Optional[List[str]] = None):
        """Train models for all specified symbols"""
        start_time = datetime.now()
        
        # Default to all available symbols
        if symbols is None:
            symbols = self.available_symbols
        else:
            # Validate symbols
            invalid = [s for s in symbols if s not in self.available_symbols]
            if invalid:
                logger.warning(f"Invalid symbols (will skip): {invalid}")
            symbols = [s for s in symbols if s in self.available_symbols]
        
        # Default to all models
        if models is None:
            models = ['linear_reg', 'logreg', 'svm', 'arima', 'lstm']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting Training")
        logger.info(f"{'='*60}")
        logger.info(f"Symbols: {len(symbols)}")
        logger.info(f"Models: {', '.join(models)}")
        logger.info(f"Quick mode: {self.quick}")
        logger.info(f"{'='*60}\n")
        
        # Train each symbol
        for symbol in tqdm(symbols, desc="Training"):
            self.train_symbol(symbol, models)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.results['summary'] = {
            'total_symbols': len(symbols),
            'total_models': len(models),
            'successful_trainings': len(self.results['models_trained']),
            'failed_trainings': len(self.results['errors']),
            'duration_seconds': duration,
            'duration_formatted': f"{int(duration // 60)}m {int(duration % 60)}s"
        }
        
        logger.info(f"\n{'='*60}")
        logger.info("Training Complete")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful: {len(self.results['models_trained'])}")
        logger.info(f"❌ Errors: {len(self.results['errors'])}")
        logger.info(f"Duration: {self.results['summary']['duration_formatted']}")
        logger.info(f"{'='*60}\n")
    
    def save_summary(self, output_file: str = "training_summary.json"):
        """Save training summary"""
        json_path = Path(output_file)
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2, cls=NumpyEncoder)
        logger.info(f"Summary saved to {json_path}")
        
        # Markdown
        md_path = json_path.with_suffix('.md')
        with open(md_path, 'w') as f:
            f.write("# Model Training Summary\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Timestamp:** {self.results['timestamp']}\n")
            f.write(f"- **Successful:** {self.results['summary']['successful_trainings']}\n")
            f.write(f"- **Failed:** {self.results['summary']['failed_trainings']}\n")
            f.write(f"- **Duration:** {self.results['summary']['duration_formatted']}\n\n")
            
            if self.results['models_trained']:
                f.write("## Successful Trainings\n\n")
                f.write("| Symbol | Model |\n|--------|-------|\n")
                for r in self.results['models_trained']:
                    f.write(f"| {r['symbol']} | {r['model_type']} |\n")
            
            if self.results['errors']:
                f.write("\n## Errors\n\n")
                f.write("| Symbol | Model | Error |\n|--------|-------|-------|\n")
                for e in self.results['errors']:
                    error_msg = e.get('error', 'Unknown')[:40]
                    model = e.get('model_type', 'N/A')
                    f.write(f"| {e['symbol']} | {model} | {error_msg}... |\n")
        
        logger.info(f"Markdown summary saved to {md_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Train ML models')
    parser.add_argument('--symbols', nargs='+', help='Stock symbols (default: all)')
    parser.add_argument('--models', nargs='+', 
                       choices=['linear_reg', 'logreg', 'svm', 'arima', 'lstm'],
                       help='Models to train (default: all)')
    parser.add_argument('--save-summary', action='store_true', help='Save summary')
    parser.add_argument('--quick', action='store_true', help='Quick mode')
    
    args = parser.parse_args()
    
    trainer = SimpleTrainer(quick=args.quick)
    trainer.train_all(symbols=args.symbols, models=args.models)
    
    if args.save_summary:
        trainer.save_summary()


if __name__ == "__main__":
    main()
