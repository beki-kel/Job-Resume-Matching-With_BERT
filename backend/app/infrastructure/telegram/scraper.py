"""Telegram scraper implementation"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError

from app.utils import clean_text

logger = logging.getLogger(__name__)


class TelegramScraper:
    """Scrapes job posts from Telegram channels"""
    
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        channels: List[str],
        session_name: str = "resume_matcher_session"
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.channels = channels
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
    
    async def connect(self):
        """Connect to Telegram"""
        try:
            self.client = TelegramClient(
                self.session_name,
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
        days_back: int = 7,
        min_text_length: int = 50
    ) -> List[Dict]:
        """
        Scrape job posts from a single channel
        
        Args:
            channel: Channel username (e.g., @ethiojobs)
            max_posts: Maximum posts to fetch
            days_back: Only fetch posts from last N days
            min_text_length: Minimum text length to consider
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            logger.info(f"Scraping {channel}...")
            
            entity = await self.client.get_entity(channel)
            date_limit = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            async for message in self.client.iter_messages(entity, limit=max_posts):
                if message.date < date_limit:
                    break
                
                if not message.text:
                    continue
                
                text = clean_text(message.text)
                
                if len(text) < min_text_length:
                    continue
                
                # Generate message link
                channel_username = channel.lstrip('@')
                message_link = f"https://t.me/{channel_username}/{message.id}"
                
                jobs.append({
                    'text': text,
                    'channel': channel,
                    'message_id': message.id,
                    'message_link': message_link,
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
    
    async def scrape_all_channels(
        self,
        max_posts: int = 100,
        sleep_between: float = 3.0,
        days_back: int = 7,
        min_text_length: int = 50
    ) -> List[Dict]:
        """
        Scrape jobs from all configured channels
        
        Args:
            max_posts: Max posts per channel
            sleep_between: Sleep seconds between channels
            days_back: Days to look back
            min_text_length: Minimum text length
        
        Returns:
            Combined list of all jobs
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        all_jobs = []
        
        for channel in self.channels:
            try:
                jobs = await self.scrape_channel(
                    channel, 
                    max_posts, 
                    days_back,
                    min_text_length
                )
                all_jobs.extend(jobs)
                
                if channel != self.channels[-1]:
                    await asyncio.sleep(sleep_between)
            
            except Exception as e:
                logger.error(f"Failed to scrape {channel}: {e}")
                continue
        
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
            fingerprint = job['text'][:200].lower().strip()
            
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                unique_jobs.append(job)
        
        logger.info(f"Deduplicated: {len(jobs)} -> {len(unique_jobs)}")
        return unique_jobs
    
    def is_connected(self) -> bool:
        """Check if scraper is connected"""
        return self.client is not None
