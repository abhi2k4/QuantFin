"""
Portfolio Database Manager
SQLite database for tracking portfolio history, allocations, and performance
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PortfolioDB:
    """Manages portfolio data persistence using SQLite"""
    
    def __init__(self, db_path: str = "portfolio.db"):
        self.db_path = Path(__file__).parent.parent.parent / "data" / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path), check_same_thread=False)
    
    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Portfolio History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_value REAL,
                cash_balance REAL,
                invested_value REAL,
                total_gain_loss REAL,
                total_gain_loss_percent REAL,
                strategy TEXT,
                metadata TEXT
            )
        """)
        
        # Portfolio Allocations Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_history_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                weight_percent REAL,
                allocation_amount REAL,
                quantity INTEGER,
                buy_price REAL,
                predicted_price REAL,
                predicted_return REAL,
                confidence REAL,
                strategy TEXT,
                FOREIGN KEY (portfolio_history_id) REFERENCES portfolio_history(id)
            )
        """)
        
        # Portfolio Positions Table (Current Holdings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE,
                quantity INTEGER,
                avg_buy_price REAL,
                total_invested REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Rebalance History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rebalance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                strategy TEXT,
                capital_allocation REAL,
                stocks_added INTEGER,
                stocks_removed INTEGER,
                total_stocks INTEGER,
                expected_return REAL,
                expected_risk REAL,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Portfolio database initialized at {self.db_path}")
    
    def save_portfolio_snapshot(self, portfolio_data: Dict[str, Any]) -> int:
        """Save portfolio snapshot to history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO portfolio_history 
            (total_value, cash_balance, invested_value, total_gain_loss, 
             total_gain_loss_percent, strategy, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            portfolio_data.get('total_value', 0),
            portfolio_data.get('cash_balance', 0),
            portfolio_data.get('invested_value', 0),
            portfolio_data.get('total_gain_loss', 0),
            portfolio_data.get('total_gain_loss_percent', 0),
            portfolio_data.get('strategy', ''),
            json.dumps(portfolio_data.get('metadata', {}))
        ))
        
        portfolio_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return portfolio_id
    
    def save_allocations(self, portfolio_id: int, allocations: List[Dict[str, Any]], strategy: str):
        """Save allocation decisions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for alloc in allocations:
            cursor.execute("""
                INSERT INTO portfolio_allocations
                (portfolio_history_id, symbol, weight_percent, allocation_amount,
                 quantity, buy_price, predicted_price, predicted_return, confidence, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                portfolio_id,
                alloc.get('symbol', ''),
                alloc.get('weight_percent', 0),
                alloc.get('allocation_amount', 0),
                alloc.get('quantity', 0),
                alloc.get('buy_price', 0),
                alloc.get('predicted_price', 0),
                alloc.get('predicted_return', 0),
                alloc.get('confidence', 0),
                strategy
            ))
        
        conn.commit()
        conn.close()
    
    def update_position(self, symbol: str, quantity: int, avg_buy_price: float, total_invested: float):
        """Update or insert position"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO portfolio_positions (symbol, quantity, avg_buy_price, total_invested, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(symbol) DO UPDATE SET
                quantity = quantity + excluded.quantity,
                avg_buy_price = ((avg_buy_price * quantity) + (excluded.avg_buy_price * excluded.quantity)) / (quantity + excluded.quantity),
                total_invested = total_invested + excluded.total_invested,
                last_updated = CURRENT_TIMESTAMP
        """, (symbol, quantity, avg_buy_price, total_invested))
        
        conn.commit()
        conn.close()
    
    def get_current_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, quantity, avg_buy_price, total_invested, last_updated
            FROM portfolio_positions
            WHERE quantity > 0
        """)
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'symbol': row[0],
                'quantity': row[1],
                'avg_buy_price': row[2],
                'total_invested': row[3],
                'last_updated': row[4]
            })
        
        conn.close()
        return positions
    
    def save_rebalance_event(self, rebalance_data: Dict[str, Any]) -> int:
        """Save rebalance event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rebalance_history
            (strategy, capital_allocation, stocks_added, stocks_removed, 
             total_stocks, expected_return, expected_risk, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rebalance_data.get('strategy', ''),
            rebalance_data.get('capital_allocation', 0),
            rebalance_data.get('stocks_added', 0),
            rebalance_data.get('stocks_removed', 0),
            rebalance_data.get('total_stocks', 0),
            rebalance_data.get('expected_return', 0),
            rebalance_data.get('expected_risk', 0),
            json.dumps(rebalance_data.get('metadata', {}))
        ))
        
        rebalance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rebalance_id
    
    def get_portfolio_history(self, days: int = 365) -> List[Dict[str, Any]]:
        """Get portfolio history for specified days"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, total_value, cash_balance, invested_value,
                   total_gain_loss, total_gain_loss_percent, strategy
            FROM portfolio_history
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp ASC
        """, (days,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'timestamp': row[0],
                'total_value': row[1],
                'cash_balance': row[2],
                'invested_value': row[3],
                'total_gain_loss': row[4],
                'total_gain_loss_percent': row[5],
                'strategy': row[6]
            })
        
        conn.close()
        return history
    
    def get_allocation_history(self, strategy: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent allocation decisions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT symbol, weight_percent, allocation_amount, quantity,
                   buy_price, predicted_price, predicted_return, confidence,
                   strategy, timestamp
            FROM portfolio_allocations
        """
        
        params = []
        if strategy:
            query += " WHERE strategy = ?"
            params.append(strategy)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        allocations = []
        for row in cursor.fetchall():
            allocations.append({
                'symbol': row[0],
                'weight_percent': row[1],
                'allocation_amount': row[2],
                'quantity': row[3],
                'buy_price': row[4],
                'predicted_price': row[5],
                'predicted_return': row[6],
                'confidence': row[7],
                'strategy': row[8],
                'timestamp': row[9]
            })
        
        conn.close()
        return allocations


# Singleton instance
_portfolio_db = None

def get_portfolio_db() -> PortfolioDB:
    """Get portfolio database singleton"""
    global _portfolio_db
    if _portfolio_db is None:
        _portfolio_db = PortfolioDB()
    return _portfolio_db
