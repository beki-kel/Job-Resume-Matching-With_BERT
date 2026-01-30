"""Quick API test"""
import asyncio
import aiohttp


SAMPLE_RESUME = """
Software Engineer with 5+ years experience in Python, JavaScript, React, and Node.js.
Strong background in API development, database design, and cloud deployment using AWS and Docker.
Experience with FastAPI, Django, PostgreSQL, MongoDB, and Redis.
"""


async def test_api():
    """Test the API"""
    base_url = "http://localhost:8000"
    
    print("Testing Resume-Job Matcher API")
    print("=" * 60)
    
    # Health check
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/health") as response:
            data = await response.json()
            print(f"\n✓ Health: {data['status']}")
            print(f"  Model: {data['model_loaded']}")
            print(f"  Scraper: {data['scraper_ready']}")
            print(f"  Cache: {data['cache_ready']}")
        
        # Match resume
        print(f"\n✓ Matching resume...")
        payload = {
            "resume_text": SAMPLE_RESUME,
            "threshold": 0.5,
            "max_results": 5
        }
        
        async with session.post(
            f"{base_url}/match_resume",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            data = await response.json()
            print(f"  Jobs scraped: {data['total_jobs_scraped']}")
            print(f"  Matches found: {data['total_matches']}")
            print(f"  Processing time: {data['processing_time_seconds']}s")
            
            if data['matches']:
                print(f"\n  Top 3 matches:")
                for i, match in enumerate(data['matches'][:3], 1):
                    print(f"\n  {i}. {match['title']}")
                    print(f"     Score: {match['score']:.3f}")
                    print(f"     Channel: {match['source_channel']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_api())
