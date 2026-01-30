# Resume-Job Matcher API

Production-ready FastAPI backend for matching resumes with Telegram job posts using fine-tuned BERT model.

## Features

- 🤖 **AI-Powered Matching**: Fine-tuned BERT model for semantic similarity
- 📱 **Telegram Scraping**: Scrapes job posts from public Ethiopian job channels
- ⚡ **Fast & Async**: Async endpoints with Redis caching
- 🔒 **Production-Ready**: Rate limiting, error handling, health checks
- 🐳 **Docker Support**: Complete containerization with docker-compose
- 📊 **Smart Ranking**: Returns jobs ranked by match score

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /match_resume
       ▼
┌─────────────────┐
│  FastAPI API    │
├─────────────────┤
│ • Rate Limiting │
│ • Validation    │
│ • Logging       │
└────┬────────┬───┘
     │        │
     │        ▼
     │   ┌─────────┐
     │   │  Redis  │ (Job Cache)
     │   └─────────┘
     │
     ▼
┌──────────────┐      ┌──────────────┐
│   Telegram   │      │  BERT Model  │
│   Scraper    │      │  Inference   │
└──────────────┘      └──────────────┘
```

## Prerequisites

1. **Telegram API Credentials**
   - Go to https://my.telegram.org/apps
   - Create an application
   - Get `api_id` and `api_hash`

2. **Fine-tuned Model**
   - Place your fine-tuned model in `./fine_tuned_bert/`
   - Or use Hugging Face Hub path

3. **Docker & Docker Compose** (for containerized deployment)

## Quick Start

### 1. Clone and Setup

```bash
cd backend
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your credentials:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_hash_here
TELEGRAM_PHONE=+251912345678
MODEL_PATH=./fine_tuned_bert
```

### 3. Run with Docker Compose

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 4. Run Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scraper_ready": true,
  "cache_ready": true,
  "timestamp": "2024-01-30T12:00:00"
}
```

### Match Resume
```bash
POST /match_resume
Content-Type: application/json

{
  "resume_text": "Software Engineer with 5 years Python experience...",
  "threshold": 0.6,
  "max_results": 20
}
```

Response:
```json
{
  "matches": [
    {
      "job_text": "Senior Python Developer needed...",
      "score": 0.85,
      "source_channel": "@ethiojobs",
      "title": "Senior Python Developer",
      "scraped_at": "2024-01-30T12:00:00"
    }
  ],
  "total_jobs_scraped": 150,
  "total_matches": 12,
  "processing_time_seconds": 2.5
}
```

### Refresh Jobs (Admin)
```bash
POST /refresh_jobs
```

Force refresh job cache (rate limited: 2/hour).

## Configuration

### Telegram Channels

Edit `config.py` or set environment variable:

```python
TELEGRAM_CHANNELS = [
    "@ethiojobs",
    "@jobs_in_ethiopia",
    "@ethiopianjobs",
    "@addisababa_jobs"
]
```

### Scraping Settings

```python
MAX_POSTS_PER_CHANNEL = 100  # Posts to fetch per channel
SCRAPE_SLEEP_SECONDS = 3.0   # Sleep between channels
CACHE_TTL_SECONDS = 3600     # Cache duration (1 hour)
```

### Job Keywords

Jobs are filtered by keywords (edit in `config.py`):

```python
JOB_KEYWORDS = [
    "vacancy", "job", "hiring", "position", 
    "opening", "career", "opportunity"
]
```

## Model Format

The API expects a fine-tuned model trained on the `facehuggerapoorv/resume-jd-match` dataset format:

**Input format:**
```
For the given job description <<JD text>> the resume: <<resume text>>. The result is,
```

**Output:** Regression score (0-1)

### Using Your Model

1. **Local model:**
   ```bash
   # Place model files in backend/fine_tuned_bert/
   backend/
   └── fine_tuned_bert/
       ├── config.json
       ├── model.safetensors
       ├── tokenizer.json
       └── ...
   ```

2. **Hugging Face Hub:**
   ```python
   MODEL_PATH = "your-username/fine-tuned-resume-matcher"
   ```

## Rate Limiting

- `/match_resume`: 10 requests/minute per IP
- `/refresh_jobs`: 2 requests/hour per IP

## Caching

Jobs are cached in Redis for 1 hour to avoid repeated scraping:
- First request: Scrapes fresh jobs (~10-30s)
- Subsequent requests: Uses cache (~1-3s)

## Security Features

- ✅ Rate limiting (slowapi)
- ✅ Input validation (Pydantic)
- ✅ CORS configuration
- ✅ Non-root Docker user
- ✅ Health checks
- ✅ Structured logging
- ✅ Error handling

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker
docker-compose logs -f api

# Local
# Logs printed to stdout
```

### Metrics
- Processing time per request
- Cache hit/miss rate
- Jobs scraped count
- Match count

## Troubleshooting

### Telegram Connection Issues

1. **First-time login:**
   ```bash
   # Run locally first to authenticate
   python -c "from scraper import TelegramScraper; import asyncio; s = TelegramScraper(...); asyncio.run(s.connect())"
   ```
   Enter the code sent to your phone.

2. **Session persistence:**
   - Session saved in `resume_matcher_session.session`
   - Mount as volume in Docker

### Model Loading Issues

```bash
# Check model path
ls -la fine_tuned_bert/

# Test model loading
python -c "from transformers import AutoModel; AutoModel.from_pretrained('./fine_tuned_bert')"
```

### Redis Connection Issues

```bash
# Check Redis
docker-compose ps redis
redis-cli ping

# Restart Redis
docker-compose restart redis
```

## Performance

- **Cold start:** ~10-30s (scraping + inference)
- **Cached:** ~1-3s (inference only)
- **Memory:** ~2-4GB (model + Redis)
- **CPU:** Optimized for CPU inference

## Production Deployment

### Environment Variables

```bash
# Production settings
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
REDIS_URL=redis://redis:6379/0
```

### Scaling

```yaml
# docker-compose.yml
api:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

### Reverse Proxy (Nginx)

```nginx
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
