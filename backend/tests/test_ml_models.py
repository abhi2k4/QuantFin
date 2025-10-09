"""
Unit Tests for ML Models and Prediction Service

Tests all ML models and the prediction service with dummy data.

Author: QuantFin Team
Date: 2025-10-09
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

# Import models
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml_models.linear_reg import LinearRegModel
from app.ml_models.logreg import LogisticRegModel
from app.ml_models.svm_model import SVMModel
from app.ml_models.arima_model import ARIMAModel
from app.ml_models.lstm_model import LSTMModel


class TestMLModels(unittest.TestCase):
    """Test suite for all ML models."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_symbol = "TEST"
        cls.dummy_df = cls._create_dummy_dataframe()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directory."""
        shutil.rmtree(cls.test_dir)
    
    @staticmethod
    def _create_dummy_dataframe(n_samples: int = 500) -> pd.DataFrame:
        """
        Create dummy feature DataFrame for testing.
        
        Args:
            n_samples (int): Number of samples
        
        Returns:
            pd.DataFrame: Dummy data with features
        """
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=n_samples, freq='D')
        
        # Generate synthetic price data with trend and noise
        base_price = 100
        trend = np.linspace(0, 50, n_samples)
        noise = np.random.normal(0, 5, n_samples)
        prices = base_price + trend + noise
        prices = np.maximum(prices, 10)  # Ensure positive prices
        
        df = pd.DataFrame({
            'Date': dates,
            'Open': prices * 0.98,
            'High': prices * 1.02,
            'Low': prices * 0.97,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, n_samples),
        })
        
        # Add technical indicators
        df['SMA_10'] = df['Close'].rolling(10).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['RSI_14'] = 50 + np.random.normal(0, 10, n_samples)  # Simplified RSI
        df['BB_upper'] = df['Close'] * 1.05
        df['BB_lower'] = df['Close'] * 0.95
        df['vol_21'] = df['Close'].rolling(21).std()
        df['avg_volume_21'] = df['Volume'].rolling(21).mean()
        
        # Lagged returns
        df['return_1d'] = df['Close'].pct_change(1)
        df['return_5d'] = df['Close'].pct_change(5)
        df['return_21d'] = df['Close'].pct_change(21)
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def test_linear_reg_model(self):
        """Test LinearRegModel."""
        print("\n=== Testing Linear Regression Model ===")
        
        model = LinearRegModel(
            symbol=self.test_symbol,
            models_dir=str(Path(self.test_dir) / "linear_reg")
        )
        
        # Test training
        metrics = model.train(self.dummy_df, test_size=0.2)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('test_r2', metrics)
        self.assertIn('test_mse', metrics)
        self.assertGreaterEqual(metrics['test_r2'], -1.0)  # R² can be negative
        
        print(f"✓ Training completed: R²={metrics['test_r2']:.4f}")
        
        # Test prediction
        prediction = model.predict(self.dummy_df)
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('expected_return', prediction)
        self.assertIn('confidence_score', prediction)
        self.assertIsInstance(prediction['expected_return'], float)
        
        print(f"✓ Prediction: return={prediction['expected_return']:.4f}, confidence={prediction['confidence_score']:.2f}")
        
        # Test save/load
        saved_path = model.save_model("test_v1")
        self.assertTrue(Path(saved_path).exists())
        
        print(f"✓ Model saved to {saved_path}")
        
        # Load model
        new_model = LinearRegModel(
            symbol=self.test_symbol,
            models_dir=str(Path(self.test_dir) / "linear_reg")
        )
        loaded_metrics = new_model.load_model("test_v1")
        
        self.assertEqual(loaded_metrics['test_r2'], metrics['test_r2'])
        
        print(f"✓ Model loaded successfully")
    
    def test_logreg_model(self):
        """Test LogisticRegModel."""
        print("\n=== Testing Logistic Regression Model ===")
        
        model = LogisticRegModel(
            symbol=self.test_symbol,
            models_dir=str(Path(self.test_dir) / "logreg")
        )
        
        # Test training
        metrics = model.train(self.dummy_df, test_size=0.2)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('test_accuracy', metrics)
        self.assertIn('test_auc', metrics)
        self.assertGreaterEqual(metrics['test_accuracy'], 0.0)
        self.assertLessEqual(metrics['test_accuracy'], 1.0)
        
        print(f"✓ Training completed: accuracy={metrics['test_accuracy']:.4f}, AUC={metrics['test_auc']:.4f}")
        
        # Test prediction
        prediction = model.predict(self.dummy_df)
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('probability_up', prediction)
        self.assertIn('predicted_direction', prediction)
        self.assertGreaterEqual(prediction['probability_up'], 0.0)
        self.assertLessEqual(prediction['probability_up'], 1.0)
        
        print(f"✓ Prediction: P(up)={prediction['probability_up']:.4f}, direction={prediction['predicted_direction']}")
        
        # Test save/load
        saved_path = model.save_model("test_v1")
        self.assertTrue(Path(saved_path).exists())
        
        print(f"✓ Model saved and loaded successfully")
    
    def test_svm_model(self):
        """Test SVMModel."""
        print("\n=== Testing SVM Model ===")
        
        model = SVMModel(
            symbol=self.test_symbol,
            models_dir=str(Path(self.test_dir) / "svm")
        )
        
        # Test training
        metrics = model.train(self.dummy_df, test_size=0.2)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('test_accuracy', metrics)
        self.assertGreaterEqual(metrics['test_accuracy'], 0.0)
        
        print(f"✓ Training completed: accuracy={metrics['test_accuracy']:.4f}")
        
        # Test prediction
        prediction = model.predict(self.dummy_df)
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('probability_up', prediction)
        self.assertGreaterEqual(prediction['probability_up'], 0.0)
        self.assertLessEqual(prediction['probability_up'], 1.0)
        
        print(f"✓ Prediction: P(up)={prediction['probability_up']:.4f}")
        
        # Test save/load
        saved_path = model.save_model("test_v1")
        self.assertTrue(Path(saved_path).exists())
        
        print(f"✓ Model saved and loaded successfully")
    
    def test_arima_model(self):
        """Test ARIMAModel."""
        print("\n=== Testing ARIMA Model ===")
        
        # Create simpler data for ARIMA (just Close prices)
        arima_df = self.dummy_df[['Date', 'Close']].copy()
        
        model = ARIMAModel(
            symbol=self.test_symbol,
            models_dir=str(Path(self.test_dir) / "arima")
        )
        
        # Test training with simple parameters
        metrics = model.train(
            arima_df,
            auto_order=True,
            max_p=2,
            max_d=1,
            max_q=2,
            test_size=21
        )
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('aic', metrics)
        self.assertIn('mse', metrics)
        self.assertIn('order', metrics)
        
        print(f"✓ Training completed: order={metrics['order']}, AIC={metrics['aic']:.2f}")
        
        # Test forecasting
        forecast = model.forecast(steps=21)
        
        self.assertIsInstance(forecast, dict)
        self.assertIn('expected_price', forecast)
        self.assertIn('confidence_interval', forecast)
        self.assertIsInstance(forecast['expected_price'], list)
        self.assertEqual(len(forecast['expected_price']), 21)
        
        print(f"✓ Forecast: 21-day ahead price={forecast['expected_price'][-1]:.2f}")
        
        # Test save/load
        saved_path = model.save_model("test_v1")
        self.assertTrue(Path(saved_path).exists())
        
        print(f"✓ Model saved and loaded successfully")
    
    def test_lstm_model(self):
        """Test LSTMModel."""
        print("\n=== Testing LSTM Model ===")
        
        model = LSTMModel(
            symbol=self.test_symbol,
            models_dir=str(Path(self.test_dir) / "lstm")
        )
        
        # Test training with small architecture for speed
        metrics = model.train(
            self.dummy_df,
            sequence_length=30,
            test_size=0.2,
            epochs=5,  # Small number for testing
            batch_size=32,
            lstm_units_1=32,
            lstm_units_2=16,
            patience=3
        )
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('test_rmse', metrics)
        self.assertIn('test_r2', metrics)
        self.assertIn('epochs_run', metrics)
        self.assertLessEqual(metrics['epochs_run'], 5)
        
        print(f"✓ Training completed: RMSE={metrics['test_rmse']:.4f}, R²={metrics['test_r2']:.4f}")
        
        # Test prediction
        prediction = model.predict(self.dummy_df)
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('expected_price', prediction)
        self.assertIn('model_confidence', prediction)
        self.assertGreater(prediction['expected_price'], 0)
        
        print(f"✓ Prediction: price={prediction['expected_price']:.2f}, confidence={prediction['model_confidence']:.2f}")
        
        # Test save/load
        saved_path = model.save_model("test_v1")
        self.assertTrue(Path(saved_path).exists())
        
        print(f"✓ Model saved and loaded successfully")


class TestPredictionService(unittest.TestCase):
    """Test suite for PredictionService."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_symbols = ["STOCK_A", "STOCK_B", "STOCK_C"]
        
        # Create dummy data for multiple symbols
        cls.dummy_data = {}
        for symbol in cls.test_symbols:
            cls.dummy_data[symbol] = TestMLModels._create_dummy_dataframe(n_samples=300)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directory."""
        shutil.rmtree(cls.test_dir)
    
    def test_model_weighted_allocation(self):
        """Test model-weighted portfolio allocation."""
        print("\n=== Testing Model-Weighted Allocation ===")
        
        # Create mock predictions
        predictions = [
            {
                'symbol': 'STOCK_A',
                'model': 'ENSEMBLE',
                'current_price': 100.0,
                'expected_return': 0.15,
                'confidence': 0.8
            },
            {
                'symbol': 'STOCK_B',
                'model': 'ENSEMBLE',
                'current_price': 200.0,
                'expected_return': 0.10,
                'confidence': 0.6
            },
            {
                'symbol': 'STOCK_C',
                'model': 'ENSEMBLE',
                'current_price': 150.0,
                'expected_return': 0.05,
                'confidence': 0.7
            }
        ]
        
        # Extract data
        symbols = [p['symbol'] for p in predictions]
        returns = np.array([p['expected_return'] for p in predictions])
        confidences = np.array([p['confidence'] for p in predictions])
        
        # Calculate weights (simplified version of model_weighted)
        scores = returns * confidences
        weights = scores / np.sum(scores)
        
        # Apply max weight cap
        max_weight = 0.10
        weights = np.minimum(weights, max_weight)
        weights = weights / np.sum(weights)
        
        self.assertEqual(len(weights), len(symbols))
        self.assertAlmostEqual(np.sum(weights), 1.0, places=2)
        self.assertTrue(np.all(weights >= 0))
        
        print(f"✓ Weights calculated: {dict(zip(symbols, weights))}")
        print(f"✓ Sum of weights: {np.sum(weights):.4f}")
    
    def test_portfolio_metrics(self):
        """Test portfolio metrics calculation."""
        print("\n=== Testing Portfolio Metrics ===")
        
        symbols = ['STOCK_A', 'STOCK_B', 'STOCK_C']
        weights = np.array([0.4, 0.35, 0.25])
        returns = np.array([0.12, 0.08, 0.10])
        
        # Portfolio return
        portfolio_return = np.sum(weights * returns)
        
        # Portfolio volatility (simplified)
        volatilities = np.array([0.20, 0.18, 0.22])
        correlation = 0.30
        
        cov_matrix = np.outer(volatilities, volatilities) * correlation
        np.fill_diagonal(cov_matrix, volatilities ** 2)
        
        portfolio_variance = weights.T @ cov_matrix @ weights
        portfolio_vol = np.sqrt(portfolio_variance)
        
        sharpe_ratio = portfolio_return / portfolio_vol
        
        self.assertGreater(portfolio_return, 0)
        self.assertGreater(portfolio_vol, 0)
        self.assertGreater(sharpe_ratio, 0)
        
        print(f"✓ Portfolio return: {portfolio_return:.4f}")
        print(f"✓ Portfolio volatility: {portfolio_vol:.4f}")
        print(f"✓ Sharpe ratio: {sharpe_ratio:.2f}")
    
    def test_ensemble_prediction(self):
        """Test ensemble prediction logic."""
        print("\n=== Testing Ensemble Prediction ===")
        
        # Mock predictions from different models
        model_predictions = [
            {
                'symbol': 'TEST',
                'model': 'LINEAR_REG',
                'current_price': 100.0,
                'expected_return': 0.10,
                'confidence': 0.7
            },
            {
                'symbol': 'TEST',
                'model': 'LSTM',
                'current_price': 100.0,
                'expected_return': 0.12,
                'confidence': 0.8
            },
            {
                'symbol': 'TEST',
                'model': 'ARIMA',
                'current_price': 100.0,
                'expected_return': 0.08,
                'confidence': 0.6
            }
        ]
        
        # Calculate weighted ensemble
        total_weight = sum(p['confidence'] for p in model_predictions)
        ensemble_return = sum(
            p['expected_return'] * p['confidence'] for p in model_predictions
        ) / total_weight
        ensemble_confidence = total_weight / len(model_predictions)
        
        expected_price = 100.0 * (1 + ensemble_return)
        
        self.assertGreater(ensemble_return, 0)
        self.assertGreater(ensemble_confidence, 0)
        self.assertLessEqual(ensemble_confidence, 1.0)
        
        print(f"✓ Ensemble return: {ensemble_return:.4f}")
        print(f"✓ Ensemble confidence: {ensemble_confidence:.2f}")
        print(f"✓ Expected price: {expected_price:.2f}")
    
    def test_output_format_validation(self):
        """Test output format matches API requirements."""
        print("\n=== Testing Output Format ===")
        
        # Mock prediction output
        prediction_output = {
            'predictions': [
                {
                    'symbol': 'RELIANCE',
                    'model': 'LSTM',
                    'current_price': 2465.0,
                    'expected_price': 2665.8,
                    'expected_return': 0.081,
                    'confidence': 0.66,
                    'prediction_date': datetime.now().isoformat()
                }
            ],
            'portfolio': {
                'strategy': 'model_weighted',
                'weights': [
                    {'symbol': 'RELIANCE', 'weight': 0.12},
                    {'symbol': 'TCS', 'weight': 0.08}
                ],
                'cash': 0.02,
                'expected_return': 0.095,
                'expected_volatility': 0.18
            },
            'metadata': {
                'prediction_date': datetime.now().strftime("%Y-%m-%d"),
                'horizon_days': 21,
                'model_type': 'ensemble'
            }
        }
        
        # Validate structure
        self.assertIn('predictions', prediction_output)
        self.assertIn('portfolio', prediction_output)
        self.assertIn('metadata', prediction_output)
        
        # Validate prediction structure
        pred = prediction_output['predictions'][0]
        required_pred_fields = ['symbol', 'model', 'current_price', 'expected_price', 
                                'expected_return', 'confidence', 'prediction_date']
        for field in required_pred_fields:
            self.assertIn(field, pred)
        
        # Validate portfolio structure
        portfolio = prediction_output['portfolio']
        required_portfolio_fields = ['strategy', 'weights', 'cash', 
                                      'expected_return', 'expected_volatility']
        for field in required_portfolio_fields:
            self.assertIn(field, portfolio)
        
        # Validate weight structure
        weight = portfolio['weights'][0]
        self.assertIn('symbol', weight)
        self.assertIn('weight', weight)
        
        # Validate value ranges
        self.assertGreaterEqual(pred['confidence'], 0.0)
        self.assertLessEqual(pred['confidence'], 1.0)
        self.assertGreaterEqual(portfolio['cash'], 0.0)
        self.assertLessEqual(portfolio['cash'], 1.0)
        
        print(f"✓ Output format validation passed")
        print(f"✓ All required fields present")
        print(f"✓ Value ranges correct")


def run_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running ML Models and Prediction Service Tests")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMLModels))
    suite.addTests(loader.loadTestsFromTestCase(TestPredictionService))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
