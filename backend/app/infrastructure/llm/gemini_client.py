"""Gemini LLM client using REST API"""
import logging
from typing import Optional
import requests
import json

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._initialized = False
    
    def initialize(self):
        """Initialize Gemini client"""
        try:
            # Test the API with a simple request
            test_url = f"{self.base_url}/models/{self.model_name}?key={self.api_key}"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                self._initialized = True
                logger.info(f"✓ Gemini client initialized ({self.model_name})")
            else:
                logger.error(f"Gemini API test failed: {response.status_code} - {response.text}")
                raise RuntimeError(f"Gemini API test failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        """
        if not self._initialized:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                raise RuntimeError(f"Gemini API error: {response.status_code}")
            
            result = response.json()
            
            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            raise RuntimeError("Unexpected response format from Gemini API")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if client is initialized"""
        return self._initialized
