import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBRegressor, XGBClassifier
import pickle
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MLService:
    """Machine Learning service for trading predictions"""
    
    def __init__(self):
        self.models_path = "backend/ml_models/"
        os.makedirs(self.models_path, exist_ok=True)
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        df = data.copy()
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Technical indicators
        df['SMA_5'] = df['Close'].rolling(5).mean()
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(20).std()
        
        # Price position
        df['Price_Position'] = (df['Close'] - df['Close'].rolling(20).min()) / (
            df['Close'].rolling(20).max() - df['Close'].rolling(20).min()
        )
        
        # Lag features
        for lag in [1, 2, 3, 5]:
            df[f'Returns_Lag_{lag}'] = df['Returns'].shift(lag)
            df[f'Close_Lag_{lag}'] = df['Close'].shift(lag)
        
        return df.dropna()
    
    async def train_linear_regression(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Train Linear Regression model for price prediction"""
        try:
            df = self.prepare_features(data)
            
            # Features and target
            feature_cols = ['SMA_5', 'SMA_20', 'EMA_12', 'EMA_26', 'Volatility', 
                           'Returns_Lag_1', 'Returns_Lag_2', 'Returns_Lag_3']
            X = df[feature_cols].values
            y = df['Close'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Save model
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_cols': feature_cols,
                'train_score': train_score,
                'test_score': test_score
            }
            
            model_path = f"{self.models_path}{symbol}_linear_regression.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            return {
                "symbol": symbol,
                "model_type": "Linear Regression",
                "train_score": train_score,
                "test_score": test_score,
                "model_path": model_path
            }
        except Exception as e:
            raise Exception(f"Error training Linear Regression for {symbol}: {str(e)}")
    
    async def train_xgboost_classifier(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Train XGBoost classifier for trading signals"""
        try:
            df = self.prepare_features(data)
            
            # Create target (next day direction)
            df['Next_Return'] = df['Returns'].shift(-1)
            df['Direction'] = (df['Next_Return'] > 0).astype(int)
            df = df.dropna()
            
            # Features
            feature_cols = ['Returns', 'SMA_5', 'SMA_20', 'EMA_12', 'EMA_26', 
                           'Volatility', 'Returns_Lag_1', 'Returns_Lag_2', 'Returns_Lag_3']
            X = df[feature_cols].values
            y = df['Direction'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = XGBClassifier(n_estimators=100, max_depth=5, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Save model
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_cols': feature_cols,
                'train_score': train_score,
                'test_score': test_score
            }
            
            model_path = f"{self.models_path}{symbol}_xgboost_classifier.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            return {
                "symbol": symbol,
                "model_type": "XGBoost Classifier",
                "train_accuracy": train_score,
                "test_accuracy": test_score,
                "model_path": model_path
            }
        except Exception as e:
            raise Exception(f"Error training XGBoost for {symbol}: {str(e)}")
    
    async def predict_stock_price(self, symbol: str, model_type: str = "linear_regression") -> Dict:
        """Make stock price prediction using trained model"""
        try:
            # Load model
            model_path = f"{self.models_path}{symbol}_{model_type}.pkl"
            if not os.path.exists(model_path):
                raise Exception(f"Model not found for {symbol}")
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Get latest data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="3mo", interval="1d")
            
            if data.empty:
                raise Exception(f"No data available for {symbol}")
            
            # Prepare features
            df = self.prepare_features(data)
            
            # Make prediction
            X_latest = df[model_data['feature_cols']].iloc[-1:].values
            X_scaled = model_data['scaler'].transform(X_latest)
            
            if model_type == "linear_regression":
                prediction = model_data['model'].predict(X_scaled)[0]
                confidence = model_data['test_score']
            else:  # classifier
                prediction = model_data['model'].predict(X_scaled)[0]
                confidence = max(model_data['model'].predict_proba(X_scaled)[0])
            
            current_price = df['Close'].iloc[-1]
            
            return {
                "symbol": symbol,
                "model_type": model_type,
                "current_price": current_price,
                "predicted_price": prediction if model_type == "linear_regression" else None,
                "predicted_direction": "BUY" if prediction > 0.5 else "SELL" if model_type != "linear_regression" else None,
                "confidence": confidence,
                "prediction_time": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error making prediction for {symbol}: {str(e)}")
    
    async def generate_trading_signals(self, symbols: List[str]) -> List[Dict]:
        """Generate trading signals for multiple symbols"""
        signals = []
        
        for symbol in symbols:
            try:
                # Get data
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="6mo", interval="1d")
                
                if len(data) < 50:
                    continue
                
                # EMA crossover strategy
                data['EMA_20'] = data['Close'].ewm(span=20).mean()
                data['EMA_50'] = data['Close'].ewm(span=50).mean()
                
                latest = data.iloc[-1]
                prev = data.iloc[-2]
                
                # Signal logic
                if latest['EMA_20'] > latest['EMA_50'] and prev['EMA_20'] <= prev['EMA_50']:
                    signal = "BUY"
                    confidence = 0.8
                elif latest['EMA_20'] < latest['EMA_50'] and prev['EMA_20'] >= prev['EMA_50']:
                    signal = "SELL"
                    confidence = 0.8
                else:
                    signal = "HOLD"
                    confidence = 0.6
                
                signals.append({
                    "symbol": symbol,
                    "signal": signal,
                    "confidence": confidence,
                    "price": float(latest['Close']),
                    "timestamp": str(latest.name),
                    "strategy": "EMA_Crossover",
                    "ema_20": float(latest['EMA_20']),
                    "ema_50": float(latest['EMA_50'])
                })
                
            except Exception as e:
                print(f"Error generating signal for {symbol}: {e}")
                continue
        
        return signals
    
    def save_model(self, model: Any, symbol: str, model_type: str) -> str:
        """Save ML model to disk"""
        model_path = f"{self.models_path}{symbol}_{model_type}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        return model_path
    
    def load_model(self, symbol: str, model_type: str) -> Any:
        """Load ML model from disk"""
        model_path = f"{self.models_path}{symbol}_{model_type}.pkl"
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        return None