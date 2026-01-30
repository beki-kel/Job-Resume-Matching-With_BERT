"""Text processing utilities"""
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


def clean_resume(text: str) -> str:
    """
    Clean user-submitted resume by removing PII and normalizing format
    More aggressive cleaning than clean_text for privacy
    
    Args:
        text: Raw resume text
    
    Returns:
        Cleaned resume text with PII removed
    """
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers (various formats)
    phone_patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\d{10,}',  # Long digit sequences
    ]
    for pattern in phone_patterns:
        text = re.sub(pattern, '[PHONE]', text)
    
    # Remove physical addresses (basic patterns)
    text = re.sub(r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|court|ct|circle|cir|way)\.?\s*,?\s*[\w\s]+,?\s*[A-Z]{2}\s*\d{5}', '[ADDRESS]', text, flags=re.IGNORECASE)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', text)
    
    # Remove LinkedIn/social media profiles
    text = re.sub(r'(?i)linkedin\.com/\S+', '[LINKEDIN]', text)
    text = re.sub(r'(?i)github\.com/\S+', '[GITHUB]', text)
    text = re.sub(r'(?i)twitter\.com/\S+', '[TWITTER]', text)
    
    # Remove dates of birth (various formats)
    text = re.sub(r'\b(?:DOB|Date of Birth|Born)[:\s]+\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', '[DOB]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b', '[DATE]', text)  # Generic dates
    
    # Remove social security numbers (US format)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!?]{2,}', '.', text)
    text = re.sub(r'\.{3,}', '...', text)
    
    return text.strip()


def extract_job_title(text: str) -> str:
    """
    Extract job title from job post text using heuristics
    
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
