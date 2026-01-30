"""PDF processing utilities"""
import logging
from typing import Optional
import PyPDF2
import pdfplumber
from io import BytesIO

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Extract text from PDF files"""
    
    @staticmethod
    def extract_text_pypdf2(pdf_bytes: bytes) -> str:
        """Extract text using PyPDF2"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    @staticmethod
    def extract_text_pdfplumber(pdf_bytes: bytes) -> str:
        """Extract text using pdfplumber (better for complex layouts)"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            text = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""
    
    @classmethod
    def extract_text(cls, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF using multiple methods
        
        Args:
            pdf_bytes: PDF file bytes
        
        Returns:
            Extracted text
        """
        # Try pdfplumber first (better quality)
        text = cls.extract_text_pdfplumber(pdf_bytes)
        
        # Fallback to PyPDF2 if pdfplumber fails
        if not text or len(text) < 50:
            logger.info("Falling back to PyPDF2")
            text = cls.extract_text_pypdf2(pdf_bytes)
        
        if not text:
            raise ValueError("Failed to extract text from PDF")
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
