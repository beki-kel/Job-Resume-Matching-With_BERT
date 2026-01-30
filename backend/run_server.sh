#!/bin/bash
# Load environment variables and run server

export TELEGRAM_API_ID=38166885
export TELEGRAM_API_HASH=97a5e37aef1a578a66283729d256db81
export TELEGRAM_PHONE=+251703533063
export MODEL_PATH=../fine_tuned_telegram_model
export TELEGRAM_CHANNELS='["@freelance_ethio","@harmeejobs"]'
export MAX_POSTS_PER_CHANNEL=200
export SCRAPE_SLEEP_SECONDS=3.0
export CACHE_TTL_SECONDS=3600
export REDIS_URL=redis://localhost:6379/0
export DEBUG=false
export CORS_ORIGINS='["*"]'

python3 -m app.main
