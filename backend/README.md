# Backend API

FastAPI backend for AI-powered resume-job matching system with LLM enhancement.

## Features

- 🤖 Fine-tuned Sentence Transformer for semantic matching
- 🧠 Gemini LLM for resume analysis and job explanations
- 📄 PDF resume upload support
- 🔒 Automatic PII removal
- 🔗 Direct Telegram links to job posts
- ⚡ Redis caching
- 📱 Telegram job scraping
- 🐳 Docker support

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start server:
```bash
./run_server.sh
```

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## API Endpoints

### POST /process_resume
Process resume with LLM to extract key information and provide feedback.

**Request (Form Data):**
- `resume_text`: Plain text resume (optional)
- `resume_file`: PDF file (optional)

**Response:**
```json
{
  "processed_resume": "Cleaned resume text...",
  "cleaned_for_matching": "Resume for ML matching...",
  "score": 8,
  "strengths": ["Clear technical skills", "Quantified achievements"],
  "improvements": ["Add certifications", "Expand leadership"],
  "key_skills": ["Python", "AWS", "Docker"],
  "experience_years": "5+"
}
```

### POST /match_resume
Match resume with scraped jobs.

**Request:**
```json
{
  "resume_text": "string",
  "threshold": 0.6,
  "max_results": 20,
  "generate_explanations": true
}
```

**Response:**
```json
{
  "matches": [
    {
      "job_text": "...",
      "score": 0.85,
      "source_channel": "@channel",
      "title": "Senior Developer",
      "scraped_at": "2026-01-30T...",
      "explanation": "Strong match because..."
    }
  ],
  "total_jobs_scraped": 104,
  "total_matches": 5,
  "processing_time_seconds": 2.5
}
```

### GET /health
Health check endpoint.

### POST /refresh_jobs
Force refresh job cache (rate limited: 2/hour).

## Configuration

Environment variables in `.env`:

**Required:**
- `TELEGRAM_API_ID` - Telegram API ID
- `TELEGRAM_API_HASH` - Telegram API hash
- `TELEGRAM_PHONE` - Phone number
- `TELEGRAM_CHANNELS` - JSON array of channels
- `MODEL_PATH` - Path to model directory

**Optional:**
- `GEMINI_API_KEY` - Gemini API key (for LLM features)
- `GEMINI_MODEL` - Model name (default: gemini-1.5-flash)
- `REDIS_URL` - Redis connection URL
- `MAX_POSTS_PER_CHANNEL` - Max posts to scrape (default: 100)
- `CACHE_TTL_SECONDS` - Cache TTL (default: 3600)

## Testing

```bash
# Test API
python3 tests/test_api.py

# Test with PDF
curl -X POST http://localhost:8000/process_resume \
  -F "resume_file=@resume.pdf"

# Test matching with explanations
curl -X POST http://localhost:8000/match_resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume...",
    "generate_explanations": true
  }'
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Performance Optimizations

- Multi-stage Docker builds for smaller images
- Redis caching for scraped jobs
- Batch embedding generation
- Connection pooling
- Health checks and graceful shutdown
- Rate limiting

## Rate Limits

- `/match_resume`: 10 requests/minute
- `/refresh_jobs`: 2 requests/hour

## Docker Services

- **api**: FastAPI application
- **redis**: Redis cache

## Troubleshooting

**LLM features not working:**
- Check `GEMINI_API_KEY` is set correctly
- Verify API key at https://makersuite.google.com/app/apikey

**PDF extraction fails:**
- Ensure PDF is not password-protected
- Try with a different PDF library

**Docker build fails:**
- Check Docker has enough memory (4GB+ recommended)
- Clear Docker cache: `docker system prune -a`
