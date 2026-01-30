"""Matching service - business logic for resume-job matching"""
import logging
import torch
from datetime import datetime
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity

from app.domain.models import MatchResult
from app.utils import clean_resume, extract_job_title
from app.infrastructure.ml import ModelLoader

logger = logging.getLogger(__name__)


class MatchingService:
    """Service for matching resumes with jobs"""
    
    def __init__(self, model_loader: ModelLoader, resume_service=None):
        self.model_loader = model_loader
        self.resume_service = resume_service  # Optional for LLM explanations
    
    def match_resume_with_jobs(
        self,
        resume_text: str,
        jobs: List[Dict],
        threshold: float = 0.6,
        max_results: int = 20,
        generate_explanations: bool = False
    ) -> List[MatchResult]:
        """
        Match resume with jobs using the loaded model
        
        Args:
            resume_text: Raw resume text
            jobs: List of job dictionaries
            threshold: Minimum score threshold
            max_results: Maximum results to return
            generate_explanations: Generate LLM explanations for matches
        
        Returns:
            List of match results
        """
        if not self.model_loader.is_loaded():
            raise RuntimeError("Model not loaded")
        
        # Clean resume
        resume_clean = clean_resume(resume_text)
        logger.info(f"Resume cleaned: {len(resume_text)} -> {len(resume_clean)} chars")
        
        model = self.model_loader.get_model()
        
        # Check if it's a Sentence Transformer
        if self.model_loader.is_sentence_transformer:
            matches = self._match_with_sentence_transformer(
                model, resume_clean, jobs, threshold, max_results
            )
        else:
            matches = self._match_with_classification_model(
                model, 
                self.model_loader.get_tokenizer(),
                self.model_loader.get_device(),
                resume_clean, 
                jobs, 
                threshold, 
                max_results
            )
        
        # Generate explanations if requested and LLM is available
        if generate_explanations and self.resume_service:
            matches = self._add_explanations(matches, resume_clean)
        
        return matches
    
    def _add_explanations(
        self,
        matches: List[MatchResult],
        resume_text: str
    ) -> List[MatchResult]:
        """Add LLM-generated explanations to top matches"""
        # Only explain top 5 matches to save API calls
        for match in matches[:5]:
            try:
                explanation = self.resume_service.generate_job_explanation(
                    resume_text,
                    match.job_text,
                    match.score
                )
                match.explanation = explanation
            except Exception as e:
                logger.warning(f"Failed to generate explanation: {e}")
                match.explanation = None
        
        return matches
    
    def _match_with_sentence_transformer(
        self,
        model,
        resume_clean: str,
        jobs: List[Dict],
        threshold: float,
        max_results: int
    ) -> List[MatchResult]:
        """Match using Sentence Transformer (cosine similarity)"""
        matches = []
        
        # Encode resume once
        resume_embedding = model.encode([resume_clean])
        
        for job in jobs:
            try:
                # Encode job
                job_embedding = model.encode([job['text']])
                
                # Compute cosine similarity
                score = cosine_similarity(resume_embedding, job_embedding)[0][0]
                score = float(score)
                score = max(0.0, min(1.0, score))  # Clip to [0, 1]
                
                # Filter by threshold
                if score >= threshold:
                    matches.append(MatchResult(
                        job_text=job['text'],
                        score=score,
                        source_channel=job['channel'],
                        title=extract_job_title(job['text']),
                        scraped_at=job['scraped_at'],
                        message_link=job.get('message_link', ''),
                        explanation=None
                    ))
            
            except Exception as e:
                logger.warning(f"Error processing job: {e}")
                continue
        
        # Sort by score descending
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results
        return matches[:max_results]
    
    def _match_with_classification_model(
        self,
        model,
        tokenizer,
        device,
        resume_clean: str,
        jobs: List[Dict],
        threshold: float,
        max_results: int
    ) -> List[MatchResult]:
        """Match using classification model"""
        matches = []
        
        for job in jobs:
            try:
                # Format input pair
                input_text = self._format_input_pair(job['text'], resume_clean)
                
                # Tokenize
                inputs = tokenizer(
                    input_text,
                    padding='max_length',
                    truncation=True,
                    max_length=512,
                    return_tensors='pt'
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                # Inference
                with torch.no_grad():
                    outputs = model(**inputs)
                    score = torch.sigmoid(outputs.logits).item()
                    score = max(0.0, min(1.0, score))
                
                # Filter by threshold
                if score >= threshold:
                    matches.append(MatchResult(
                        job_text=job['text'],
                        score=score,
                        source_channel=job['channel'],
                        title=extract_job_title(job['text']),
                        scraped_at=job['scraped_at'],
                        message_link=job.get('message_link', ''),
                        explanation=None
                    ))
            
            except Exception as e:
                logger.warning(f"Error processing job: {e}")
                continue
        
        # Sort by score descending
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results
        return matches[:max_results]
    
    @staticmethod
    def _format_input_pair(job_text: str, resume_text: str) -> str:
        """Format job-resume pair for classification model"""
        max_jd_len = 300
        max_resume_len = 300
        
        if len(job_text) > max_jd_len:
            job_text = job_text[:max_jd_len] + "..."
        
        if len(resume_text) > max_resume_len:
            resume_text = resume_text[:max_resume_len] + "..."
        
        return f"For the given job description <<{job_text}>> the resume: <<{resume_text}>>. The result is,"
