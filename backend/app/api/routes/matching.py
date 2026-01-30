"""Matching routes"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.domain.schemas import ResumeRequest, MatchResponse, JobMatch, RefreshResponse
from app.services import MatchingService, ScraperService
from app.api.dependencies import get_matching_service, get_scraper_service
from app.core import settings, NoJobsFoundException

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Matching"])


@router.post("/match_resume", response_model=MatchResponse)
@limiter.limit(settings.RATE_LIMIT_MATCH)
async def match_resume(
    request: Request,
    resume_req: ResumeRequest,
    matching_service: MatchingService = Depends(get_matching_service),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """
    Match resume with scraped Telegram job posts
    
    - Scrapes recent jobs from configured Telegram channels
    - Runs inference with fine-tuned model
    - Returns ranked matches above threshold
    """
    start_time = datetime.utcnow()
    
    try:
        # Get jobs (from cache or scrape)
        jobs = await scraper_service.get_jobs(
            max_posts=settings.MAX_POSTS_PER_CHANNEL,
            sleep_between=settings.SCRAPE_SLEEP_SECONDS,
            days_back=settings.SCRAPE_DAYS_BACK,
            min_text_length=settings.MIN_JOB_TEXT_LENGTH
        )
        
        # Match resume with jobs
        matches = matching_service.match_resume_with_jobs(
            resume_text=resume_req.resume_text,
            jobs=jobs,
            threshold=resume_req.threshold,
            max_results=resume_req.max_results,
            generate_explanations=resume_req.generate_explanations
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Found {len(matches)} matches in {processing_time:.2f}s")
        
        return MatchResponse(
            matches=[
                JobMatch(
                    job_text=m.job_text,
                    score=m.score,
                    source_channel=m.source_channel,
                    title=m.title,
                    scraped_at=m.scraped_at,
                    message_link=m.message_link,
                    explanation=m.explanation
                ) for m in matches
            ],
            total_jobs_scraped=len(jobs),
            total_matches=len(matches),
            processing_time_seconds=round(processing_time, 2)
        )
    
    except NoJobsFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in match_resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/refresh_jobs", response_model=RefreshResponse)
@limiter.limit(settings.RATE_LIMIT_REFRESH)
async def refresh_jobs(
    request: Request,
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """
    Force refresh job cache by scraping new jobs
    (Admin endpoint - rate limited)
    """
    try:
        logger.info("Force refreshing jobs...")
        jobs = await scraper_service.refresh_jobs(
            max_posts=settings.MAX_POSTS_PER_CHANNEL,
            sleep_between=settings.SCRAPE_SLEEP_SECONDS
        )
        
        return RefreshResponse(
            status="success",
            jobs_scraped=len(jobs),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error refreshing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
