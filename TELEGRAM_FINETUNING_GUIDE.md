# Fine-Tuning with Telegram Job Scraping - Complete Guide

## 📓 Notebook Created

**File:** `finetune_with_telegram_scraping.ipynb`  
**Size:** 16 KB  
**Cells:** 17 cells (markdown + code)

## 🎯 What This Notebook Does

### 1. Scrapes Real Jobs from Telegram
- Uses **Telethon** to scrape 200 recent jobs
- Channels: @freelance_ethio, @harmeejobs, @ethiojobs, @jobs_in_ethiopia
- Filters by job keywords (vacancy, hiring, position, etc.)
- Cleans text (removes URLs, emojis, phone numbers)

### 2. Loads Resume Dataset
- Primary: `netsol/resume-score-details` from Hugging Face
- Fallback: Uses job descriptions as pseudo-resumes
- Cleans and normalizes all text

### 3. Creates Weak Labels
- **Method:** TF-IDF + Cosine Similarity
- Pairs each job with 8 resumes (4 positive + 4 negative)
- Generates ~1000-2000 training pairs
- Scores normalized to 0-1 range

### 4. Fine-Tunes Sentence Transformer
- **Model:** all-MiniLM-L6-v2 (384 dim, CPU-friendly)
- **Loss:** CosineSimilarityLoss (regression)
- **Epochs:** 3
- **Batch Size:** 16
- **Split:** 80/10/10 (train/val/test)

### 5. Evaluates Performance
- **Metrics:** MSE, Pearson, Spearman correlations
- Test set evaluation
- Inference examples

## 📋 Notebook Structure

| Cell | Type | Content |
|------|------|---------|
| 1 | Markdown | Introduction and overview |
| 2 | Code | Install packages |
| 3 | Code | Import libraries |
| 4 | Code | Configuration (API keys, settings) |
| 5 | Code | Text cleaning functions |
| 6 | Code | Telegram scraper function |
| 7 | Code | Execute scraping |
| 8 | Code | Load resume dataset |
| 9 | Code | Create weak labels (TF-IDF) |
| 10 | Code | Prepare training data |
| 11 | Code | Load Sentence Transformer |
| 12 | Code | Setup training (DataLoader, loss) |
| 13 | Code | Fine-tune model |
| 14 | Code | Evaluate on test set |
| 15 | Code | Inference example |
| 16 | Code | Save model |
| 17 | Markdown | Conclusion and next steps |

## 🚀 Quick Start

### 1. Prerequisites

```bash
pip install sentence-transformers telethon datasets scikit-learn pandas numpy scipy
```

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Create an application
3. Get `api_id` and `api_hash`
4. Update Cell 4 in the notebook

### 3. Run the Notebook

```bash
jupyter notebook finetune_with_telegram_scraping.ipynb
```

Or use Google Colab, Kaggle, or any Jupyter environment.

### 4. First Run Authentication

On first run, Telethon will ask for:
- Verification code (sent to your phone)
- Password (if 2FA enabled)

Session will be saved for future runs.

## 📊 Expected Results

### Dataset Size
- **Jobs scraped:** ~200 jobs
- **Resumes loaded:** ~500-1000 resumes
- **Training pairs:** ~1000-2000 pairs
- **Training time:** ~10-30 minutes (CPU)

### Performance Metrics
- **MSE:** ~0.10-0.20 (lower is better)
- **Pearson:** ~0.40-0.60 (higher is better)
- **Spearman:** ~0.40-0.60 (higher is better)

### Model Output
- **Format:** Sentence Transformer model
- **Location:** `./fine_tuned_telegram_model/`
- **Size:** ~90 MB
- **Embedding dim:** 384 (all-MiniLM-L6-v2)

## 🔧 Configuration Options

### Telegram Settings

```python
# In Cell 4
TELEGRAM_API_ID = YOUR_API_ID
TELEGRAM_API_HASH = 'YOUR_API_HASH'
TELEGRAM_PHONE = '+YOUR_PHONE'

CHANNELS = [
    '@freelance_ethio',
    '@harmeejobs',
    '@ethiojobs',
    '@jobs_in_ethiopia'
]

MAX_JOBS = 200
JOBS_PER_CHANNEL = 100
DAYS_BACK = 30
```

### Model Settings

```python
# Choose model
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'  # Fast, 384 dim
# Or
MODEL_NAME = 'sentence-transformers/paraphrase-mpnet-base-v2'  # Better, 768 dim

# Training
EPOCHS = 3
BATCH_SIZE = 16
RESUMES_PER_JOB = 8
```

### Pairing Strategy

```python
# In create_weak_labels function
# Adjust positive/negative ratio
top_indices = np.argsort(similarities)[-resumes_per_job//2:]  # Top matches
bottom_indices = np.random.choice(...)  # Random negatives
```

## 🎓 Key Features

### 1. Weak Labeling with TF-IDF

**Why TF-IDF?**
- No manual labeling required
- Fast computation
- Reasonable proxy for semantic similarity
- Works well for bootstrapping

**How it works:**
```python
# Vectorize all texts
vectorizer = TfidfVectorizer(max_features=5000)
job_vectors = vectorizer.transform(job_texts)
resume_vectors = vectorizer.transform(resume_texts)

# Compute similarities
similarities = cosine_similarity(job_vectors, resume_vectors)
```

### 2. Balanced Pairing

