"""
Application Settings and Configuration
This module handles all environment-based configurations using Pydantic V2
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Info
    app_name: str = "URL Shortener"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "url_shortener"
    mongodb_username: str = "admin"
    mongodb_password: str = "password"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    # Monitoring
    prometheus_port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    This ensures we only load settings once from environment
    """
    return Settings()
