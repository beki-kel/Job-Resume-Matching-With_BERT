#!/bin/bash
# Setup script for Resume-Job Matcher API

set -e

echo "=========================================="
echo "Resume-Job Matcher API Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env with your Telegram credentials${NC}"
    exit 1
fi

# Check if model exists
if [ ! -d "fine_tuned_bert" ]; then
    echo -e "${YELLOW}⚠ Model directory not found: fine_tuned_bert/${NC}"
    echo "Please place your fine-tuned model in ./fine_tuned_bert/"
    echo "Or update MODEL_PATH in .env to point to your model"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Build and start services
echo ""
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "Checking API health..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ API is healthy!${NC}"
        break
    fi
    echo "Waiting for API... ($i/10)"
    sleep 3
done

echo ""
echo "=========================================="
echo -e "${GREEN}Setup complete!${NC}"
echo "=========================================="
echo ""
echo "API is running at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f api"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Test API:     python test_api.py"
echo ""
