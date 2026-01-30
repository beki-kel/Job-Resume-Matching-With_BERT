# Complete Resume-Job Matching Workflow

## Overview
This document demonstrates the complete end-to-end workflow of the Resume-Job Matching system with all features enabled.

## Step 1: Process Resume with LLM

Upload a PDF resume for intelligent analysis:

```bash
curl -X POST "http://localhost:8000/process_resume" \
  -F "resume_file=@resume.pdf" \
  -H "accept: application/json"
```

**Response**:
```json
{
  "processed_resume": "Professional summary without PII...",
  "cleaned_for_matching": "Cleaned text for matching...",
  "score": 8,
  "strengths": [
    "Full-stack development expertise",
    "Experience with modern frameworks",
    "Backend development and API integration"
  ],
  "improvements": [
    "Quantify results with metrics",
    "Add more project outcomes",
    "Include certifications"
  ],
  "key_skills": [
    "JavaScript", "TypeScript", "Python", 
    "React", "Node.js", "Docker"
  ],
  "experience_years": "3+"
}
```

**Features**:
- ✅ Automatic PII removal (names, emails, phones, addresses)
- ✅ Resume quality scoring (1-10)
- ✅ Actionable feedback and suggestions
- ✅ Key skills extraction
- ✅ Experience estimation

## Step 2: Match Resume with Jobs

Match the processed resume against scraped Telegram jobs:

```bash
curl -X POST "http://localhost:8000/match_resume" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your processed resume text...",
    "threshold": 0.5,
    "max_results": 10,
    "generate_explanations": true
  }'
```

**Response**:
```json
{
  "matches": [
    {
      "job_text": "Job Title: Fullstack Developer (React + Node/Python)...",
      "score": 0.6277,
      "source_channel": "@freelance_ethio",
      "title": "Fullstack Developer React Node/Python Job",
      "scraped_at": "2026-01-30T20:33:43.704151",
      "message_link": "https://t.me/freelance_ethio/92196",
      "explanation": "The 0.63 score suggests a moderate match. The resume highlights full-stack experience, specifically mentioning React which is a key requirement..."
    }
  ],
  "total_jobs_scraped": 104,
  "total_matches": 6,
  "processing_time_seconds": 17.42
}
```

**Features**:
- ✅ Semantic matching using fine-tuned BERT model
- ✅ Cosine similarity scoring (0-1 scale)
- ✅ LLM-generated explanations for top 5 matches
- ✅ Direct Telegram links to original job posts
- ✅ Full job descriptions included
- ✅ Automatic job title extraction

## Step 3: View Job Details

Users can click the `message_link` to view the full job posting on Telegram:

**Example Link**: `https://t.me/freelance_ethio/92196`

This opens the Telegram app/web and shows:
- Complete job description
- Application instructions
- Contact information
- Deadline
- Salary/compensation details

## Complete Pipeline Flow

```
┌─────────────────┐
│  Upload PDF     │
│  Resume         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extract Text   │
│  (PyPDF2/       │
│   pdfplumber)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Analysis   │
│  (Gemini 2.0)   │
│  - Remove PII   │
│  - Score (1-10) │
│  - Extract      │
│    Skills       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scrape Jobs    │
│  (Telegram)     │
│  - 4 channels   │
│  - 104 jobs     │
│  - With links   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Match Jobs     │
│  (Fine-tuned    │
│   BERT Model)   │
│  - Cosine sim   │
│  - Threshold    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate       │
│  Explanations   │
│  (Gemini LLM)   │
│  - Top 5 only   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Return Results │
│  - Scores       │
│  - Links        │
│  - Explanations │
└─────────────────┘
```

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Extraction | ~0.5s | Per page |
| LLM Resume Analysis | ~3-5s | One-time per resume |
| Job Scraping | ~4s | Cached for 1 hour |
| BERT Matching | ~0.1s | Per job (104 jobs = ~10s) |
| LLM Explanations | ~1s | Per job (top 5 = ~5s) |
| **Total Pipeline** | **~17s** | End-to-end |

## API Endpoints Summary

### 1. Health Check
```bash
GET /health
```
Returns system status including LLM availability.

### 2. Process Resume
```bash
POST /process_resume
```
- Accepts: PDF file or text
- Returns: Analyzed resume with score and feedback

### 3. Match Resume
```bash
POST /match_resume
```
- Accepts: Resume text + options
- Returns: Ranked job matches with links and explanations

### 4. Refresh Jobs
```bash
POST /refresh_jobs
```
- Forces cache refresh
- Scrapes latest jobs from Telegram

## Configuration

### Required Environment Variables
```env
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# LLM (Gemini)
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.0-flash

# Model
MODEL_PATH=../fine_tuned_telegram_model

# Channels
TELEGRAM_CHANNELS=["@freelance_ethio", "@ethiojobsofficial"]
```

## Example Use Case

**Scenario**: Job seeker wants to find matching jobs

1. **Upload Resume**: User uploads their PDF resume
2. **Get Feedback**: System analyzes and provides quality score (8/10) with suggestions
3. **Find Matches**: System finds 6 matching jobs from 104 scraped posts
4. **Review Results**: User sees:
   - Top match: Fullstack Developer (62.8% match)
   - Explanation: "Your React and backend experience align well..."
   - Link: Click to view full job on Telegram
5. **Apply**: User clicks link, reads full description, and applies

## Benefits

### For Job Seekers
- ✅ Automatic resume improvement suggestions
- ✅ Ranked job matches with explanations
- ✅ Direct links to apply
- ✅ Understand why jobs match
- ✅ Privacy-protected (PII removed)

### For Recruiters
- ✅ Automated candidate screening
- ✅ Skill extraction
- ✅ Match quality scoring
- ✅ Detailed fit analysis

### For Developers
- ✅ Clean architecture
- ✅ Easy to extend
- ✅ Well-documented
- ✅ Docker support
- ✅ Comprehensive logging

## Next Steps

1. **Frontend Integration**: Build UI to display results
2. **User Accounts**: Save resumes and match history
3. **Email Notifications**: Alert users of new matching jobs
4. **Advanced Filters**: Location, salary, experience level
5. **Multi-language**: Support Amharic job posts
6. **Mobile App**: Native iOS/Android apps

## Troubleshooting

### LLM Not Working
- Check `GEMINI_API_KEY` is set
- Verify API key is valid
- Check internet connection
- Review logs: `docker-compose logs api`

### No Jobs Found
- Verify Telegram credentials
- Check channel access
- Run `/refresh_jobs` endpoint
- Check Redis is running

### Low Match Scores
- Lower threshold (default 0.6 → 0.5)
- Improve resume quality
- Add more relevant skills
- Check job descriptions match your field

## Support

For issues or questions:
- Check logs: `docker-compose logs -f api`
- Review ARCHITECTURE.md
- Check FEATURES.md
- Open GitHub issue
