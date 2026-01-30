# JobMatch AI 🤖

AI powered resume job website that allows you to Upload your resume, get AI analysis, and find matching jobs from Telegram channels.

## ✨ Features

- 🎯 **Smart Matching** - Fine-tuned BERT model for semantic job matching
- 🧠 **AI Analysis** - Gemini LLM analyzes resumes and explains matches
- 📱 **Telegram Integration** - Scrapes jobs from Ethiopian job channels
- ⚡ **Fast** - Redis caching for instant results
- � **Privacy** - Automatic PII removal from resumes

## � Quick Start

### Prerequisites
```bash
# Required
- Python 3.9+
- Node.js 18+
- Redis

# API Keys (free)
- Telegram API: https://my.telegram.org/apps
- Gemini API: https://aistudio.google.com/app/apikey
```

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your API keys to .env

# Start server
./run_server.sh
```

Backend runs at **http://localhost:8000**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start app
npm run dev
```

Frontend runs at **http://localhost:3000**

### 3. Use the App

1. Open http://localhost:3000
2. Upload your resume (PDF)
3. View AI analysis
4. Browse matching jobs
5. Click to apply on Telegram

## 🎨 UI Features

- **Aurora Background** - Animated gradient effects
- **Glass Cards** - Shining edges on hover
- **Iconsax Icons** - Modern, bold icons
- **Smooth Animations** - Framer Motion transitions
- **Responsive** - Works on all devices

## ⚙️ Configuration

### Backend (.env)
```env
# Telegram API (get from https://my.telegram.org/apps)
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash
TELEGRAM_PHONE=+251912345678

# Gemini API (get from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash

# Job Channels (Ethiopian job channels)
TELEGRAM_CHANNELS=["@freelance_ethio", "@ethiojobsofficial", "@effoyjobs", "@web3hiring", "@harmeejobs"]

# Scraping Settings
MAX_POSTS_PER_CHANNEL=300
SCRAPE_DAYS_BACK=14

# Redis
REDIS_URL=redis://localhost:6379/0

# Model Path
MODEL_PATH=../fine_tuned_telegram_model
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   ├── infrastructure/  # External services
│   │   └── domain/      # Models & schemas
│   └── .env             # Configuration
│
├── frontend/            # Next.js frontend
│   ├── app/            # Pages
│   ├── components/     # React components
│   ├── lib/            # Utilities & hooks
│   └── .env.local      # Configuration
│
└── fine_tuned_telegram_model/  # BERT model
```

## 🔧 Tech Stack

**Backend**
- FastAPI - Web framework
- PyTorch - ML framework
- Sentence-BERT - Semantic matching
- Gemini - LLM for analysis
- Redis - Caching
- Telethon - Telegram scraping

**Frontend**
- Next.js 15 - React framework
- TypeScript - Type safety
- Tailwind CSS v4 - Styling
- Framer Motion - Animations
- Iconsax - Icons

## 📊 How It Works

1. **Resume Upload** → PDF text extraction + PII removal
2. **AI Analysis** → Gemini scores resume (1-10) + extracts skills
3. **Job Scraping** → Fetches jobs from Telegram (cached daily)
4. **Matching** → BERT computes similarity scores (57%+ threshold)
5. **Explanations** → Gemini explains why jobs match
6. **Results** → Ranked jobs with direct Telegram links

## 🎯 API Endpoints

```bash
# Process resume
POST /process_resume
- Upload: PDF file
- Returns: Score, strengths, improvements, skills

# Match jobs
POST /match_resume
- Body: { resume_text, threshold: 0.57, max_results: 20 }
- Returns: Ranked job matches with explanations

# Cache info
GET /cache/info

# Health check
GET /health
```

Full API docs: http://localhost:8000/docs

## 🐳 Docker Deployment

```bash
cd backend
docker-compose up -d
```

## 🔍 Troubleshooting

**Backend won't start?**
- Check Redis: `redis-cli ping` (should return PONG)
- Verify API keys in `.env`
- Check logs: `tail -f backend/logs/*.log`

**Frontend build error?**
- Clear cache: `rm -rf frontend/.next`
- Reinstall: `cd frontend && npm install`

**No jobs found?**
- Wait for initial scrape (~2 min)
- Check cache: `curl http://localhost:8000/cache/info`
- Force refresh: `curl -X POST http://localhost:8000/refresh_jobs`

**Gemini rate limit?**
- Free tier: 15 requests/min
- Wait 1 minute or upgrade API key

## 📝 Development

```bash
# Backend with auto-reload
cd backend && ./run_server.sh

# Frontend with hot reload
cd frontend && npm run dev

# Run tests
cd backend && pytest
```

## 🎓 For Beginners

**Never used Python/Node.js?**

1. Install Python: https://python.org/downloads
2. Install Node.js: https://nodejs.org
3. Install Redis: 
   - Mac: `brew install redis && brew services start redis`
   - Ubuntu: `sudo apt install redis-server`
   - Windows: https://redis.io/docs/install/install-redis/install-redis-on-windows/

4. Follow Quick Start above

**Need help with API keys?**
- Telegram: Login → https://my.telegram.org/apps → Create app
- Gemini: Login → https://aistudio.google.com/app/apikey → Create key

## 📄 License

MIT

---

**🚀 Ready to match resumes!** Open http://localhost:3000
