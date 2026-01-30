"""Domain models"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    """Job posting domain model"""
    text: str
    channel: str
    message_id: int
    message_link: str
    date: str
    scraped_at: str


@dataclass
class MatchResult:
    """Match result domain model"""
    job_text: str
    score: float
    source_channel: str
    title: str
    scraped_at: str
    message_link: str
    explanation: Optional[str] = None
