"""
Configuration management for ArtifexAI Backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "ArtifexAI API"
    app_version: str = "7.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000"
    ]
    
    # Database
    database_url: str = "sqlite:///data/artist_database.db"
    
    # Model
    model_path: str = "../../art_auction_project/artifacts/art_price_model.pkl"
    preprocessor_path: str = "../../art_auction_project/artifacts/preprocessor.pkl"
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    
    # Image Processing
    image_resize_size: tuple = (64, 64)
    
    # Business Logic
    current_year: int = 2024
    default_artist_frequency: int = 1
    default_artist_median_price: float = 500.0
    default_artist_price_std: float = 250.0
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