For each job:
- **4 positive pairs:** Top TF-IDF matches (similar)
- **4 negative pairs:** Random low matches (dissimilar)

This creates a balanced dataset for better learning.

### 3. Sentence Transformers

**Advantages:**
- Pre-trained on semantic similarity
- Easy fine-tuning API
- Efficient inference
- Production-ready

**Loss Function:**
- `CosineSimilarityLoss`: Regression loss for 0-1 scores
- Optimizes cosine similarity between embeddings

## 📈 Improving Performance

### 1. More Data

```python
# Increase scraping
MAX_JOBS = 500
JOBS_PER_CHANNEL = 200

# More resumes per job
RESUMES_PER_JOB = 12
```

### 2. Better Model

```python
# Use larger model
MODEL_NAME = 'sentence-transformers/paraphrase-mpnet-base-v2'  # 768 dim
# Or
MODEL_NAME = 'sentence-transformers/all-roberta-large-v1'  # 1024 dim
```

### 3. More Training

```python
# More epochs
EPOCHS = 5

# Larger batch size (if GPU available)
BATCH_SIZE = 32
```

### 4. Better Labeling

```python
# Use pre-trained model for labeling instead of TF-IDF
labeling_model = SentenceTransformer('all-MiniLM-L6-v2')
job_embs = labeling_model.encode(job_texts)
resume_embs = labeling_model.encode(resume_texts)
similarities = cosine_similarity(job_embs, resume_embs)
```

## 🔄 Integration with Backend

### Update Backend Model

```bash
# After training, copy model to backend
cp -r ./fine_tuned_telegram_model backend/fine_tuned_bert

# Update backend/.env
MODEL_PATH=./fine_tuned_bert
```

### Restart Backend

```bash
cd backend
./run_server.sh
```

The backend will automatically use the new model!

## 🧪 Testing the Model

### In Notebook

```python
# Load model
model = SentenceTransformer('./fine_tuned_telegram_model')

# Test
job = "Software Engineer with Python experience"
resume = "5 years Python developer, Django, FastAPI"

job_emb = model.encode([job])
resume_emb = model.encode([resume])

similarity = cosine_similarity(job_emb, resume_emb)[0][0]
print(f"Similarity: {similarity:.4f}")
```

### With Backend API

```bash
curl -X POST http://localhost:8000/match_resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume...",
    "threshold": 0.6,
    "max_results": 10
  }'
```

## 📝 Notes

### Telegram Scraping

- **Rate Limits:** Telethon handles FloodWaitError automatically
- **Sleep:** 3 seconds between channels to avoid rate limits
- **Session:** Saved as `scraper_session.session` for reuse
- **Public Channels:** Only scrapes public channels (ethical)

### Resume Dataset

- **Primary:** netsol/resume-score-details (Hugging Face)
- **Fallback:** Uses job descriptions if dataset unavailable
- **Alternative:** Can use local CSV files

### Weak Labels

- **Quality:** TF-IDF is a reasonable proxy but not perfect
- **Improvement:** Use pre-trained model for better labels
- **Manual:** Can add manual labels for validation

## 🐛 Troubleshooting

### Issue: Telegram Authentication Failed

**Solution:**
```python
# Delete old session
!rm scraper_session.session*

# Run scraping cell again
# Enter verification code when prompted
```

### Issue: No Jobs Found

**Solution:**
- Check channel names (must start with @)
- Verify channels are public
- Adjust `DAYS_BACK` to get older posts
- Check `JOB_KEYWORDS` filter

### Issue: Resume Dataset Not Loading

**Solution:**
```python
# Use fallback (job descriptions as resumes)
# Or load local CSV
resumes_df = pd.read_csv('your_resumes.csv')
```

### Issue: Out of Memory

**Solution:**
```python
# Reduce batch size
BATCH_SIZE = 8

# Reduce data size
MAX_JOBS = 100
RESUMES_PER_JOB = 6
```

### Issue: Slow Training

**Solution:**
- Use GPU if available
- Reduce model size (all-MiniLM-L6-v2)
- Reduce epochs
- Reduce data size

## 📚 Additional Resources

### Sentence Transformers
- Docs: https://www.sbert.net/
- Models: https://www.sbert.net/docs/pretrained_models.html
- Training: https://www.sbert.net/docs/training/overview.html

### Telethon
- Docs: https://docs.telethon.dev/
- Getting Started: https://docs.telethon.dev/en/stable/basic/quick-start.html

### Datasets
- Hugging Face: https://huggingface.co/datasets
- netsol/resume-score-details: https://huggingface.co/datasets/netsol/resume-score-details

## ✅ Checklist

Before running:
- [ ] Install all packages
- [ ] Get Telegram API credentials
- [ ] Update Cell 4 with credentials
- [ ] Verify Telegram channels are accessible
- [ ] Have ~30 minutes for training

After training:
- [ ] Check evaluation metrics
- [ ] Test inference examples
- [ ] Save model to backend
- [ ] Update backend configuration
- [ ] Test with backend API

## 🎉 Summary

This notebook provides a complete pipeline for:
1. ✅ Scraping real jobs from Telegram
2. ✅ Loading resume datasets
3. ✅ Creating weak labels automatically
4. ✅ Fine-tuning Sentence Transformers
5. ✅ Evaluating performance
6. ✅ Ready for production use

**Result:** A fine-tuned model specifically trained on Ethiopian job market data, ready to power your resume-job matching API!
