"""Configuration management using Pydantic Settings"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "Resume-Job Matcher API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["*"]
    
    # Model Settings
    MODEL_PATH: str = "./fine_tuned_bert"
    
    # LLM Settings (Gemini)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    
    # Telegram Settings
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE: str
    TELEGRAM_CHANNELS: List[str] = [
        "@ethiojobs",
        "@jobs_in_ethiopia",
    ]
    
    # Scraping Settings
    MAX_POSTS_PER_CHANNEL: int = 200
    SCRAPE_SLEEP_SECONDS: float = 3.0
    SCRAPE_DAYS_BACK: int = 2
    MIN_JOB_TEXT_LENGTH: int = 50
    
    # Cache Settings
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 3600  # Fallback TTL (cache uses daily refresh strategy)
    
    # Inference Settings
    DEFAULT_THRESHOLD: float = 0.6
    MAX_RESULTS: int = 20
    
    # Rate Limiting
    RATE_LIMIT_MATCH: str = "10/minute"
    RATE_LIMIT_REFRESH: str = "2/hour"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
