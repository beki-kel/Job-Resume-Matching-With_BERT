# JobMatch AI 🤖

AI-Powered Resume-Job Matching System with Glassmorphic UI

## Overview

JobMatch AI is a full-stack application that uses AI to match resumes with job postings from Telegram channels. It features a modern glassmorphic UI, semantic matching with fine-tuned BERT, and LLM-powered explanations.

## Features

### Backend (FastAPI)
- 🤖 **Fine-tuned BERT Model** - Semantic job matching
- 🧠 **Gemini LLM Integration** - Resume analysis & match explanations
- 📄 **PDF Processing** - Extract text from resume PDFs
- 🔒 **PII Removal** - Automatic removal of personal information
- 📱 **Telegram Scraping** - Fetch jobs from Telegram channels
- 💾 **Redis Caching** - Smart daily cache strategy
- 🔗 **Direct Links** - Telegram message links for each job
- 🐳 **Docker Support** - Easy deployment

### Frontend (Next.js)
- 🎨 **Glassmorphic Design** - Apple-inspired dark theme
- ⚡ **Next.js 15** - Latest React framework
- 🎭 **Framer Motion** - Smooth animations
- 📱 **Responsive** - Works on all devices
- ✨ **Shimmer Loading** - Beautiful loading states
- 🎯 **Clean Architecture** - Maintainable codebase
- 🔄 **Real-time Updates** - Live processing feedback

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis
- Telegram API credentials
- Google Gemini API key

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start server
./run_server.sh
```

Backend runs on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local if needed

# Start development server
npm run dev
```

Frontend runs on http://localhost:3000

### 3. Open Application

Visit http://localhost:3000 and start matching resumes!

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── api/              # API routes
│   ├── core/             # Configuration
│   ├── domain/           # Models & schemas
│   ├── infrastructure/   # External services
│   │   ├── cache/       # Redis cache
│   │   ├── llm/         # Gemini client
│   │   ├── ml/          # BERT model
│   │   └── telegram/    # Telegram scraper
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── tests/                # Tests
└── .env                  # Environment variables
```

### Frontend Structure
```
frontend/
├── app/                  # Next.js App Router
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Main page
│   └── globals.css      # Global styles
├── components/
│   ├── features/        # Feature components
│   └── ui/              # UI components
├── lib/
│   ├── api/             # API client
│   ├── hooks/           # Custom hooks
│   ├── types/           # TypeScript types
│   ├── utils/           # Utilities
│   └── constants/       # Constants
└── public/              # Static assets
```

## User Flow

1. **Upload Resume** - Drag & drop PDF file
2. **AI Analysis** - View resume score, strengths, improvements
3. **Job Matches** - Browse ranked job listings with scores
4. **Apply** - Click Telegram link to apply directly

## API Endpoints

### Resume Processing
```bash
POST /process_resume
- Upload PDF resume
- Returns: Analysis with score, strengths, improvements, skills
```

### Job Matching
```bash
POST /match_resume
- Body: { resume_text, threshold, max_results, generate_explanations }
- Returns: Ranked job matches with scores and explanations
```

### Cache Management
```bash
GET /cache/info
- Returns: Cache status and job count

POST /refresh_jobs
- Force refresh job cache
```

### Health Check
```bash
GET /health
- Returns: System status
```

## Configuration

### Backend (.env)
```env
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
TELEGRAM_CHANNELS=["@channel1", "@channel2"]

# LLM
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.0-flash

# Model
MODEL_PATH=../fine_tuned_telegram_model

# Scraping
MAX_POSTS_PER_CHANNEL=300
SCRAPE_DAYS_BACK=14

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Performance

- **Resume Processing**: ~3-5s (LLM analysis)
- **Job Matching**: ~0.5s (with cache)
- **Total Flow**: ~5-6s (end-to-end)
- **Cache Hit Rate**: 99% (after first scrape)

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ML**: PyTorch, Transformers, Sentence-BERT
- **LLM**: Google Gemini
- **Cache**: Redis
- **Scraping**: Telethon
- **PDF**: PyPDF2, pdfplumber

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **HTTP**: Axios

## Documentation

### Backend
- [README](backend/README.md)
- [Architecture](backend/ARCHITECTURE.md)
- [Features](backend/FEATURES.md)
- [Complete Workflow](backend/COMPLETE_WORKFLOW.md)
- [Caching Strategy](backend/CACHING_STRATEGY.md)

### Frontend
- [README](frontend/README.md)
- [Frontend Complete](FRONTEND_COMPLETE.md)

### API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Backend (Docker)
```bash
cd backend
docker-compose up -d
```

### Frontend (Vercel)
```bash
cd frontend
vercel
```

## Development

### Backend
```bash
cd backend
./run_server.sh
```

### Frontend
```bash
cd frontend
npm run dev
```

### Run Tests
```bash
cd backend
pytest
```

## Troubleshooting

### Backend Issues
- Check Redis is running: `redis-cli ping`
- Verify Telegram credentials
- Check Gemini API key
- Review logs: `docker-compose logs -f api`

### Frontend Issues
- Clear Next.js cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check API connection: `curl http://localhost:8000/health`

## Contributing

1. Follow clean architecture principles
2. Use TypeScript for type safety
3. Add proper error handling
4. Write meaningful commit messages
5. Update documentation

## License

MIT

## Support

For issues or questions:
- Check documentation in respective folders
- Review API docs at http://localhost:8000/docs
- Open an issue on GitHub

---

**Built with ❤️ using AI-powered technologies**

🚀 **Ready to use!** Open http://localhost:3000 and start matching!
