"""
Configuration settings for the FastAPI backend
"""

import os
from typing import List

class Settings:
    # API Settings
    API_TITLE: str = "Powerlifting Meet Scraper API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for analyzing powerlifting meets using LiftingCast and OpenPowerlifting data"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173"
    ]
    
    # Data Settings
    CACHE_DIR: str = "data_cache"
    MAX_WORKERS: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Timeouts
    REQUEST_TIMEOUT: int = 30
    DRIVER_TIMEOUT: int = 10

settings = Settings() 