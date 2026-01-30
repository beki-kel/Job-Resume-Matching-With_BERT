# Project Structure

Complete overview of the Resume-Job Matcher API codebase.

## Directory Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management (Pydantic Settings)
├── scraper.py             # Telegram scraper (Telethon)
├── cache.py               # Redis cache implementation
├── utils.py               # Utility functions (text processing, formatting)
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Multi-container orchestration
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── setup.sh             # Automated setup script
├── test_api.py          # API test suite
├── example_client.py    # Example client implementation
├── README.md            # Main documentation
├── DEPLOYMENT.md        # Deployment guide
└── PROJECT_STRUCTURE.md # This file
```

## Core Components

### 1. main.py

**Purpose:** FastAPI application with all endpoints and business logic

**Key Features:**
- Async endpoints for performance
- Rate limiting (slowapi)
- CORS middleware
- Global exception handling
- Model loading and inference
- Health checks

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /match_resume` - Main matching endpoint
- `POST /refresh_jobs` - Force cache refresh (admin)

**Startup/Shutdown:**
- Loads model on startup
- Initializes Telegram scraper
- Connects to Redis cache
- Cleanup on shutdown

### 2. config.py

**Purpose:** Centralized configuration using Pydantic Settings

**Configuration Groups:**
- **API Settings:** CORS, debug mode
- **Model Settings:** Model path (local or HF Hub)
- **Telegram Settings:** API credentials, channels list
- **Scraping Settings:** Posts limit, sleep time, keywords
- **Cache Settings:** Redis URL, TTL
- **Inference Settings:** Default threshold, max results

**Environment Variables:**
All settings can be overridden via `.env` file or environment variables.

### 3. scraper.py

**Purpose:** Telegram job scraping using Telethon

**Class: TelegramScraper**

**Methods:**
- `connect()` - Connect to Telegram
- `disconnect()` - Cleanup connection
- `scrape_channel()` - Scrape single channel
- `scrape_jobs()` - Scrape all configured channels
- `_deduplicate_jobs()` - Remove duplicate posts

**Features:**
- Async scraping
- Rate limit handling (FloodWaitError)
- Date filtering (last N days)
- Keyword filtering
- Text cleaning
- Deduplication

**Safety:**
- Sleep between channels (configurable)
- Error handling per channel
- Public channels only

### 4. cache.py

**Purpose:** Redis-based caching for scraped jobs

**Class: JobCache**

**Methods:**
- `connect()` - Connect to Redis
- `disconnect()` - Close connection
- `get_jobs()` - Retrieve cached jobs
- `set_jobs()` - Cache jobs with TTL
- `clear_cache()` - Clear cache

**Features:**
- Async Redis operations
- JSON serialization
- TTL-based expiration (default 1 hour)
- Graceful degradation (works without Redis)

### 5. utils.py

**Purpose:** Text processing and formatting utilities

**Functions:**

**`clean_text(text: str) -> str`**
- Removes URLs, emails, phone numbers
- Removes Telegram usernames
- Removes emojis
- Removes signatures/footers
- Normalizes whitespace

**`is_job_related(text: str, keywords: List[str]) -> bool`**
- Filters job-related posts
- Case-insensitive keyword matching

**`extract_job_title(text: str) -> str`**
- Extracts job title using regex patterns
- Fallback to first line
- Default: "Job Opening"

**`format_input_pair(job_text: str, resume_text: str) -> str`**
- Formats input in dataset style
- Truncates to fit 512 tokens
- Format: "For the given job description <<JD>> the resume: <<resume>>. The result is,"

## Data Flow

### Request Flow

```
1. Client sends POST /match_resume
   ↓
2. FastAPI validates request (Pydantic)
   ↓
3. Rate limiter checks (slowapi)
   ↓
4. Check Redis cache for jobs
   ↓
5a. Cache HIT → Use cached jobs
5b. Cache MISS → Scrape Telegram channels
   ↓
6. For each job:
   - Format input pair (utils.format_input_pair)
   - Tokenize (transformers)
   - Run inference (model)
   - Calculate score
   ↓
7. Filter by threshold
   ↓
8. Sort by score (descending)
   ↓
9. Limit results (max_results)
   ↓
10. Return JSON response
```

### Scraping Flow

```
1. TelegramScraper.scrape_jobs()
   ↓
2. For each channel:
   - Get channel entity
   - Fetch messages (max_posts)
   - Filter by date (last 7 days)
   - Filter by keywords
   - Clean text
   - Sleep between channels
   ↓
3. Deduplicate jobs
   ↓
4. Cache in Redis (1 hour TTL)
   ↓
5. Return jobs list
```

## Pydantic Models

### Request Models

**ResumeRequest**
```python
{
  "resume_text": str,      # 50-10000 chars
  "threshold": float,      # 0.0-1.0, default 0.6
  "max_results": int       # 1-100, default 20
}
```

### Response Models

**JobMatch**
```python
{
  "job_text": str,
  "score": float,
  "source_channel": str,
  "title": str,
  "scraped_at": str
}
```

**MatchResponse**
```python
{
  "matches": List[JobMatch],
  "total_jobs_scraped": int,
  "total_matches": int,
  "processing_time_seconds": float
}
```

**HealthResponse**
```python
{
  "status": str,
  "model_loaded": bool,
  "scraper_ready": bool,
  "cache_ready": bool,
  "timestamp": str
}
```

## Docker Architecture

### Services

**1. Redis**
- Image: `redis:7-alpine`
- Port: 6379
- Volume: `redis_data` (persistent)
- Health check: `redis-cli ping`

