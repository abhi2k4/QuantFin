from functools import lru_cache
from typing import Optional

class Settings:
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = None
    twelve_data_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./quantfin.db"
    
    # ML Models
    models_path: str = "ml_models/"
    data_path: str = "data/"
    
    # Trading
    default_portfolio_value: float = 100000.0
    
    # News Analysis
    max_news_articles: int = 50

@lru_cache()
def get_settings():
    return Settings()