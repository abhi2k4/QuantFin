"""
Portfolio Database Manager - SQLite storage for portfolio positions

Stores and retrieves portfolio allocations from SQLite database
to persist real ML-driven portfolio recommendations.

Author: QuantFin Team
Date: 2025-10-30
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class PortfolioDatabase:
    """Manages portfolio data in SQLite database."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent.parent / "data" / "portfolio.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolio positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                allocation_amount REAL NOT NULL,
                predicted_return REAL,
                confidence REAL,
                strategy TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Portfolio metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                cash_balance REAL NOT NULL,
                total_invested REAL NOT NULL,
                strategy TEXT,
                expected_return REAL,
                expected_risk REAL,
                sharpe_ratio REAL,
                last_rebalance TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Performance tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                portfolio_value REAL NOT NULL,
                predicted_value REAL,
                nifty50_value REAL,
                strategy TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_portfolio(self, positions: List[Dict], metadata: Dict):
        """Save portfolio positions and metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing positions
            cursor.execute('DELETE FROM positions')
            
            # Insert new positions
            now = datetime.now().isoformat()
            for pos in positions:
                cursor.execute('''
                    INSERT INTO positions 
                    (symbol, quantity, buy_price, allocation_amount, predicted_return, 
                     confidence, strategy, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pos['symbol'],
                    pos['quantity'],
                    pos['buy_price'],
                    pos['allocation_amount'],
                    pos.get('predicted_return', 0),
                    pos.get('confidence', 0),
                    metadata.get('strategy', 'UNKNOWN'),
                    now,
                    now
                ))
            
            # Update metadata
            cursor.execute('DELETE FROM portfolio_metadata')
            cursor.execute('''
                INSERT INTO portfolio_metadata
                (id, cash_balance, total_invested, strategy, expected_return, 
                 expected_risk, sharpe_ratio, last_rebalance, created_at, updated_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.get('cash_balance', 0),
                metadata.get('total_invested', 0),
                metadata.get('strategy', 'UNKNOWN'),
                metadata.get('expected_return', 0),
                metadata.get('expected_risk', 0),
                metadata.get('sharpe_ratio', 0),
                now,
                now,
                now
            ))
            
            conn.commit()
            logger.info(f"Saved {len(positions)} positions to database")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save portfolio: {e}")
            raise
        finally:
            conn.close()
    
    def get_positions(self) -> List[Dict]:
        """Get all current portfolio positions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, quantity, buy_price, allocation_amount, 
                   predicted_return, confidence, strategy
            FROM positions
            ORDER BY allocation_amount DESC
        ''')
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'symbol': row[0],
                'quantity': row[1],
                'avg_buy_price': row[2],
                'allocation_amount': row[3],
                'predicted_return': row[4],
                'confidence': row[5],
                'strategy': row[6]
            })
        
        conn.close()
        return positions
    
    def get_metadata(self) -> Dict:
        """Get portfolio metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cash_balance, total_invested, strategy, expected_return,
                   expected_risk, sharpe_ratio, last_rebalance
            FROM portfolio_metadata
            WHERE id = 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'cash_balance': row[0],
                'total_invested': row[1],
                'strategy': row[2],
                'expected_return': row[3],
                'expected_risk': row[4],
                'sharpe_ratio': row[5],
                'last_rebalance': row[6]
            }
        else:
            # Return default if no metadata exists
            return {
                'cash_balance': 10000000.0,  # 1 Crore (10M)
                'total_invested': 0.0,
                'strategy': 'LINEAR',
                'expected_return': 0.0,
                'expected_risk': 0.0,
                'sharpe_ratio': 0.0,
                'last_rebalance': None
            }
    
    def save_performance_snapshot(self, portfolio_value: float, predicted_value: float, 
                                   nifty50_value: float, strategy: str):
        """Save daily performance snapshot for tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        now = datetime.now().isoformat()
        
        # Check if today's snapshot already exists
        cursor.execute('SELECT id FROM performance_history WHERE date = ?', (today,))
        if cursor.fetchone():
            # Update existing
            cursor.execute('''
                UPDATE performance_history
                SET portfolio_value = ?, predicted_value = ?, nifty50_value = ?, strategy = ?
                WHERE date = ?
            ''', (portfolio_value, predicted_value, nifty50_value, strategy, today))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO performance_history
                (date, portfolio_value, predicted_value, nifty50_value, strategy, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (today, portfolio_value, predicted_value, nifty50_value, strategy, now))
        
        conn.commit()
        conn.close()
    
    def get_performance_history(self, days: int = 90) -> List[Dict]:
        """Get performance history for the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, portfolio_value, predicted_value, nifty50_value, strategy
            FROM performance_history
            ORDER BY date DESC
            LIMIT ?
        ''', (days,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'date': row[0],
                'portfolio_value': row[1],
                'predicted_value': row[2],
                'nifty50_value': row[3],
                'strategy': row[4]
            })
        
        conn.close()
        return list(reversed(history))  # Return oldest first


# Singleton instance
_portfolio_db = None

def get_portfolio_db() -> PortfolioDatabase:
    """Get singleton portfolio database instance."""
    global _portfolio_db
    if _portfolio_db is None:
        _portfolio_db = PortfolioDatabase()
    return _portfolio_db
