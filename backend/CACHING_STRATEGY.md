# Caching Strategy

## Overview

The system uses Redis for intelligent job caching with a **daily refresh strategy**. Jobs are scraped once per day and cached until the next day (UTC), preventing unnecessary Telegram API calls and improving response times.

## How It Works

### Daily Cache Lifecycle

```
Day 1 (2026-01-30):
├─ 09:00 - First user request
│  └─ Cache empty → Scrape jobs from Telegram
│  └─ Cache 104 jobs with date "2026-01-30"
│  └─ Set TTL to expire at end of day (23:59:59 UTC)
│
├─ 10:00 - Second user request
│  └─ Cache hit! Use cached jobs from 2026-01-30
│  └─ No scraping needed
│
├─ 15:00 - Third user request
│  └─ Cache hit! Use cached jobs from 2026-01-30
│  └─ No scraping needed
│
└─ 23:59:59 - Cache expires

Day 2 (2026-01-31):
├─ 08:00 - First user request
│  └─ Cache expired (new day) → Scrape fresh jobs
│  └─ Cache 108 jobs with date "2026-01-31"
│  └─ Set TTL to expire at end of day
│
└─ ... (cycle repeats)
```

## Key Features

### 1. Date-Based Validation
- Cache stores both jobs and the cache date
- On each request, checks if cache is from today (UTC)
- If cache is from yesterday, it's considered invalid

### 2. Automatic Expiration
- TTL calculated as seconds until end of day (UTC)
- Minimum 1 hour TTL as fallback
- Cache automatically expires at midnight UTC

### 3. No Redundant Scraping
- Multiple users on the same day share the same cache
- Telegram API is only called once per day
- Reduces rate limiting issues

### 4. Manual Refresh Option
- Admin endpoint `/refresh_jobs` forces cache refresh
- Useful for testing or urgent updates
- Clears old cache and scrapes fresh jobs

## Configuration

### Environment Variables

```env
# How many days back to scrape when refreshing
SCRAPE_DAYS_BACK=2

# Fallback TTL (not used with daily strategy)
CACHE_TTL_SECONDS=3600

# Redis connection
REDIS_URL=redis://localhost:6379/0
```

### Cache Keys

- `scraped_jobs`: Stores the job data (JSON)
- `scraped_jobs_date`: Stores the cache date (YYYY-MM-DD)

## API Endpoints

### Check Cache Status

```bash
GET /cache/info
```

**Response**:
```json
{
  "status": "active",
  "cache_date": "2026-01-30",
  "job_count": 104,
  "ttl_seconds": 11642,
  "is_valid": true,
  "message": "Cache from 2026-01-30 with 104 jobs"
}
```

**Possible Statuses**:
- `active`: Cache is valid and contains jobs
- `empty`: No cached jobs
- `unavailable`: Redis not connected

### Force Refresh

```bash
POST /refresh_jobs
```

Forces immediate scraping and cache refresh, regardless of cache validity.

## Implementation Details

### Cache Validation Logic

```python
async def _is_cache_valid(self) -> bool:
    """Check if cache is from today"""
    cache_date = await redis.get("scraped_jobs_date")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return cache_date == today
```

### TTL Calculation

```python
# Calculate seconds until end of day (UTC)
now = datetime.now(timezone.utc)
end_of_day = now.replace(hour=23, minute=59, second=59)
ttl = int((end_of_day - now).total_seconds())

# Use at least 1 hour as fallback
ttl = max(ttl, 3600)
```

### Cache Flow in Matching

```python
async def get_jobs():
    # Check cache first
    if cache.is_valid():
        return cache.get_jobs()  # Cache hit!
    
    # Cache miss - scrape new jobs
    jobs = await scraper.scrape_all_channels()
    
    # Store in cache with today's date
    await cache.set_jobs(jobs)
    
    return jobs
```

## Benefits

### For Users
- ✅ **Faster responses**: No waiting for scraping on most requests
- ✅ **Consistent results**: All users see same jobs throughout the day
- ✅ **Reliable service**: Less dependent on Telegram API availability

