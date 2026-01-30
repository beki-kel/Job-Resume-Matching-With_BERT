"""Resume processing service with LLM enhancement"""
import logging
import json
from typing import Dict, Any

from app.infrastructure.llm import GeminiClient
from app.utils.text_processing import clean_resume

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for processing and enhancing resumes with LLM"""
    
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
    
    def process_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Process resume with LLM to extract key information and provide feedback
        
        Args:
            resume_text: Raw resume text
        
        Returns:
            Dictionary with processed resume, score, and suggestions
        """
        if not self.gemini_client.is_initialized():
            raise RuntimeError("Gemini client not initialized")
        
        prompt = self._build_resume_processing_prompt(resume_text)
        
        try:
            response = self.gemini_client.generate(prompt)
            result = self._parse_llm_response(response)
            
            # Add cleaned version for matching
            result['cleaned_for_matching'] = clean_resume(result['processed_resume'])
            
            logger.info(f"Resume processed - Score: {result['score']}/10")
            return result
        
        except Exception as e:
            logger.error(f"Resume processing failed: {e}")
            # Fallback to basic cleaning
            return {
                'processed_resume': clean_resume(resume_text),
                'cleaned_for_matching': clean_resume(resume_text),
                'score': 5,
                'strengths': ['Resume submitted successfully'],
                'improvements': ['LLM processing unavailable - using basic cleaning'],
                'key_skills': [],
                'experience_years': 'Unknown'
            }
    
    def _build_resume_processing_prompt(self, resume_text: str) -> str:
        """Build prompt for resume processing"""
        return f"""Analyze this resume and provide feedback in STRICT JSON format.

RESUME:
{resume_text}

INSTRUCTIONS:
1. Create a SHORT summary (max 200 words) of professional experience WITHOUT personal info (no names, emails, phones, addresses)
2. Rate quality 1-10
3. List 3-5 key strengths
4. List 3-5 improvements
5. Extract 5-10 key technical skills
6. Estimate years of experience

OUTPUT ONLY THIS JSON (no markdown, no extra text):
{{
  "processed_resume": "Brief professional summary without PII",
  "score": 8,
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "improvements": ["Improvement 1", "Improvement 2", "Improvement 3"],
  "key_skills": ["Skill1", "Skill2", "Skill3"],
  "experience_years": "5+"
}}"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Try to parse JSON
            try:
                result = json.loads(response.strip())
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON object using regex
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON object found in response")
            
            # Validate required fields
            required_fields = ['processed_resume', 'score', 'strengths', 'improvements']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure score is in range
            result['score'] = max(1, min(10, int(result['score'])))
            
            # Ensure lists
            if not isinstance(result['strengths'], list):
                result['strengths'] = [str(result['strengths'])]
            if not isinstance(result['improvements'], list):
                result['improvements'] = [str(result['improvements'])]
            if 'key_skills' not in result:
                result['key_skills'] = []
            if not isinstance(result['key_skills'], list):
                result['key_skills'] = [str(result['key_skills'])]
            if 'experience_years' not in result:
                result['experience_years'] = 'Unknown'
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.error(f"Full response: {response}")
            raise ValueError(f"Invalid response from LLM: {str(e)}")
    
    def generate_job_explanation(
        self,
        resume_text: str,
        job_text: str,
        score: float
    ) -> str:
        """
        Generate detailed explanation of job-resume match
        
        Args:
            resume_text: Resume text
            job_text: Job description
            score: Match score
        
        Returns:
            Detailed explanation
        """
        if not self.gemini_client.is_initialized():
            return self._fallback_explanation(score)
        
        prompt = f"""You are a career advisor. Explain why this resume matches (or doesn't match) this job posting.

RESUME SUMMARY:
{resume_text[:500]}...

JOB POSTING:
{job_text[:500]}...

MATCH SCORE: {score:.2f} (0-1 scale, where 1 is perfect match)

Provide a clear, concise explanation (2-3 sentences) covering:
1. Why this score was given
2. Key matching skills/experience
3. What's missing (if score < 0.7)

Keep it professional and actionable. No JSON, just plain text."""
        
        try:
            explanation = self.gemini_client.generate(prompt)
            return explanation.strip()
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return self._fallback_explanation(score)
    
    @staticmethod
    def _fallback_explanation(score: float) -> str:
        """Fallback explanation when LLM is unavailable"""
        if score >= 0.7:
            return f"Strong match ({score:.0%}). Your skills and experience align well with this position."
        elif score >= 0.5:
            return f"Moderate match ({score:.0%}). Some relevant skills, but may need additional qualifications."
        else:
            return f"Weak match ({score:.0%}). Limited alignment with required qualifications."
