"""
Portfolio Manager - Real portfolio calculations and management

Manages user portfolios using actual stock data and calculates
real returns, risk metrics, and performance.

Author: QuantFin Team
Date: 2025-10-10
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import logging

from .real_data_service import get_real_data_service

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Manages real portfolios with actual stock positions and calculations.
    """
    
    def __init__(self, portfolio_file: Optional[str] = None):
        """Initialize portfolio manager."""
        if portfolio_file is None:
            portfolio_file = Path(__file__).resolve().parent.parent.parent / "data" / "portfolio.json"
        
        self.portfolio_file = Path(portfolio_file)
        self.data_service = get_real_data_service()
        self.logger = logging.getLogger(__name__)
        
        # Load or create portfolio
        self.portfolio = self._load_portfolio()
    
    def _load_portfolio(self) -> Dict:
        """Load portfolio from JSON file or create default."""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        else:
            # Create default portfolio with sample positions
            default_portfolio = {
                'cash_balance': 500000.0,
                'positions': {
                    'RELIANCE': {'quantity': 50, 'avg_buy_price': 2500.0},
                    'TCS': {'quantity': 30, 'avg_buy_price': 3500.0},
                    'INFY': {'quantity': 40, 'avg_buy_price': 1500.0},
                    'HDFCBANK': {'quantity': 60, 'avg_buy_price': 1600.0}
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            self._save_portfolio(default_portfolio)
            return default_portfolio
    
    def _save_portfolio(self, portfolio: Dict):
        """Save portfolio to JSON file."""
        self.portfolio_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get comprehensive portfolio summary with real calculations.
        
        Returns:
            Dict with positions, values, and daily changes
        """
        positions_data = []
        total_invested = 0.0
        current_value = 0.0
        
        # Get latest prices
        symbols = list(self.portfolio['positions'].keys())
        latest_prices = self.data_service.get_latest_prices(symbols)
        
        # Calculate yesterday's value for daily change
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_value = 0.0
        
        for symbol, position_info in self.portfolio['positions'].items():
            quantity = position_info['quantity']
            avg_buy_price = position_info['avg_buy_price']
            
            if symbol not in latest_prices:
                self.logger.warning(f"No price data for {symbol}")
                continue
            
            current_price = latest_prices[symbol]
            position_value = quantity * current_price
            invested = quantity * avg_buy_price
            
            gain_loss = position_value - invested
            gain_loss_percent = (gain_loss / invested) * 100 if invested > 0 else 0
            
            # Get yesterday's price for daily change
            yesterday_price = self.data_service.get_price_on_date(symbol, yesterday)
            if yesterday_price:
                yesterday_position_value = quantity * yesterday_price
                yesterday_value += yesterday_position_value
                
                daily_change = current_price - yesterday_price
                daily_change_percent = (daily_change / yesterday_price) * 100
            else:
                daily_change = 0
                daily_change_percent = 0
            
            positions_data.append({
                'symbol': symbol,
                'quantity': quantity,
                'avg_buy_price': round(avg_buy_price, 2),
                'current_price': round(current_price, 2),
                'invested': round(invested, 2),
                'current_value': round(position_value, 2),
                'gain_loss': round(gain_loss, 2),
                'gain_loss_percent': round(gain_loss_percent, 2),
                'daily_change': round(daily_change, 2),
                'daily_change_percent': round(daily_change_percent, 2),
                'allocation_percent': 0  # Will calculate below
            })
            
            total_invested += invested
            current_value += position_value
        
        # Calculate allocation percentages
        for position in positions_data:
            position['allocation_percent'] = round(
                (position['current_value'] / current_value) * 100, 2
            ) if current_value > 0 else 0
        
        # Calculate portfolio daily change
        if yesterday_value > 0:
            daily_change = current_value - yesterday_value
            daily_change_percent = (daily_change / yesterday_value) * 100
        else:
            daily_change = 0
            daily_change_percent = 0
        
        cash_balance = self.portfolio.get('cash_balance', 0)
        total_value = current_value + cash_balance
        
        return {
            'total_value': round(total_value, 2),
            'invested_value': round(total_invested, 2),
            'current_holdings_value': round(current_value, 2),
            'cash_balance': round(cash_balance, 2),
            'total_gain_loss': round(current_value - total_invested, 2),
            'total_gain_loss_percent': round(((current_value - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0,
            'daily_change': round(daily_change, 2),
            'daily_change_percent': round(daily_change_percent, 2),
            'total_positions': len(positions_data),
            'positions': positions_data
        }
    
    def get_portfolio_performance(self, timeframe: str = '3M') -> Dict:
        """
        Get historical portfolio performance.
        
        Args:
            timeframe: '1M', '3M', '6M', '1Y'
            
        Returns:
            Dict with dates and values
        """
        # Map timeframe to days
        timeframe_days = {
            '1M': 30,
            '3M': 90,
            '6M': 180,
            '1Y': 365
        }
        
        days = timeframe_days.get(timeframe, 90)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get positions
        positions = self.portfolio['positions']
        
        # Calculate portfolio value for each day
        dates = []
        values = []
        
        # Sample every few days to reduce computation
        sample_interval = max(1, days // 100)
        
        for i in range(0, days, sample_interval):
            date = start_date + timedelta(days=i)
            
            portfolio_value = 0.0
            for symbol, position_info in positions.items():
                quantity = position_info['quantity']
                price = self.data_service.get_price_on_date(symbol, date)
                
                if price:
                    portfolio_value += quantity * price
            
            # Add cash balance
            portfolio_value += self.portfolio.get('cash_balance', 0)
            
            dates.append(date.strftime('%Y-%m-%d'))
            values.append(round(portfolio_value, 2))
        
        # Calculate returns
        if len(values) > 1:
            total_return = values[-1] - values[0]
            total_return_percent = (total_return / values[0]) * 100 if values[0] > 0 else 0
        else:
            total_return = 0
            total_return_percent = 0
        
        return {
            'timeframe': timeframe,
            'dates': dates,
            'values': values,
            'total_return': round(total_return, 2),
            'total_return_percent': round(total_return_percent, 2),
            'start_value': values[0] if values else 0,
            'end_value': values[-1] if values else 0
        }
    
    def calculate_risk_metrics(self) -> Dict:
        """Calculate portfolio risk metrics (Sharpe ratio, volatility, etc.)."""
        positions = self.portfolio['positions']
        
        # Calculate portfolio returns
        returns_data = {}
        for symbol in positions.keys():
            try:
                returns = self.data_service.calculate_returns(symbol)
                returns_data[symbol] = returns
            except Exception as e:
                self.logger.warning(f"Could not calculate returns for {symbol}: {e}")
                continue
        
        if not returns_data:
            return {
                'sharpe_ratio': 0,
                'volatility': 0,
                'max_drawdown': 0,
                'beta': 0
            }
        
        # Combine returns weighted by allocation
        returns_df = pd.DataFrame(returns_data)
        
        # Get current allocations
        summary = self.get_portfolio_summary()
        weights = {}
        for position in summary['positions']:
            weights[position['symbol']] = position['allocation_percent'] / 100
        
        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0, index=returns_df.index)
        for symbol, weight in weights.items():
            if symbol in returns_df.columns:
                portfolio_returns += returns_df[symbol] * weight
        
        # Calculate metrics
        mean_return = portfolio_returns.mean()
        volatility = portfolio_returns.std()
        
        # Sharpe Ratio (assuming risk-free rate = 0.05/252 daily)
        risk_free_rate = 0.05 / 252
        sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Max Drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'annual_return': round(float(mean_return * 252 * 100), 2),
            'volatility': round(float(volatility * np.sqrt(252) * 100), 2),
            'sharpe_ratio': round(float(sharpe_ratio * np.sqrt(252)), 2),
            'max_drawdown': round(float(max_drawdown * 100), 2)
        }
    
    def add_position(self, symbol: str, quantity: int, price: float):
        """Add or update a position."""
        if symbol not in self.portfolio['positions']:
            self.portfolio['positions'][symbol] = {
                'quantity': quantity,
                'avg_buy_price': price
            }
        else:
            # Update average price
            current = self.portfolio['positions'][symbol]
            total_quantity = current['quantity'] + quantity
            total_cost = (current['quantity'] * current['avg_buy_price']) + (quantity * price)
            avg_price = total_cost / total_quantity
            
            self.portfolio['positions'][symbol] = {
                'quantity': total_quantity,
                'avg_buy_price': avg_price
            }
        
        self.portfolio['last_updated'] = datetime.now().isoformat()
        self._save_portfolio(self.portfolio)
    
    def remove_position(self, symbol: str, quantity: int):
        """Remove or reduce a position."""
        if symbol in self.portfolio['positions']:
            current_qty = self.portfolio['positions'][symbol]['quantity']
            
            if quantity >= current_qty:
                del self.portfolio['positions'][symbol]
            else:
                self.portfolio['positions'][symbol]['quantity'] = current_qty - quantity
            
            self.portfolio['last_updated'] = datetime.now().isoformat()
            self._save_portfolio(self.portfolio)


# Global instance
_portfolio_manager = None


def get_portfolio_manager() -> PortfolioManager:
    """Get or create global PortfolioManager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager
