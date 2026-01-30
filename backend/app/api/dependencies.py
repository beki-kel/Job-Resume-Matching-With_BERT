"""Dependency injection for API routes"""
from typing import Optional
from fastapi import Depends

from app.infrastructure import ModelLoader, TelegramScraper, RedisCache
from app.infrastructure.llm import GeminiClient
from app.services import MatchingService, ScraperService
from app.services.resume_service import ResumeService


# Global instances (initialized in main.py)
_model_loader: Optional[ModelLoader] = None
_scraper: Optional[TelegramScraper] = None
_cache: Optional[RedisCache] = None
_gemini_client: Optional[GeminiClient] = None
_matching_service: Optional[MatchingService] = None
_scraper_service: Optional[ScraperService] = None
_resume_service: Optional[ResumeService] = None


def set_model_loader(model_loader: ModelLoader):
    """Set global model loader"""
    global _model_loader
    _model_loader = model_loader


def set_scraper(scraper: TelegramScraper):
    """Set global scraper"""
    global _scraper
    _scraper = scraper


def set_cache(cache: RedisCache):
    """Set global cache"""
    global _cache
    _cache = cache


def set_gemini_client(client: GeminiClient):
    """Set global Gemini client"""
    global _gemini_client
    _gemini_client = client


def set_matching_service(service: MatchingService):
    """Set global matching service"""
    global _matching_service
    _matching_service = service


def set_scraper_service(service: ScraperService):
    """Set global scraper service"""
    global _scraper_service
    _scraper_service = service


def set_resume_service(service: ResumeService):
    """Set global resume service"""
    global _resume_service
    _resume_service = service


def get_model_loader() -> ModelLoader:
    """Get model loader dependency"""
    if _model_loader is None:
        raise RuntimeError("Model loader not initialized")
    return _model_loader


def get_scraper() -> TelegramScraper:
    """Get scraper dependency"""
    if _scraper is None:
        raise RuntimeError("Scraper not initialized")
    return _scraper


def get_cache() -> Optional[RedisCache]:
    """Get cache dependency"""
    return _cache


def get_gemini_client() -> Optional[GeminiClient]:
    """Get Gemini client dependency"""
    return _gemini_client


def get_matching_service() -> MatchingService:
    """Get matching service dependency"""
    if _matching_service is None:
        raise RuntimeError("Matching service not initialized")
    return _matching_service


def get_scraper_service() -> ScraperService:
    """Get scraper service dependency"""
    if _scraper_service is None:
        raise RuntimeError("Scraper service not initialized")
    return _scraper_service


def get_resume_service() -> ResumeService:
    """Get resume service dependency"""
    if _resume_service is None:
        raise RuntimeError("Resume service not initialized")
    return _resume_service
