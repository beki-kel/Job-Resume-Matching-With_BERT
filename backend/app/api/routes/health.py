"""Health check routes"""
from datetime import datetime
from fastapi import APIRouter, Depends
from typing import Optional

from app.domain.schemas import HealthResponse
from app.api.dependencies import get_model_loader, get_scraper, get_cache, get_gemini_client
from app.infrastructure import ModelLoader, TelegramScraper, RedisCache
from app.infrastructure.llm import GeminiClient

router = APIRouter(tags=["Health"])


@router.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Resume-Job Matcher API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check(
    model_loader: ModelLoader = Depends(get_model_loader),
    scraper: TelegramScraper = Depends(get_scraper),
    cache: RedisCache = Depends(get_cache),
    gemini: GeminiClient = Depends(get_gemini_client)
):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model_loader.is_loaded() and scraper.is_connected() else "degraded",
        model_loaded=model_loader.is_loaded(),
        scraper_ready=scraper.is_connected(),
        cache_ready=cache.is_connected() if cache else False,
        llm_ready=gemini.is_initialized() if gemini else False,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/cache/info")
async def cache_info(cache: RedisCache = Depends(get_cache)):
    """
    Get cache information
    
    Returns cache date, job count, and validity status
    """
    if not cache or not cache.is_connected():
        return {
            "status": "unavailable",
            "message": "Cache not connected"
        }
    
    info = await cache.get_cache_info()
    
    if not info:
        return {
            "status": "empty",
            "message": "No cached jobs"
        }
    
    return {
        "status": "active",
        "cache_date": info["cache_date"],
        "job_count": info["job_count"],
        "ttl_seconds": info["ttl_seconds"],
        "is_valid": info["is_valid"],
        "message": f"Cache from {info['cache_date']} with {info['job_count']} jobs"
    }
