"""
Configuration management using Pydantic Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "Resume-Job Matcher API"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["*"]
    
    # Model Settings
    MODEL_PATH: str = "./fine_tuned_bert"  # Local path or HF hub
    
    # Telegram Settings
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE: str
    TELEGRAM_CHANNELS: List[str] = [
        "@ethiojobs",
        "@jobs_in_ethiopia",
        "@ethiopianjobs",
        "@addisababa_jobs"
    ]
    
    # Scraping Settings
    MAX_POSTS_PER_CHANNEL: int = 100
    SCRAPE_SLEEP_SECONDS: float = 3.0
    JOB_KEYWORDS: List[str] = [
        "vacancy", "job", "hiring", "position", "opening",
        "career", "opportunity", "recruit", "apply", "wanted"
    ]
    
    # Cache Settings
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    
    # Inference Settings
    DEFAULT_THRESHOLD: float = 0.6
    MAX_RESULTS: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
