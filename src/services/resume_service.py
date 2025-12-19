# src/services/resume_service.py
"""
Resume Service - High-level business logic for resume operations
"""

import logging
from typing import List, AsyncIterator, cast
from collections.abc import AsyncGenerator

from .llm_service import get_llm_service
from .vector_service import get_vector_service
from ..schemas import (
    ResumeMatch,
    JobAnalysis,
    SearchMatchesRequest,
    SearchMatchesResponse,
)

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for resume-related operations"""
    
    def __init__(self):
        self.llm_service = get_llm_service()
        self.vector_service = get_vector_service()
    
    async def search_matching_resumes(
        self,
        request: SearchMatchesRequest
    ) -> SearchMatchesResponse:
        """Search for resumes matching the job description"""
        
        logger.info(f"Searching for top {request.top_k} matching resumes")
        
        # Generate embedding for job description
        query_embedding = await self.vector_service.embed_text(
            request.job_description
        )
        
        # Search for similar resumes
        matches = await self.vector_service.similarity_search(
            query_embedding,
            top_k=request.top_k
        )
        
        logger.info(f"Found {len(matches)} matching resumes")
        
        return SearchMatchesResponse(
            matches=matches,
            total_found=len(matches)
        )
    
    async def analyze_job_description(
        self,
        job_description: str
    ) -> JobAnalysis:
        """Analyze job description to extract key information"""
        
        logger.info("Analyzing job description")
        
        # Use LLM to analyze the job description
        analysis_data = await self.llm_service.analyze_text(job_description)
        
        return JobAnalysis(
            required_skills=analysis_data.get("required_skills", []),
            experience_level=analysis_data.get("experience_level", "Mid"),
            key_responsibilities=analysis_data.get("key_responsibilities", []),
            estimated_match_threshold=analysis_data.get(
                "estimated_match_threshold",
                0.7
            )
        )
    
    async def generate_optimized_resume(
        self,
        job_description: str,
        matched_resumes: List[ResumeMatch],
        stream: bool = True
    ) -> AsyncIterator[str]:
        """Generate an optimized resume based on job description and matches"""
        
        logger.info(
            f"Generating resume for {len(matched_resumes)} matched profiles"
        )
        
        # Use LLM to generate resume
        # generate_resume is an async generator function (uses yield)
        # When called, it returns an async generator object directly, not a coroutine
        # We need to cast to help the type checker understand this
        resume_generator = cast(
            AsyncGenerator[str, None],
            self.llm_service.generate_resume(
                job_description,
                matched_resumes,
                stream=stream
            )
        )
        async for chunk in resume_generator:
            yield chunk
        
        logger.info("Resume generation complete")
    
    async def process_job_description_workflow(
        self,
        job_description: str,
        top_k: int = 5
    ) -> tuple[JobAnalysis, List[ResumeMatch], str]:
        """
        Complete workflow: analyze → search → generate
        Returns: (analysis, matches, generated_resume)
        """
        
        logger.info("Starting complete job description workflow")
        
        # Step 1: Analyze job description
        analysis = await self.analyze_job_description(job_description)
        
        # Step 2: Search for matching resumes
        search_result = await self.search_matching_resumes(
            SearchMatchesRequest(
                job_description=job_description,
                top_k=top_k
            )
        )
        
        # Step 3: Generate resume (non-streaming for complete workflow)
        resume_chunks = []
        async for chunk in self.generate_optimized_resume(
            job_description,
            search_result.matches,
            stream=False
        ):
            resume_chunks.append(chunk)
        
        generated_resume = "".join(resume_chunks)
        
        logger.info("Complete workflow finished")
        
        return analysis, search_result.matches, generated_resume


# Singleton instance
_resume_service = None


def get_resume_service() -> ResumeService:
    """Get resume service instance (singleton)"""
    global _resume_service
    
    if _resume_service is None:
        _resume_service = ResumeService()
    
    return _resume_service