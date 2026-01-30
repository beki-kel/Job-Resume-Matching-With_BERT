"""
FastAPI Backend for Resume-Job Matcher
Scrapes Telegram job channels and matches resumes using fine-tuned BERT model
"""
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from config import settings
from scraper import TelegramScraper
from cache import JobCache
from utils import clean_text, extract_job_title, format_input_pair

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# FastAPI app
app = FastAPI(
    title="Resume-Job Matcher API",
    description="Match resumes with Telegram job posts using fine-tuned BERT",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global state
model = None
tokenizer = None
device = None
scraper = None
cache = None


# Pydantic models
class ResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=10000, description="User resume text")
    threshold: Optional[float] = Field(0.6, ge=0.0, le=1.0, description="Minimum match score")
    max_results: Optional[int] = Field(20, ge=1, le=100, description="Maximum results to return")


class JobMatch(BaseModel):
    job_text: str
    score: float
    source_channel: str
    title: str
    scraped_at: str


class MatchResponse(BaseModel):
    matches: List[JobMatch]
    total_jobs_scraped: int
    total_matches: int
    processing_time_seconds: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    scraper_ready: bool
    cache_ready: bool
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize model, scraper, and cache on startup"""
    global model, tokenizer, device, scraper, cache
    
    logger.info("Starting up Resume-Job Matcher API...")
    
    # Device setup
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
    logger.info(f"Using device: {device}")
    
    # Load model - Try Sentence Transformer first, then fall back to classification model
    try:
        logger.info(f"Loading model from: {settings.MODEL_PATH}")
        
        # Check if it's a Sentence Transformer model
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(settings.MODEL_PATH, device=str(device))
            tokenizer = None  # Not needed for Sentence Transformers
            logger.info("✓ Loaded as Sentence Transformer model")
        except:
            # Fall back to classification model
            tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_PATH)
            model = AutoModelForSequenceClassification.from_pretrained(
                settings.MODEL_PATH,
                num_labels=1,
                problem_type='regression'
            )
            model.to(device)
            model.eval()
            logger.info("✓ Loaded as classification model")
        logger.info("✓ Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")
    
    # Initialize scraper
    try:
        scraper = TelegramScraper(
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            phone=settings.TELEGRAM_PHONE,
            channels=settings.TELEGRAM_CHANNELS
        )
        await scraper.connect()
        logger.info("✓ Telegram scraper initialized")
    except Exception as e:
        logger.error(f"Failed to initialize scraper: {e}")
        scraper = None
    
    # Initialize cache
    try:
        cache = JobCache(
            redis_url=settings.REDIS_URL,
            ttl_seconds=settings.CACHE_TTL_SECONDS
        )
        await cache.connect()
        logger.info("✓ Cache initialized")
    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        cache = None
    
    logger.info("Startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    if scraper:
        await scraper.disconnect()
    if cache:
        await cache.disconnect()
    logger.info("Shutdown complete")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Resume-Job Matcher API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model and scraper else "degraded",
        model_loaded=model is not None,
        scraper_ready=scraper is not None,
        cache_ready=cache is not None,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/match_resume", response_model=MatchResponse, tags=["Matching"])
@limiter.limit("10/minute")
async def match_resume(request: Request, resume_req: ResumeRequest):
    """
    Match resume with scraped Telegram job posts
    
    - Scrapes recent jobs from configured Telegram channels
    - Runs inference with fine-tuned model
    - Returns ranked matches above threshold
    """
    start_time = datetime.utcnow()
    
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not scraper:
        raise HTTPException(status_code=503, detail="Scraper not available")
    
    try:
        # Get cached jobs or scrape new ones
        jobs = await cache.get_jobs() if cache else None
        
        if not jobs:
            logger.info("Cache miss - scraping new jobs...")
            jobs = await scraper.scrape_jobs(
                max_posts=settings.MAX_POSTS_PER_CHANNEL,
                sleep_between=settings.SCRAPE_SLEEP_SECONDS
            )
            
            if not jobs:
                raise HTTPException(
                    status_code=404,
                    detail="No jobs found in configured channels"
                )
            
            # Cache jobs
            if cache:
                await cache.set_jobs(jobs)
            
            logger.info(f"Scraped {len(jobs)} jobs")
        else:
            logger.info(f"Using {len(jobs)} cached jobs")
        
        # Run inference
        matches = []
        resume_clean = clean_text(resume_req.resume_text)
        
        # Check if model is Sentence Transformer
        is_sentence_transformer = hasattr(model, 'encode')
        
        if is_sentence_transformer:
            # Sentence Transformer inference (cosine similarity)
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            # Encode resume once
            resume_embedding = model.encode([resume_clean])
            
            for job in jobs:
                try:
                    # Encode job
                    job_embedding = model.encode([job['text']])
                    
                    # Compute cosine similarity
                    score = cosine_similarity(resume_embedding, job_embedding)[0][0]
                    score = float(score)
                    score = max(0.0, min(1.0, score))  # Clip to [0, 1]
                    
                    # Filter by threshold
                    if score >= resume_req.threshold:
                        matches.append({
                            'job_text': job['text'],
                            'score': score,
                            'source_channel': job['channel'],
                            'title': extract_job_title(job['text']),
                            'scraped_at': job['scraped_at']
                        })
                
                except Exception as e:
                    logger.warning(f"Error processing job: {e}")
                    continue
        else:
            # Classification model inference
            for job in jobs:
                try:
                    # Format input pair in dataset style
                    input_text = format_input_pair(job['text'], resume_clean)
                    
                    # Tokenize
                    inputs = tokenizer(
                        input_text,
                        padding='max_length',
                        truncation=True,
                        max_length=512,
                        return_tensors='pt'
                    )
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    
                    # Inference
                    with torch.no_grad():
                        outputs = model(**inputs)
                        score = torch.sigmoid(outputs.logits).item()
                        score = max(0.0, min(1.0, score))  # Clip to [0, 1]
                    
                    # Filter by threshold
                    if score >= resume_req.threshold:
                        matches.append({
                            'job_text': job['text'],
                            'score': score,
                            'source_channel': job['channel'],
                            'title': extract_job_title(job['text']),
                            'scraped_at': job['scraped_at']
                        })
                
                except Exception as e:
                    logger.warning(f"Error processing job: {e}")
                    continue
        
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit results
        matches = matches[:resume_req.max_results]
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Found {len(matches)} matches in {processing_time:.2f}s")
        
        return MatchResponse(
            matches=[JobMatch(**m) for m in matches],
            total_jobs_scraped=len(jobs),
            total_matches=len(matches),
            processing_time_seconds=round(processing_time, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in match_resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/refresh_jobs", tags=["Admin"])
@limiter.limit("2/hour")
async def refresh_jobs(request: Request):
    """
    Force refresh job cache by scraping new jobs
    (Admin endpoint - rate limited)
    """
    if not scraper:
        raise HTTPException(status_code=503, detail="Scraper not available")
    
    try:
        logger.info("Force refreshing jobs...")
        jobs = await scraper.scrape_jobs(
            max_posts=settings.MAX_POSTS_PER_CHANNEL,
            sleep_between=settings.SCRAPE_SLEEP_SECONDS
        )
        
        if cache:
            await cache.set_jobs(jobs)
        
        return {
            "status": "success",
            "jobs_scraped": len(jobs),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error refreshing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