**2. API**
- Build: Custom Dockerfile
- Port: 8000
- Volumes:
  - Model: `./fine_tuned_bert:/app/fine_tuned_bert:ro`
  - Session: `telegram_session:/app`
- Depends on: Redis
- Health check: `curl /health`

### Networks

- `resume_matcher_network` (bridge)

### Volumes

- `redis_data` - Redis persistence
- `telegram_session` - Telegram session files

## Environment Variables

### Required

```bash
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abc123...
TELEGRAM_PHONE=+251912345678
```

### Optional (with defaults)

```bash
MODEL_PATH=./fine_tuned_bert
REDIS_URL=redis://redis:6379/0
MAX_POSTS_PER_CHANNEL=100
SCRAPE_SLEEP_SECONDS=3.0
CACHE_TTL_SECONDS=3600
DEBUG=false
CORS_ORIGINS=["*"]
```

## Dependencies

### Core

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **torch** - PyTorch for model
- **transformers** - Hugging Face models

### Scraping

- **telethon** - Telegram client
- **cryptg** - Crypto for Telethon

### Caching

- **redis** - Redis client (async)

### Utilities

- **slowapi** - Rate limiting
- **python-dotenv** - Environment variables
- **structlog** - Structured logging

## Testing

### test_api.py

**Tests:**
1. Health check endpoint
2. Resume matching endpoint
3. Job refresh endpoint

**Usage:**
```bash
python test_api.py
```

### example_client.py

**Demonstrates:**
- Client initialization
- Health check
- Resume matching
- Top N matches
- Error handling

**Usage:**
```bash
python example_client.py
```

## Security Features

### 1. Rate Limiting

- `/match_resume`: 10 requests/minute per IP
- `/refresh_jobs`: 2 requests/hour per IP
- Uses slowapi with Redis backend

### 2. Input Validation

- Pydantic models validate all inputs
- Min/max length constraints
- Type checking
- Range validation

### 3. Error Handling

- Global exception handler
- Specific HTTP exceptions
- Structured error responses
- Logging of all errors

### 4. Docker Security

- Non-root user (appuser)
- Read-only model volume
- Health checks
- Resource limits

### 5. CORS

- Configurable origins
- Production: specific domains only
- Development: allow all

## Performance Optimizations

### 1. Caching

- Redis cache for scraped jobs (1 hour)
- Avoids repeated scraping
- Reduces Telegram API calls

### 2. Async Operations

- Async endpoints
- Async scraping
- Async Redis operations
- Non-blocking I/O

### 3. Model Inference

- Model loaded once at startup
- Batch processing possible
- Device detection (CUDA/MPS/CPU)
- Gradient disabled (eval mode)

### 4. Text Processing

- Truncation to fit 512 tokens
- Efficient regex patterns
- Deduplication

## Monitoring & Logging

### Logging Levels

- **INFO:** Normal operations
- **WARNING:** Recoverable errors
- **ERROR:** Serious errors
- **DEBUG:** Detailed debugging (dev only)

### Logged Events

- Startup/shutdown
- Model loading
- Scraping operations
- Cache hits/misses
- Request processing
- Errors and exceptions

### Metrics

- Processing time per request
- Jobs scraped count
- Matches found count
- Cache hit rate
- Error rate

## Extensibility

### Adding New Channels

```python
# config.py
TELEGRAM_CHANNELS = [
    "@ethiojobs",
    "@new_channel_1",
    "@new_channel_2"
]
```

### Custom Keywords

```python
# config.py
JOB_KEYWORDS = [
    "vacancy", "job", "hiring",
    "custom_keyword_1",
    "custom_keyword_2"
]
```

### Different Model

```python
# config.py
MODEL_PATH = "your-username/different-model"

# Or local path
MODEL_PATH = "/path/to/model"
```

### Additional Endpoints

```python
# main.py
@app.get("/custom_endpoint")
async def custom_endpoint():
    # Your logic
    return {"result": "data"}
```

## Best Practices

### 1. Configuration

- Use environment variables
- Never commit secrets
- Use `.env.example` as template

### 2. Error Handling

- Catch specific exceptions
- Log errors with context
- Return meaningful error messages

### 3. Async/Await

- Use async for I/O operations
- Avoid blocking calls
- Use asyncio.sleep() not time.sleep()

### 4. Testing

- Test all endpoints
- Test error cases
- Test with real data

### 5. Documentation

- Keep README updated
- Document API changes
- Add code comments

## Troubleshooting Guide

### Issue: Model not loading

**Check:**
- Model path in .env
- Model files exist
- Permissions (755)

### Issue: Telegram connection failed

**Check:**
- API credentials
- Phone number format
- Session file exists
- Network connectivity

### Issue: Redis connection failed

**Check:**
- Redis running
- Redis URL correct
- Network connectivity
- Firewall rules

### Issue: No jobs found

**Check:**
- Channels exist and public
- Keywords match job posts
- Date range (last 7 days)
- Scraping limits

## Future Enhancements

### Potential Features

1. **Authentication**
   - API keys
   - JWT tokens
   - User management

2. **Advanced Matching**
   - Multi-model ensemble
   - Skill extraction
   - Location filtering

3. **Analytics**
   - Usage statistics
   - Popular jobs
   - Match quality metrics

4. **Notifications**
   - Email alerts
   - Webhook callbacks
   - Real-time updates

5. **Database**
   - PostgreSQL for jobs
   - User profiles
   - Match history

6. **Frontend**
   - Web UI
   - Mobile app
   - Admin dashboard

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Submit PR

## License

MIT License - See LICENSE file

## Support

- GitHub Issues
- Email: support@example.com
- Documentation: /docs
