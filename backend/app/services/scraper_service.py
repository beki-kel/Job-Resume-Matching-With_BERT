"""Scraper service - business logic for job scraping"""
import logging
from typing import List, Dict, Optional

from app.infrastructure.telegram import TelegramScraper
from app.infrastructure.cache import RedisCache
from app.core.exceptions import NoJobsFoundException

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping and caching jobs"""
    
    def __init__(
        self,
        scraper: TelegramScraper,
        cache: Optional[RedisCache] = None
    ):
        self.scraper = scraper
        self.cache = cache
    
    async def get_jobs(
        self,
        max_posts: int = 100,
        sleep_between: float = 3.0,
        days_back: int = 7,
        min_text_length: int = 50,
        force_refresh: bool = False
    ) -> List[Dict]:
        """
        Get jobs from cache or scrape new ones
        
        Args:
            max_posts: Max posts per channel
            sleep_between: Sleep between channels
            days_back: Days to look back
            min_text_length: Minimum text length
            force_refresh: Force refresh cache
        
        Returns:
            List of job dictionaries
        """
        # Try cache first if not forcing refresh
        if not force_refresh and self.cache:
            cached_jobs = await self.cache.get_jobs()
            if cached_jobs:
                logger.info(f"Using {len(cached_jobs)} cached jobs")
                return cached_jobs
        
        # Scrape new jobs
        logger.info("Scraping new jobs...")
        jobs = await self.scraper.scrape_all_channels(
            max_posts=max_posts,
            sleep_between=sleep_between,
            days_back=days_back,
            min_text_length=min_text_length
        )
        
        if not jobs:
            raise NoJobsFoundException("No jobs found in configured channels")
        
        # Cache jobs
        if self.cache:
            await self.cache.set_jobs(jobs)
        
        logger.info(f"Scraped {len(jobs)} jobs")
        return jobs
    
    async def refresh_jobs(
        self,
        max_posts: int = 100,
        sleep_between: float = 3.0
    ) -> List[Dict]:
        """Force refresh jobs"""
        return await self.get_jobs(
            max_posts=max_posts,
            sleep_between=sleep_between,
            force_refresh=True
        )
