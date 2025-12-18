# src/handlers/http_handler.py
"""
HTTP Handler - Handles HTTP endpoints
"""

import logging
from datetime import datetime
from typing import List
from fastapi import UploadFile

from ..services import get_resume_service
from ..models import (
    ResumeMatch,
    UploadJobResponse,
    SearchMatchesRequest,
    AnalyzeJobRequest,
    GenerateResumeRequest,
)
from ..core.exceptions import FileUploadException

logger = logging.getLogger(__name__)


class HTTPHandler:
    """Handler for HTTP endpoints"""
    
    def __init__(self):
        self.resume_service = get_resume_service()
    
    async def handle_file_upload(self, file: UploadFile) -> UploadJobResponse:
        """Handle job description file upload"""
        
        try:
            logger.info(f"Processing uploaded file: {file.filename}")
            
            # Read file content
            content = await file.read()
            job_description = content.decode('utf-8')
            
            # Search for matching resumes
            search_request = SearchMatchesRequest(
                job_description=job_description,
                top_k=5
            )
            
            result = await self.resume_service.search_matching_resumes(
                search_request
            )
            
            return UploadJobResponse(
                status="success",
                job_description=job_description,
                matches=result.matches,
                upload_time=datetime.now()
            )
        
        except UnicodeDecodeError as e:
            logger.error(f"File encoding error: {e}")
            raise FileUploadException(
                "Unable to decode file. Please ensure it's a text file with UTF-8 encoding."
            )
        
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise FileUploadException(str(e))
    
    async def handle_search_matches(
        self,
        request: SearchMatchesRequest
    ):
        """Handle resume search request"""
        
        logger.info(f"Searching for {request.top_k} matching resumes")
        
        result = await self.resume_service.search_matching_resumes(request)
        
        return {
            "success": True,
            "data": {
                "matches": [match.dict() for match in result.matches],
                "total_found": result.total_found
            }
        }
    
    async def handle_analyze_job(self, request: AnalyzeJobRequest):
        """Handle job description analysis request"""
        
        logger.info("Analyzing job description")
        
        analysis = await self.resume_service.analyze_job_description(
            request.job_description
        )
        
        return {
            "success": True,
            "data": analysis.dict()
        }
    
    async def handle_generate_resume(
        self,
        request: GenerateResumeRequest
    ):
        """Handle resume generation request (non-streaming)"""
        
        logger.info("Generating resume (non-streaming)")
        
        # Generate resume
        resume_chunks = []
        async for chunk in self.resume_service.generate_optimized_resume(
            request.job_description,
            request.matched_resumes,
            stream=False
        ):
            resume_chunks.append(chunk)
        
        resume = "".join(resume_chunks)
        
        return {
            "success": True,
            "data": {
                "resume": resume,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    async def stream_resume_generation(
        self,
        job_description: str,
        matched_resumes: List[ResumeMatch]
    ):
        """Stream resume generation (yields chunks)"""
        
        logger.info("Streaming resume generation")
        
        async for chunk in self.resume_service.generate_optimized_resume(
            job_description,
            matched_resumes,
            stream=True
        ):
            yield chunk


# Singleton instance
_http_handler = None


def get_http_handler() -> HTTPHandler:
    """Get HTTP handler instance (singleton)"""
    global _http_handler
    
    if _http_handler is None:
        _http_handler = HTTPHandler()
    
    return _http_handler