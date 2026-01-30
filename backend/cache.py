"""
Redis cache for scraped jobs
"""
import json
import logging
from typing import List, Dict, Optional

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class JobCache:
    """Redis-based cache for scraped jobs"""
    
    CACHE_KEY = "scraped_jobs"
    
    def __init__(self, redis_url: str, ttl_seconds: int = 3600):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
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
        """Get cached jobs"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(self.CACHE_KEY)
            if data:
                jobs = json.loads(data)
                logger.info(f"Cache hit: {len(jobs)} jobs")
                return jobs
            return None
        except Exception as e:
            logger.error(f"Error getting cached jobs: {e}")
            return None
    
    async def set_jobs(self, jobs: List[Dict]):
        """Cache jobs with TTL"""
        if not self.redis_client:
            return
        
        try:
            data = json.dumps(jobs)
            await self.redis_client.setex(
                self.CACHE_KEY,
                self.ttl_seconds,
                data
            )
            logger.info(f"Cached {len(jobs)} jobs (TTL: {self.ttl_seconds}s)")
        except Exception as e:
            logger.error(f"Error caching jobs: {e}")
    
    async def clear_cache(self):
        """Clear job cache"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(self.CACHE_KEY)
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
