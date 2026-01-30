# Deployment Guide

Complete guide for deploying the Resume-Job Matcher API to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Security Checklist](#security-checklist)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required

- Docker & Docker Compose
- Telegram API credentials (api_id, api_hash, phone)
- Fine-tuned BERT model

### Optional

- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)
- Cloud provider account (AWS, GCP, Azure, DigitalOcean)

## Local Development

### 1. Setup Environment

```bash
# Clone repository
cd backend

# Create environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Prepare Model

```bash
# Option 1: Copy local model
cp -r /path/to/fine_tuned_bert ./fine_tuned_bert

# Option 2: Use Hugging Face Hub
# Set MODEL_PATH=your-username/model-name in .env
```

### 4. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
# macOS: brew install redis && redis-server
# Ubuntu: sudo apt install redis-server
```

### 5. Run API

```bash
# Development mode (auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Test

```bash
# Run test suite
python test_api.py

# Or use curl
curl http://localhost:8000/health
```

## Docker Deployment

### Quick Start

```bash
# Run setup script
./setup.sh

# Or manually
docker-compose up -d
```

### Custom Configuration

#### 1. Edit docker-compose.yml

```yaml
api:
  environment:
    - MAX_POSTS_PER_CHANNEL=200
    - CACHE_TTL_SECONDS=7200
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

#### 2. Mount Custom Model

```yaml
volumes:
  - /path/to/your/model:/app/fine_tuned_bert:ro
```

#### 3. Use External Redis

```yaml
api:
  environment:
    - REDIS_URL=redis://your-redis-host:6379/0
```

### Production Build

```bash
# Build optimized image
docker build -t resume-matcher:prod --target production .

# Run with production settings
docker run -d \
  --name resume-matcher \
  -p 8000:8000 \
  -e DEBUG=false \
  -e REDIS_URL=redis://redis:6379 \
  --restart unless-stopped \
  resume-matcher:prod
```

## Cloud Deployment

### AWS (ECS/Fargate)

#### 1. Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t resume-matcher .
docker tag resume-matcher:latest <account>.dkr.ecr.us-east-1.amazonaws.com/resume-matcher:latest

# Push
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/resume-matcher:latest
```

#### 2. Create ECS Task Definition

```json
{
  "family": "resume-matcher",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/resume-matcher:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "REDIS_URL", "value": "redis://elasticache-endpoint:6379"},
        {"name": "MODEL_PATH", "value": "/app/fine_tuned_bert"}
      ],
      "secrets": [
        {"name": "TELEGRAM_API_ID", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "TELEGRAM_API_HASH", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

#### 3. Setup ElastiCache (Redis)

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id resume-matcher-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

### DigitalOcean App Platform

#### 1. Create app.yaml

```yaml
name: resume-matcher
services:
  - name: api
    github:
      repo: your-username/resume-matcher
      branch: main
    dockerfile_path: backend/Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: professional-s
    envs:
      - key: REDIS_URL
        value: ${redis.DATABASE_URL}
      - key: TELEGRAM_API_ID
        value: ${TELEGRAM_API_ID}
        type: SECRET
      - key: TELEGRAM_API_HASH
        value: ${TELEGRAM_API_HASH}
        type: SECRET
    health_check:
      http_path: /health

databases:
  - name: redis
    engine: REDIS
    production: true
```

#### 2. Deploy

```bash
doctl apps create --spec app.yaml
```

### Google Cloud Run

#### 1. Build and Push

```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/resume-matcher

# Or use Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

#### 2. Deploy

```bash
gcloud run deploy resume-matcher \
  --image gcr.io/PROJECT_ID/resume-matcher \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars REDIS_URL=redis://... \
  --set-secrets TELEGRAM_API_ID=telegram-api-id:latest \
  --allow-unauthenticated
```

## Security Checklist

### Before Production

- [ ] Change default credentials
- [ ] Set `DEBUG=false`
- [ ] Configure CORS properly (not `["*"]`)
- [ ] Use HTTPS/TLS
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Use secrets manager for credentials
- [ ] Enable logging and monitoring
- [ ] Set resource limits
- [ ] Use non-root user in Docker
- [ ] Keep dependencies updated
- [ ] Implement authentication (if needed)

### Environment Variables

```bash
# Production .env
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
TELEGRAM_API_ID=<from-secrets-manager>
TELEGRAM_API_HASH=<from-secrets-manager>
REDIS_URL=<secure-redis-url>
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Monitoring

### Health Checks

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Docker healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Logging

```python
# Structured logging with structlog
import structlog

logger = structlog.get_logger()
logger.info("request_processed", 
           endpoint="/match_resume",
           processing_time=2.5,
           matches=12)
```

### Metrics (Prometheus)

```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')
```

### Alerts

```yaml
# Example alert rules
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.1
        annotations:
          summary: "High error rate detected"
      
      - alert: SlowResponses
        expr: api_request_duration_seconds > 10
        annotations:
          summary: "API responses are slow"
```

## Troubleshooting

### Common Issues

#### 1. Model Not Loading

```bash
# Check model files
ls -la fine_tuned_bert/

# Test loading
python -c "from transformers import AutoModel; AutoModel.from_pretrained('./fine_tuned_bert')"

# Check permissions
chmod -R 755 fine_tuned_bert/
```

#### 2. Telegram Connection Failed

```bash
# Authenticate locally first
python -c "
from telethon import TelegramClient
client = TelegramClient('session', API_ID, API_HASH)
client.start(phone=PHONE)
"

# Copy session file to Docker volume
docker cp resume_matcher_session.session container:/app/
```

#### 3. Redis Connection Issues

```bash
# Test Redis
redis-cli ping

# Check connection
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

#### 4. Out of Memory

```bash
# Increase Docker memory
# Docker Desktop -> Settings -> Resources -> Memory

# Or limit model batch size
# Reduce MAX_POSTS_PER_CHANNEL in config
```

#### 5. Rate Limiting Issues

```bash
# Increase Telegram sleep time
SCRAPE_SLEEP_SECONDS=5.0

# Reduce posts per channel
MAX_POSTS_PER_CHANNEL=50
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=true docker-compose up

# View detailed logs
docker-compose logs -f --tail=100 api
```

### Performance Tuning

```python
# Increase workers
uvicorn main:app --workers 4

# Use gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Optimize model inference
model.to('cuda')  # Use GPU if available
torch.set_num_threads(4)  # CPU threads
```

## Backup & Recovery

### Backup Telegram Session

```bash
# Backup session file
docker cp container:/app/resume_matcher_session.session ./backup/

# Restore
docker cp ./backup/resume_matcher_session.session container:/app/
```

### Backup Redis Data

```bash
# Redis persistence
docker-compose exec redis redis-cli BGSAVE

# Copy dump
docker cp container:/data/dump.rdb ./backup/
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
api:
  deploy:
    replicas: 3
  
# Load balancer
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

### Vertical Scaling

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health: `curl http://localhost:8000/health`
- Open GitHub issue with logs and configuration
