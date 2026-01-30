"""
Example client for Resume-Job Matcher API
Shows how to integrate the API into your application
"""
import requests
from typing import List, Dict, Optional


class ResumeMatcherClient:
    """Client for Resume-Job Matcher API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def match_resume(
        self,
        resume_text: str,
        threshold: float = 0.6,
        max_results: int = 20
    ) -> Dict:
        """
        Match resume with job posts
        
        Args:
            resume_text: User's resume text
            threshold: Minimum match score (0-1)
            max_results: Maximum results to return
        
        Returns:
            Dictionary with matches and metadata
        """
        payload = {
            "resume_text": resume_text,
            "threshold": threshold,
            "max_results": max_results
        }
        
        response = self.session.post(
            f"{self.base_url}/match_resume",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def get_top_matches(
        self,
        resume_text: str,
        top_n: int = 5,
        threshold: float = 0.6
    ) -> List[Dict]:
        """
        Get top N job matches
        
        Args:
            resume_text: User's resume
            top_n: Number of top matches
            threshold: Minimum score
        
        Returns:
            List of top matches
        """
        result = self.match_resume(resume_text, threshold, top_n)
        return result['matches']
    
    def refresh_jobs(self) -> Dict:
        """Force refresh job cache"""
        response = self.session.post(f"{self.base_url}/refresh_jobs")
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ResumeMatcherClient("http://localhost:8000")
    
    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Model loaded: {health['model_loaded']}")
    
    # Sample resume
    resume = """
    Senior Software Engineer with 7 years of experience.
    Expert in Python, Django, FastAPI, and microservices architecture.
    Strong background in cloud technologies (AWS, Docker, Kubernetes).
    Experience with machine learning and data engineering.
    Led teams of 5+ developers on multiple projects.
    MSc in Computer Science from top university.
    """
    
    # Get matches
    print("\nFinding job matches...")
    result = client.match_resume(resume, threshold=0.65, max_results=10)
    
    print(f"\nFound {result['total_matches']} matches from {result['total_jobs_scraped']} jobs")
    print(f"Processing time: {result['processing_time_seconds']}s")
    
    # Display top matches
    print("\nTop 5 matches:")
    for i, match in enumerate(result['matches'][:5], 1):
        print(f"\n{i}. {match['title']}")
        print(f"   Score: {match['score']:.2%}")
        print(f"   Channel: {match['source_channel']}")
        print(f"   Preview: {match['job_text'][:150]}...")
    
    # Get only top 3
    print("\n" + "="*60)
    print("Getting top 3 matches only...")
    top_3 = client.get_top_matches(resume, top_n=3, threshold=0.7)
    
    for i, match in enumerate(top_3, 1):
        print(f"\n{i}. {match['title']} - {match['score']:.2%}")
