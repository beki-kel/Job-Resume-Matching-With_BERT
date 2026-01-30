"""Resume processing routes"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional

from app.domain.schemas import ResumeProcessRequest, ResumeProcessResponse
from app.services.resume_service import ResumeService
from app.api.dependencies import get_resume_service
from app.utils.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resume"])


@router.post("/process_resume", response_model=ResumeProcessResponse)
async def process_resume(
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    resume_service: ResumeService = Depends(get_resume_service)
):
    """
    Process resume with LLM to extract key information and provide feedback
    
    Accepts either:
    - resume_text: Plain text resume
    - resume_file: PDF file upload
    
    Returns:
    - Processed resume (PII removed)
    - Quality score (1-10)
    - Strengths and improvement suggestions
    - Key skills extracted
    """
    try:
        # Get resume text from either source
        if resume_file:
            if not resume_file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are supported"
                )
            
            pdf_bytes = await resume_file.read()
            resume_text = PDFProcessor.extract_text(pdf_bytes)
            logger.info(f"Extracted text from PDF: {resume_file.filename}")
        
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Either resume_text or resume_file must be provided"
            )
        
        if len(resume_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text is too short (minimum 50 characters)"
            )
        
        # Process resume with LLM
        result = resume_service.process_resume(resume_text)
        
        return ResumeProcessResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
