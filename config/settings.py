"""Configuration settings for GoalPredictor.AI."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "GoalPredictor.AI"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # API Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./goalpredictor.db"
    
    # Redis
    redis_url: Optional[str] = None
    
    # Football Data API
    football_api_key: Optional[str] = None
    football_api_base_url: str = "https://api.football-data.org/v4"
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Subscription
    free_tier_daily_limit: int = 3
    premium_monthly_price_eur: float = 7.99
    
    # AI Model
    model_version: str = "1.0.0"
    min_confidence_threshold: float = 0.5
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
