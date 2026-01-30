"""
Utility functions for text processing and job extraction
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean text by removing URLs, emojis, extra whitespace
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove Telegram usernames
    text = re.sub(r'@\w+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers (basic pattern)
    text = re.sub(r'\+?\d[\d\s\-\(\)]{7,}\d', '', text)
    
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common signatures/footers
    signature_patterns = [
        r'(?i)sent from.*',
        r'(?i)forwarded from.*',
        r'(?i)join us.*',
        r'(?i)follow us.*',
        r'(?i)subscribe.*'
    ]
    for pattern in signature_patterns:
        text = re.sub(pattern, '', text)
    
    return text.strip()


def is_job_related(text: str, keywords: List[str]) -> bool:
    """
    Check if text is job-related based on keywords
    
    Args:
        text: Text to check
        keywords: List of job-related keywords
    
    Returns:
        True if job-related
    """
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def extract_job_title(text: str) -> str:
    """
    Extract job title from job post text
    Uses heuristics to find title
    
    Args:
        text: Job post text
    
    Returns:
        Extracted title or fallback
    """
    # Common patterns for job titles
    patterns = [
        r'(?i)position[:\s]+([^\n\.]{5,50})',
        r'(?i)vacancy[:\s]+([^\n\.]{5,50})',
        r'(?i)hiring[:\s]+([^\n\.]{5,50})',
        r'(?i)job title[:\s]+([^\n\.]{5,50})',
        r'(?i)role[:\s]+([^\n\.]{5,50})',
        r'(?i)we are looking for[:\s]+([^\n\.]{5,50})',
        r'(?i)wanted[:\s]+([^\n\.]{5,50})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            title = match.group(1).strip()
            # Clean up
            title = re.sub(r'[^\w\s\-/]', '', title)
            if len(title) > 5:
                return title[:100]  # Limit length
    
    # Fallback: use first line if short enough
    first_line = text.split('\n')[0].strip()
    if 5 < len(first_line) < 100:
        return first_line
    
    return "Job Opening"


def format_input_pair(job_text: str, resume_text: str) -> str:
    """
    Format job-resume pair in dataset style for inference
    
    Dataset format:
    "For the given job description <<JD>> the resume: <<resume>>. The result is, [label]"
    
    Args:
        job_text: Job description
        resume_text: Resume text
    
    Returns:
        Formatted input string
    """
    # Truncate if too long (to fit in 512 tokens)
    max_jd_len = 300
    max_resume_len = 300
    
    if len(job_text) > max_jd_len:
        job_text = job_text[:max_jd_len] + "..."
    
    if len(resume_text) > max_resume_len:
        resume_text = resume_text[:max_resume_len] + "..."
    
    # Format in dataset style
    formatted = f"For the given job description <<{job_text}>> the resume: <<{resume_text}>>. The result is,"
    
    return formatted