### For System
- ✅ **Reduced API calls**: 1 scrape/day instead of 1 scrape/request
- ✅ **Lower rate limiting**: Stays within Telegram API limits
- ✅ **Better performance**: Redis is much faster than scraping
- ✅ **Cost effective**: Fewer API calls = lower costs

### For Telegram
- ✅ **Respectful usage**: Doesn't spam their API
- ✅ **Sustainable**: Won't trigger rate limits or bans
- ✅ **Good citizen**: Follows best practices

## Monitoring

### Check Cache Health

```bash
# Get cache info
curl http://localhost:8000/cache/info

# Check system health (includes cache status)
curl http://localhost:8000/health
```

### Logs to Watch

```
✓ Connected to Redis
Cache hit: 104 jobs from 2026-01-30
Cached 104 jobs for 2026-01-30 (expires in 11642s)
Cache expired (new day) - need to refresh
```

## Troubleshooting

### Cache Not Working

**Symptom**: Every request scrapes jobs

**Solutions**:
1. Check Redis is running: `docker-compose ps redis`
2. Check Redis connection: `curl http://localhost:8000/health`
3. Check logs for Redis errors
4. Verify REDIS_URL in .env

### Cache Stuck on Old Date

**Symptom**: Cache shows yesterday's date

**Solutions**:
1. Force refresh: `curl -X POST http://localhost:8000/refresh_jobs`
2. Clear cache manually: `redis-cli DEL scraped_jobs scraped_jobs_date`
3. Restart services: `docker-compose restart`

### Jobs Not Updating

**Symptom**: Same jobs all day

**Expected Behavior**: This is normal! Cache refreshes daily.

**If you need fresh jobs**:
- Wait until next day (automatic)
- Use `/refresh_jobs` endpoint (manual)

## Performance Metrics

### Without Cache
- First request: ~4s (scraping)
- Second request: ~4s (scraping again)
- Third request: ~4s (scraping again)
- **Total for 3 requests**: ~12s

### With Cache
- First request: ~4s (scraping + caching)
- Second request: ~0.1s (cache hit)
- Third request: ~0.1s (cache hit)
- **Total for 3 requests**: ~4.2s (65% faster!)

### Scalability
- 100 users/day without cache: 100 scrapes = ~400s
- 100 users/day with cache: 1 scrape = ~4s (99% reduction!)

## Future Enhancements

### Possible Improvements
1. **Smart refresh**: Refresh cache at specific times (e.g., 6 AM)
2. **Partial updates**: Only scrape new posts, not all posts
3. **Multi-region cache**: Different cache per timezone
4. **Cache warming**: Pre-populate cache before first request
5. **Analytics**: Track cache hit rate and performance

### Advanced Features
1. **Incremental scraping**: Only fetch posts since last scrape
2. **Channel-specific TTL**: Different refresh rates per channel
3. **Priority refresh**: Refresh popular channels more often
4. **Predictive caching**: Pre-fetch based on usage patterns

## Best Practices

### For Development
- Use `/refresh_jobs` to test with fresh data
- Check `/cache/info` to verify cache state
- Monitor logs for cache hit/miss patterns

### For Production
- Set `SCRAPE_DAYS_BACK=2` for recent jobs
- Monitor Redis memory usage
- Set up Redis persistence (RDB/AOF)
- Use Redis Sentinel for high availability

### For Scaling
- Use Redis Cluster for distributed cache
- Implement cache warming on startup
- Add cache metrics to monitoring
- Set up alerts for cache failures

## Summary

The daily cache strategy provides:
- ✅ Optimal balance between freshness and performance
- ✅ Significant reduction in API calls
- ✅ Better user experience with faster responses
- ✅ Sustainable and respectful API usage
- ✅ Easy to monitor and troubleshoot

Jobs are fresh enough (updated daily) while avoiding unnecessary scraping on every request.
