"""
Telegram scraper using Telethon
Scrapes job posts from public channels
"""
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError
from telethon.tl.types import Message

from config import settings
from utils import clean_text, is_job_related

logger = logging.getLogger(__name__)


class TelegramScraper:
    """Scrapes job posts from Telegram channels"""
    
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        channels: List[str]
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.channels = channels
        self.client: Optional[TelegramClient] = None
    
    async def connect(self):
        """Connect to Telegram"""
        try:
            self.client = TelegramClient(
                'resume_matcher_session',
                self.api_id,
                self.api_hash
            )
            await self.client.start(phone=self.phone)
            logger.info("✓ Connected to Telegram")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")
    
    async def scrape_channel(
        self,
        channel: str,
        max_posts: int = 100,
        days_back: int = 7
    ) -> List[Dict]:
        """
        Scrape job posts from a single channel
        
        Args:
            channel: Channel username (e.g., @ethiojobs)
            max_posts: Maximum posts to fetch
            days_back: Only fetch posts from last N days
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            logger.info(f"Scraping {channel}...")
            
            # Get channel entity
            entity = await self.client.get_entity(channel)
            
            # Calculate date limit (timezone-aware)
            from datetime import timezone
            date_limit = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            # Fetch messages
            async for message in self.client.iter_messages(
                entity,
                limit=max_posts
            ):
                # Check date
                if message.date < date_limit:
                    break
                
                # Skip non-text messages
                if not message.text:
                    continue
                
                # Clean text
                text = clean_text(message.text)
                
                # Filter job-related posts
                if not is_job_related(text, settings.JOB_KEYWORDS):
                    continue
                
                # Skip very short posts
                if len(text) < 50:
                    continue
                
                jobs.append({
                    'text': text,
                    'channel': channel,
                    'message_id': message.id,
                    'date': message.date.isoformat(),
                    'scraped_at': datetime.utcnow().isoformat()
                })
            
            logger.info(f"✓ Found {len(jobs)} jobs in {channel}")
        
        except ChannelPrivateError:
            logger.warning(f"Channel {channel} is private or doesn't exist")
        except FloodWaitError as e:
            logger.warning(f"Rate limited on {channel}, wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Error scraping {channel}: {e}")
        
        return jobs
    
    async def scrape_jobs(
        self,
        max_posts: int = 100,
        sleep_between: float = 3.0
    ) -> List[Dict]:
        """
        Scrape jobs from all configured channels
        
        Args:
            max_posts: Max posts per channel
            sleep_between: Sleep seconds between channels
        
        Returns:
            Combined list of all jobs
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        all_jobs = []
        
        for channel in self.channels:
            try:
                jobs = await self.scrape_channel(channel, max_posts)
                all_jobs.extend(jobs)
                
                # Sleep between channels to avoid rate limits
                if channel != self.channels[-1]:
                    await asyncio.sleep(sleep_between)
            
            except Exception as e:
                logger.error(f"Failed to scrape {channel}: {e}")
                continue
        
        # Remove duplicates based on text similarity
        all_jobs = self._deduplicate_jobs(all_jobs)
        
        logger.info(f"Total jobs scraped: {len(all_jobs)}")
        return all_jobs
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on text similarity"""
        if not jobs:
            return []
        
        unique_jobs = []
        seen_texts = set()
        
        for job in jobs:
            # Use first 200 chars as fingerprint
            fingerprint = job['text'][:200].lower().strip()
            
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                unique_jobs.append(job)
        
        logger.info(f"Deduplicated: {len(jobs)} -> {len(unique_jobs)}")
        return unique_jobs
