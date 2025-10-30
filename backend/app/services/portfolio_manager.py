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
from .portfolio_db import get_portfolio_db

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Manages real portfolios with actual stock positions stored in SQLite.
    """
    
    def __init__(self):
        """Initialize portfolio manager with SQLite database."""
        self.data_service = get_real_data_service()
        self.db = get_portfolio_db()
        self.logger = logging.getLogger(__name__)
        # Don't initialize default portfolio here - do it on first access
    
    def _initialize_default_portfolio(self):
        """Initialize portfolio with some default stocks if database is empty."""
        # Simple fallback - just add some popular stocks with default allocations
        default_positions = [
            {'symbol': 'RELIANCE', 'quantity': 20, 'buy_price': 2500.0, 'allocation_amount': 50000},
            {'symbol': 'TCS', 'quantity': 15, 'buy_price': 3500.0, 'allocation_amount': 52500},
            {'symbol': 'INFY', 'quantity': 30, 'buy_price': 1500.0, 'allocation_amount': 45000},
            {'symbol': 'HDFCBANK', 'quantity': 25, 'buy_price': 1600.0, 'allocation_amount': 40000},
        ]
        
        self.db.save_portfolio(
            positions=default_positions,
            metadata={
                'cash_balance': 10000000.0,  # 1 Crore (10M)
                'total_invested': 187500.0,
                'strategy': 'MANUAL',
                'expected_return': 0.0,
                'expected_risk': 0.0,
                'sharpe_ratio': 0.0
            }
        )
        self.logger.info("Initialized default portfolio with popular stocks")
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get comprehensive portfolio summary with real calculations from SQLite.
        
        Returns:
            Dict with positions, values, and daily changes
        """
        # Get positions from database
        db_positions = self.db.get_positions()
        metadata = self.db.get_metadata()
        
        if not db_positions:
            self._initialize_default_portfolio()
            db_positions = self.db.get_positions()
            metadata = self.db.get_metadata()
        
        positions_data = []
        total_invested = 0.0
        current_value = 0.0
        
        # Get latest prices
        symbols = [pos['symbol'] for pos in db_positions]
        latest_prices = self.data_service.get_latest_prices(symbols)
        
        # Calculate yesterday's value for daily change
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_value = 0.0
        
        for position in db_positions:
            symbol = position['symbol']
            quantity = position['quantity']
            avg_buy_price = position['avg_buy_price']
            
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
        
        cash_balance = metadata.get('cash_balance', 0)
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
    
    def get_portfolio_performance(
        self, 
        timeframe: str = '3M',
        as_of_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get comprehensive portfolio performance with REAL historical data and metrics.
        
        Args:
            timeframe: "1M", "3M", "6M", or "1Y"
            as_of_date: Optional date to anchor the timeframe (default: latest available)
            
        Returns:
            Dict with time series data and comprehensive metrics
        """
        # Calculate days based on timeframe
        days_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
        days = days_map.get(timeframe, 90)
        
        # Set end date
        if as_of_date:
            end_date = as_of_date
        else:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=days)
        
        # Get positions and cash balance from database
        db_positions = self.db.get_positions()
        metadata = self.db.get_metadata()
        cash_balance = metadata.get('cash_balance', 0)
        
        if not db_positions:
            # Initialize if empty
            self._initialize_default_portfolio()
            db_positions = self.db.get_positions()
            metadata = self.db.get_metadata()
            cash_balance = metadata.get('cash_balance', 0)
        
        if not db_positions:
            self.logger.warning("No positions in portfolio")
            return {
                'timeframe': timeframe,
                'data': [],
                'metrics': {
                    'initial_value': cash_balance,
                    'final_value': cash_balance,
                    'total_return': 0.0,
                    'volatility': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0
                },
                'warnings': ['No positions in portfolio']
            }
        
        # Convert to dict format for compatibility
        positions = {}
        for pos in db_positions:
            positions[pos['symbol']] = {
                'quantity': pos['quantity'],
                'avg_buy_price': pos['avg_buy_price']
            }
        
        try:
            # Load price data for all symbols
            price_data = {}
            warnings = []
            
            for symbol in positions.keys():
                try:
                    df = self.data_service.get_ohlcv_data(
                        symbol, 
                        start_date=start_date,
                        end_date=end_date
                    )
                    if df.empty:
                        warnings.append(f"No data for {symbol} in timeframe")
                        continue
                    price_data[symbol] = df[['Date', 'Close']].set_index('Date')
                except Exception as e:
                    warnings.append(f"Error loading {symbol}: {str(e)}")
                    self.logger.error(f"Error loading {symbol}: {e}")
                    continue
            
            if not price_data:
                raise ValueError("No price data available for any symbols")
            
            # Combine all dates (inner join to only use dates where ALL symbols have data)
            all_dates = None
            for symbol, df in price_data.items():
                if all_dates is None:
                    all_dates = df.index
                else:
                    all_dates = all_dates.intersection(df.index)
            
            if len(all_dates) == 0:
                raise ValueError("No common trading dates found for all symbols")
            
            all_dates = sorted(all_dates)
            
            # Calculate daily portfolio values
            portfolio_values = []
            for date in all_dates:
                daily_value = cash_balance
                
                for symbol, position_info in positions.items():
                    if symbol in price_data:
                        quantity = position_info['quantity']
                        try:
                            price = float(price_data[symbol].loc[date, 'Close'])
                            daily_value += quantity * price
                        except KeyError:
                            continue
                
                portfolio_values.append(daily_value)
            
            # Convert to pandas Series for calculations
            portfolio_series = pd.Series(portfolio_values, index=all_dates)
            
            # Calculate metrics
            initial_value = portfolio_values[0]
            final_value = portfolio_values[-1]
            
            # Total return
            total_return = ((final_value / initial_value) - 1) * 100 if initial_value > 0 else 0.0
            
            # Daily returns
            daily_returns = portfolio_series.pct_change().dropna()
            
            # Annualized volatility
            volatility = float(daily_returns.std() * np.sqrt(252) * 100) if len(daily_returns) > 1 else 0.0
            
            # Sharpe ratio (risk-free rate = 0)
            if len(daily_returns) > 1 and daily_returns.std() > 0:
                sharpe_ratio = float((daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)))
            else:
                sharpe_ratio = 0.0
            
            # Maximum drawdown
            running_max = portfolio_series.expanding().max()
            drawdowns = (portfolio_series - running_max) / running_max
            max_drawdown = float(drawdowns.min() * 100) if len(drawdowns) > 0 else 0.0
            
            # Prepare time series data for response
            data = [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'value': round(float(value), 2)
                }
                for date, value in zip(all_dates, portfolio_values)
            ]
            
            # Compile metrics
            metrics = {
                'initial_value': round(float(initial_value), 2),
                'final_value': round(float(final_value), 2),
                'total_return': round(float(total_return), 2),
                'volatility': round(float(volatility), 2),
                'sharpe_ratio': round(float(sharpe_ratio), 2),
                'max_drawdown': round(float(max_drawdown), 2)
            }
            
            response = {
                'timeframe': timeframe,
                'data': data,
                'metrics': metrics
            }
            
            if warnings:
                response['warnings'] = warnings
            
            self.logger.info(f"Portfolio performance calculated for {timeframe}: {len(data)} data points")
            return response
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio performance: {e}", exc_info=True)
            raise
    
    # DEPRECATED METHODS - These methods used old self.portfolio dict structure
    # They are kept for backwards compatibility but should not be used
    # Use database methods instead (db.save_portfolio, db.get_positions, etc.)
    
    # def calculate_risk_metrics(self) -> Dict:
    #     """DEPRECATED: Calculate portfolio risk metrics."""
    #     pass
    
    # def add_position(self, symbol: str, quantity: int, price: float):
    #     """DEPRECATED: Add or update a position. Use db.save_portfolio instead."""
    #     pass
    
    # def remove_position(self, symbol: str, quantity: int):
    #     """DEPRECATED: Remove or reduce a position. Use db.save_portfolio instead."""
    #     pass


# Global instance
_portfolio_manager = None


def get_portfolio_manager() -> PortfolioManager:
    """Get or create global PortfolioManager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager
