"""FastAPI application entry point"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core import settings
from app.infrastructure import ModelLoader, TelegramScraper, RedisCache
from app.infrastructure.llm import GeminiClient
from app.services import MatchingService, ScraperService
from app.services.resume_service import ResumeService
from app.api import dependencies
from app.api.routes import health, matching, resume

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting up Resume-Job Matcher API...")
    
    # Initialize model loader
    model_loader = ModelLoader(settings.MODEL_PATH)
    model_loader.load_model()
    dependencies.set_model_loader(model_loader)
    
    # Initialize Gemini client
    gemini_client = None
    if settings.GEMINI_API_KEY:
        try:
            gemini_client = GeminiClient(
                api_key=settings.GEMINI_API_KEY,
                model_name=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS
            )
            gemini_client.initialize()
            dependencies.set_gemini_client(gemini_client)
        except Exception as e:
            logger.warning(f"Gemini initialization failed: {e}")
            logger.warning("LLM features will be disabled")
    else:
        logger.warning("GEMINI_API_KEY not set - LLM features disabled")
    
    # Initialize scraper
    try:
        scraper = TelegramScraper(
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            phone=settings.TELEGRAM_PHONE,
            channels=settings.TELEGRAM_CHANNELS
        )
        await scraper.connect()
        dependencies.set_scraper(scraper)
        logger.info("✓ Telegram scraper initialized")
    except Exception as e:
        logger.error(f"Failed to initialize scraper: {e}")
        scraper = None
    
    # Initialize cache
    try:
        cache = RedisCache(
            redis_url=settings.REDIS_URL,
            ttl_seconds=settings.CACHE_TTL_SECONDS
        )
        await cache.connect()
        dependencies.set_cache(cache)
        logger.info("✓ Cache initialized")
    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        cache = None
    
    # Initialize services
    resume_service = None
    if gemini_client:
        resume_service = ResumeService(gemini_client)
        dependencies.set_resume_service(resume_service)
        logger.info("✓ Resume service initialized")
    
    matching_service = MatchingService(model_loader, resume_service)
    dependencies.set_matching_service(matching_service)
    
    scraper_service = ScraperService(scraper, cache)
    dependencies.set_scraper_service(scraper_service)
    
    logger.info("Startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if scraper:
        await scraper.disconnect()
    if cache:
        await cache.disconnect()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Match resumes with Telegram job posts using fine-tuned BERT and LLM enhancement",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = matching.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(health.router)
app.include_router(matching.router)
app.include_router(resume.router)


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
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
