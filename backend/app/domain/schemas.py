"""Request and Response schemas"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeRequest(BaseModel):
    """Resume matching request"""
    resume_text: str = Field(..., min_length=50, max_length=10000, description="User resume text")
    threshold: Optional[float] = Field(0.6, ge=0.0, le=1.0, description="Minimum match score")
    max_results: Optional[int] = Field(20, ge=1, le=100, description="Maximum results to return")
    generate_explanations: Optional[bool] = Field(False, description="Generate LLM explanations for matches")


class ResumeProcessRequest(BaseModel):
    """Resume processing request"""
    resume_text: str = Field(..., min_length=50, max_length=20000, description="Raw resume text")


class ResumeProcessResponse(BaseModel):
    """Resume processing response"""
    processed_resume: str
    cleaned_for_matching: str
    score: int
    strengths: List[str]
    improvements: List[str]
    key_skills: List[str]
    experience_years: str


class JobMatch(BaseModel):
    """Job match result"""
    job_text: str
    score: float
    source_channel: str
    title: str
    scraped_at: str
    message_link: str = Field(..., description="Direct link to the Telegram message")
    explanation: Optional[str] = None  # LLM-generated explanation


class MatchResponse(BaseModel):
    """Match response"""
    matches: List[JobMatch]
    total_jobs_scraped: int
    total_matches: int
    processing_time_seconds: float
    resume_analysis: Optional[ResumeProcessResponse] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    scraper_ready: bool
    cache_ready: bool
    llm_ready: bool
    timestamp: str


class RefreshResponse(BaseModel):
    """Refresh jobs response"""
    status: str
    jobs_scraped: int
    timestamp: str
