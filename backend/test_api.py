"""
Test script for Resume-Job Matcher API
"""
import requests
import json
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:8000"

# Sample resume
SAMPLE_RESUME = """
Software Engineer with 5+ years of experience in Python, Django, and FastAPI.
Strong background in building scalable web applications and RESTful APIs.
Experience with Docker, Kubernetes, PostgreSQL, and Redis.
Proficient in machine learning with TensorFlow and PyTorch.
Bachelor's degree in Computer Science.
Excellent problem-solving and communication skills.
"""


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing /health endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    pprint(response.json())


def test_match_resume():
    """Test resume matching endpoint"""
    print("\n" + "="*60)
    print("Testing /match_resume endpoint")
    print("="*60)
    
    payload = {
        "resume_text": SAMPLE_RESUME,
        "threshold": 0.6,
        "max_results": 10
    }
    
    print(f"\nSending resume ({len(SAMPLE_RESUME)} chars)...")
    
    response = requests.post(
        f"{BASE_URL}/match_resume",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResults:")
        print(f"  Total jobs scraped: {data['total_jobs_scraped']}")
        print(f"  Total matches: {data['total_matches']}")
        print(f"  Processing time: {data['processing_time_seconds']}s")
        
        print(f"\nTop matches:")
        for i, match in enumerate(data['matches'][:5], 1):
            print(f"\n  {i}. {match['title']}")
            print(f"     Score: {match['score']:.3f}")
            print(f"     Channel: {match['source_channel']}")
            print(f"     Text: {match['job_text'][:100]}...")
    else:
        print(f"Error: {response.text}")


def test_refresh_jobs():
    """Test job refresh endpoint"""
    print("\n" + "="*60)
    print("Testing /refresh_jobs endpoint")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/refresh_jobs")
    print(f"Status: {response.status_code}")
    pprint(response.json())


if __name__ == "__main__":
    print("Resume-Job Matcher API Test Suite")
    print("="*60)
    
    try:
        # Test health
        test_health()
        
        # Test matching
        test_match_resume()
        
        # Uncomment to test refresh (rate limited)
        # test_refresh_jobs()
        
        print("\n" + "="*60)
        print("Tests completed!")
        print("="*60)
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the server is running: docker-compose up -d")
    except Exception as e:
        print(f"\n❌ Error: {e}")
