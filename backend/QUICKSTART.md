# Quick Start Guide

Get the Resume-Job Matcher API running in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- Telegram API credentials ([Get here](https://my.telegram.org/apps))
- Fine-tuned BERT model

## Steps

### 1. Setup Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```bash
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_hash_here
TELEGRAM_PHONE=+251912345678
MODEL_PATH=./fine_tuned_bert
```

### 2. Add Your Model

```bash
# Copy your fine-tuned model
cp -r /path/to/fine_tuned_bert ./fine_tuned_bert

# Or use Hugging Face Hub (set in .env)
MODEL_PATH=your-username/model-name
```

### 3. Start Services

```bash
# Automated setup
./setup.sh

# Or manual
docker-compose up -d
```

### 4. Test API

```bash
# Check health
curl http://localhost:8000/health

# Run tests
python test_api.py
```

### 5. Use API

```bash
curl -X POST http://localhost:8000/match_resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Software Engineer with 5 years Python experience...",
    "threshold": 0.6,
    "max_results": 10
  }'
```

## API Docs

Interactive documentation: http://localhost:8000/docs

## Common Commands

```bash
# View logs
docker-compose logs -f api

# Restart
docker-compose restart

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

## Troubleshooting

### Telegram Authentication

First time? Run locally to authenticate:

```bash
pip install telethon
python -c "
from telethon import TelegramClient
client = TelegramClient('resume_matcher_session', API_ID, API_HASH)
client.start(phone=PHONE)
"
```

Enter the code sent to your phone. Session file will be created.

### Model Not Found

```bash
# Check model exists
ls -la fine_tuned_bert/

# Should contain:
# - config.json
# - model.safetensors (or pytorch_model.bin)
# - tokenizer files
```

### Redis Connection

```bash
# Test Redis
docker-compose ps redis
docker-compose logs redis
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture

## Support

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- GitHub Issues: [Create issue](https://github.com/your-repo/issues)
