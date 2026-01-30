"""Redis cache implementation"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

import redis.asyncio as redis

from app.core.exceptions import CacheException

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-based cache for scraped jobs with daily refresh strategy"""
    
    CACHE_KEY = "scraped_jobs"
    CACHE_DATE_KEY = "scraped_jobs_date"
    
    def __init__(self, redis_url: str, ttl_seconds: int = 3600):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds  # Fallback TTL
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✓ Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def get_jobs(self) -> Optional[List[Dict]]:
        """
        Get cached jobs if they're from today
        
        Returns:
            List of jobs if cache is valid, None otherwise
        """
        if not self.redis_client:
            return None
        
        try:
            # Check if cache is from today
            if not await self._is_cache_valid():
                logger.info("Cache expired (new day) - need to refresh")
                return None
            
            # Get cached jobs
            data = await self.redis_client.get(self.CACHE_KEY)
            if data:
                jobs = json.loads(data)
                cache_date = await self.redis_client.get(self.CACHE_DATE_KEY)
                logger.info(f"Cache hit: {len(jobs)} jobs from {cache_date}")
                return jobs
            return None
        except Exception as e:
            logger.error(f"Error getting cached jobs: {e}")
            return None
    
    async def set_jobs(self, jobs: List[Dict]):
        """
        Cache jobs with today's date
        Jobs will be valid until end of day (UTC)
        """
        if not self.redis_client:
            return
        
        try:
            now = datetime.now(timezone.utc)
            today = now.strftime("%Y-%m-%d")
            
            # Calculate seconds until end of day (UTC)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            seconds_until_eod = int((end_of_day - now).total_seconds())
            
            # Use at least 1 hour TTL as fallback
            ttl = max(seconds_until_eod, 3600)
            
            # Store jobs
            data = json.dumps(jobs)
            await self.redis_client.setex(
                self.CACHE_KEY,
                ttl,
                data
            )
            
            # Store cache date
            await self.redis_client.setex(
                self.CACHE_DATE_KEY,
                ttl,
                today
            )
            
            logger.info(f"Cached {len(jobs)} jobs for {today} (expires in {ttl}s)")
        except Exception as e:
            logger.error(f"Error caching jobs: {e}")
    
    async def _is_cache_valid(self) -> bool:
        """
        Check if cache is from today
        
        Returns:
            True if cache is from today, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            cache_date = await self.redis_client.get(self.CACHE_DATE_KEY)
            if not cache_date:
                return False
            
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            return cache_date == today
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    async def clear_cache(self):
        """Clear job cache"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(self.CACHE_KEY)
            await self.redis_client.delete(self.CACHE_DATE_KEY)
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    async def get_cache_info(self) -> Optional[Dict]:
        """
        Get cache information
        
        Returns:
            Dictionary with cache date and job count
        """
        if not self.redis_client:
            return None
        
        try:
            cache_date = await self.redis_client.get(self.CACHE_DATE_KEY)
            data = await self.redis_client.get(self.CACHE_KEY)
            
            if cache_date and data:
                jobs = json.loads(data)
                ttl = await self.redis_client.ttl(self.CACHE_KEY)
                
                return {
                    "cache_date": cache_date,
                    "job_count": len(jobs),
                    "ttl_seconds": ttl,
                    "is_valid": await self._is_cache_valid()
                }
            return None
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if cache is connected"""
        return self.redis_client is not None
