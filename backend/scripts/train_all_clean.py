"""
Comprehensive ML Model Training Script for All Nifty 50 Stocks

This script trains all ML models on the full dataset of Nifty 50 stocks.

Usage:
    # Train all models for all stocks
    python scripts/train_all_clean.py --save-summary
    
    # Train specific models for specific stocks
    python scripts/train_all_clean.py --symbols RELIANCE TCS --models lstm linear_reg
    
    # Quick training (fewer epochs/iterations)
    python scripts/train_all_clean.py --quick --symbols RELIANCE TCS

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
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

# Import ML models
from app.ml_models.linear_reg import LinearRegModel
from app.ml_models.logreg import LogisticRegModel
from app.ml_models.svm_model import SVMModel
from app.ml_models.arima_model import ARIMAModel
from app.ml_models.lstm_model import LSTMModel

# Import data processing
from app.services.data_preprocessor import DataPreprocessor
from app.services.feature_engineer import FeatureEngineer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Comprehensive model trainer for all stocks"""
    
    def __init__(self, use_gpu: bool = False, quick: bool = False):
        """
        Initialize the model trainer
        
        Args:
            use_gpu: Whether to use GPU for training (currently only affects LSTM)
            quick: Whether to use quick mode (fewer epochs/iterations)
        """
        self.use_gpu = use_gpu
        self.quick = quick
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'models_trained': [],
            'errors': [],
            'summary': {}
        }
        
        # Initialize data processing
        logger.info("Initializing DataPreprocessor...")
        self.preprocessor = DataPreprocessor()
        self.preprocessor.load_data("data")
        
        logger.info("Initializing FeatureEngineer...")
        self.feature_engineer = FeatureEngineer(self.preprocessor)
        
        # Get list of all stocks
        self.all_symbols = self.preprocessor.get_stock_list()
        logger.info(f"Found {len(self.all_symbols)} stocks in dataset")
        
        # Define model types
        self.model_types = {
            'linear_reg': LinearRegModel,
            'logreg': LogisticRegModel,
            'svm': SVMModel,
            'arima': ARIMAModel,
            'lstm': LSTMModel
        }
        
    def get_features_for_symbol(self, symbol: str) -> pd.DataFrame:
        """
        Get features for a specific stock symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with features
        """
        try:
            # Get stock data
            stock_data = self.preprocessor.get_stock_data(symbol)
            if stock_data is None or stock_data.empty:
                logger.error(f"No data available for {symbol}")
                return None
            
            # Create features
            features = self.feature_engineer.create_features([symbol])
            if features is None or features.empty:
                logger.error(f"Failed to create features for {symbol}")
                return None
                
            return features
        except Exception as e:
            logger.error(f"Error getting features for {symbol}: {str(e)}")
            return None
    
    def train_linear_regression(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train Linear Regression model"""
        try:
            logger.info(f"  Training Linear Regression for {symbol}...")
            model = LinearRegModel(symbol=symbol, model_dir="ml_models/linear_reg")
            
            # Train
            metrics = model.train(features)
            
            # Save model
            model.save()
            
            return {
                'status': 'success',
                'model_type': 'linear_reg',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ Linear Regression failed for {symbol}: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'linear_reg',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_logistic_regression(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train Logistic Regression model"""
        try:
            logger.info(f"  Training Logistic Regression for {symbol}...")
            model = LogisticRegModel(symbol=symbol, model_dir="ml_models/logreg")
            
            # Train
            metrics = model.train(features)
            
            # Save model
            model.save()
            
            return {
                'status': 'success',
                'model_type': 'logreg',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ Logistic Regression failed for {symbol}: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'logreg',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_svm(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train SVM model"""
        try:
            logger.info(f"  Training SVM for {symbol}...")
            model = SVMModel(symbol=symbol, model_dir="ml_models/svm")
            
            # Train
            metrics = model.train(features)
            
            # Save model
            model.save()
            
            return {
                'status': 'success',
                'model_type': 'svm',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ SVM failed for {symbol}: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'svm',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_arima(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train ARIMA model"""
        try:
            logger.info(f"  Training ARIMA for {symbol}...")
            model = ARIMAModel(symbol=symbol, model_dir="ml_models/arima")
            
            # Train (ARIMA doesn't use features DataFrame directly)
            metrics = model.train(features)
            
            # Save model
            model.save()
            
            return {
                'status': 'success',
                'model_type': 'arima',
                'symbol': symbol,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"❌ ARIMA failed for {symbol}: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'arima',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_lstm(self, symbol: str, features: pd.DataFrame) -> Dict:
        """Train LSTM model"""
        try:
            logger.info(f"  Training LSTM for {symbol}...")
            model = LSTMModel(symbol=symbol, model_dir="ml_models/lstm")
            
            # Use fewer epochs in quick mode
            epochs = 5 if self.quick else 50
            
            # Train
            metrics = model.train(features, epochs=epochs)
            
            # Save model
            model.save()
            
            return {
                'status': 'success',
                'model_type': 'lstm',
                'symbol': symbol,
                'metrics': metrics,
                'epochs': epochs
            }
        except Exception as e:
            logger.error(f"❌ LSTM failed for {symbol}: {str(e)}")
            return {
                'status': 'error',
                'model_type': 'lstm',
                'symbol': symbol,
                'error': str(e)
            }
    
    def train_symbol(self, symbol: str, models: List[str]) -> List[Dict]:
        """
        Train all specified models for a single stock symbol
        
        Args:
            symbol: Stock symbol
            models: List of model types to train
            
        Returns:
            List of result dictionaries
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {symbol}")
        logger.info(f"{'='*60}")
        
        # Get features
        features = self.get_features_for_symbol(symbol)
        if features is None:
            error_result = {
                'status': 'error',
                'symbol': symbol,
                'error': 'Failed to load features'
            }
            self.results['errors'].append(error_result)
            return [error_result]
        
        # Train each model
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
                logger.warning(f"Unknown model type: {model_name}")
                continue
                
            result = model_trainers[model_name](symbol, features)
            results.append(result)
            
            if result['status'] == 'success':
                self.results['models_trained'].append(result)
                logger.info(f"✅ {model_name} for {symbol} completed successfully")
            else:
                self.results['errors'].append(result)
        
        return results
    
    def train_all(self, symbols: Optional[List[str]] = None, models: Optional[List[str]] = None):
        """
        Train models for all specified symbols
        
        Args:
            symbols: List of symbols to train (None = all)
            models: List of model types to train (None = all)
        """
        start_time = datetime.now()
        
        # Use all symbols if none specified
        if symbols is None:
            symbols = self.all_symbols
        
        # Use all models if none specified
        if models is None:
            models = list(self.model_types.keys())
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting Training")
        logger.info(f"{'='*60}")
        logger.info(f"Symbols: {len(symbols)}")
        logger.info(f"Models: {', '.join(models)}")
        logger.info(f"Quick mode: {self.quick}")
        logger.info(f"Use GPU: {self.use_gpu}")
        logger.info(f"{'='*60}\n")
        
        # Train each symbol
        for symbol in tqdm(symbols, desc="Training symbols"):
            self.train_symbol(symbol, models)
        
        # Calculate summary
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
        logger.info(f"Total symbols: {len(symbols)}")
        logger.info(f"Total models: {len(models)}")
        logger.info(f"✅ Successful: {len(self.results['models_trained'])}")
        logger.info(f"❌ Errors: {len(self.results['errors'])}")
        logger.info(f"Duration: {self.results['summary']['duration_formatted']}")
        logger.info(f"{'='*60}\n")
        
    def save_summary(self, output_file: str = "training_summary.json"):
        """
        Save training summary to JSON and Markdown files
        
        Args:
            output_file: Output JSON file path
        """
        # Save JSON
        json_path = Path(output_file)
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Summary saved to {json_path}")
        
        # Save Markdown
        md_path = json_path.with_suffix('.md')
        with open(md_path, 'w') as f:
            f.write("# Model Training Summary\n\n")
            
            # Summary table
            f.write("## Summary\n\n")
            f.write(f"- **Timestamp:** {self.results['timestamp']}\n")
            f.write(f"- **Total Symbols:** {self.results['summary']['total_symbols']}\n")
            f.write(f"- **Total Models:** {self.results['summary']['total_models']}\n")
            f.write(f"- **Successful Trainings:** {self.results['summary']['successful_trainings']}\n")
            f.write(f"- **Failed Trainings:** {self.results['summary']['failed_trainings']}\n")
            f.write(f"- **Duration:** {self.results['summary']['duration_formatted']}\n\n")
            
            # Successful trainings
            if self.results['models_trained']:
                f.write("## Successful Trainings\n\n")
                f.write("| Symbol | Model | Metrics |\n")
                f.write("|--------|-------|--------|\n")
                for result in self.results['models_trained']:
                    metrics_str = json.dumps(result.get('metrics', {}))[:50]
                    f.write(f"| {result['symbol']} | {result['model_type']} | {metrics_str}... |\n")
                f.write("\n")
            
            # Errors
            if self.results['errors']:
                f.write("## Errors\n\n")
                f.write("| Symbol | Model | Error |\n")
                f.write("|--------|-------|-------|\n")
                for error in self.results['errors']:
                    error_msg = error.get('error', 'Unknown')[:50]
                    model_type = error.get('model_type', 'N/A')
                    f.write(f"| {error['symbol']} | {model_type} | {error_msg}... |\n")
                f.write("\n")
        
        logger.info(f"Markdown summary saved to {md_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Train ML models for stock prediction')
    parser.add_argument('--symbols', nargs='+', help='Stock symbols to train (default: all)')
    parser.add_argument('--models', nargs='+', 
                       choices=['linear_reg', 'logreg', 'svm', 'arima', 'lstm'],
                       help='Models to train (default: all)')
    parser.add_argument('--use-gpu', action='store_true', help='Use GPU for training')
    parser.add_argument('--save-summary', action='store_true', help='Save training summary')
    parser.add_argument('--quick', action='store_true', help='Quick mode (fewer epochs)')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = ModelTrainer(use_gpu=args.use_gpu, quick=args.quick)
    
    # Train models
    trainer.train_all(symbols=args.symbols, models=args.models)
    
    # Save summary if requested
    if args.save_summary:
        trainer.save_summary()


if __name__ == "__main__":
    main()
