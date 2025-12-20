"""
FastMCP Server for Resume Matching and Generation

This is the main MCP server using FastMCP framework with:
- @mcp.tool decorators for tools
- @mcp.resource decorators for resources
- @mcp.prompt decorators for prompts
"""

import json
import logging
import base64
from typing import List, Optional
from datetime import datetime

from fastmcp import FastMCP
from fastmcp.server import Context

from .config import settings
from .services import (
    get_resume_service,
    get_vector_service,
)
from .utils import DocumentParser
from .schemas import (
    ResumeMatch,
    JobAnalysis,
    SearchMatchesRequest,
    GenerateResumeRequest,
)
from .core.exceptions import FileUploadException

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name=settings.app_name,
    version=settings.app_version,
    host=settings.host,
    port=settings.port,
    log_level=settings.log_level,
    debug=settings.debug,
)

# Initialize services (singleton pattern)
resume_service = get_resume_service()
vector_service = get_vector_service()
document_parser = DocumentParser()

# In-memory storage for job descriptions and matches
_job_descriptions: dict[str, dict] = {}
_matched_resumes: dict[str, List[ResumeMatch]] = {}


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
async def upload_job_description(
    input_data: str,
    input_type: str = "text",
    filename: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Upload a job description from text, file (base64), or URL.
    
    Args:
        input_data: Job description text, base64-encoded file, or URL
        input_type: Type of input - "text", "file", or "url"
        filename: Optional filename for file type (required for file type)
        ctx: FastMCP context for logging (automatically injected)
    
    Returns:
        JSON string with upload status and job description ID
    """
    try:
        if ctx:
            await ctx.info(f"Uploading job description (type: {input_type})")
        else:
            logger.info(f"Uploading job description (type: {input_type})")
        
        # Parse input based on type
        if input_type == "url":
            if not settings.allow_url_uploads:
                raise ValueError("URL uploads are not enabled")
            if ctx:
                await ctx.debug(f"Parsing URL: {input_data[:100]}...")
            job_description_text = await document_parser.parse(input_data, is_url=True)
            job_id = f"job_{datetime.now().isoformat()}"
        elif input_type == "file":
            if not filename:
                raise ValueError("filename is required for file type")
            if ctx:
                await ctx.debug(f"Processing file: {filename}")
            # Decode base64 file
            try:
                file_bytes = base64.b64decode(input_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {e}")
            
            # Validate file size
            if len(file_bytes) > settings.max_upload_size:
                raise ValueError(f"File size exceeds maximum of {settings.max_upload_size} bytes")
            
            # Parse file
            job_description_text = await document_parser.parse(
                file_bytes, filename, False
            )
            job_id = f"job_{datetime.now().isoformat()}"
        else:
            # Text input
            job_description_text = input_data
            job_id = f"job_{datetime.now().isoformat()}"
        
        if not job_description_text.strip():
            raise ValueError("Job description cannot be empty")
        
        # Store job description
        _job_descriptions[job_id] = {
            "id": job_id,
            "text": job_description_text,
            "uploaded_at": datetime.now().isoformat(),
            "input_type": input_type,
        }
        
        if ctx:
            await ctx.info(f"Job description uploaded with ID: {job_id}")
        else:
            logger.info(f"Job description uploaded with ID: {job_id}")
        
        return json.dumps({
            "status": "success",
            "job_id": job_id,
            "message": "Job description uploaded successfully",
            "text_preview": job_description_text[:200] + "..." if len(job_description_text) > 200 else job_description_text
        }, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Upload failed: {e}")
        else:
            logger.error(f"Upload failed: {e}")
        raise FileUploadException(str(e))


@mcp.tool()
async def search_matching_resumes(
    job_description: str,
    top_k: int = 5,
    ctx: Optional[Context] = None
) -> str:
    """
    Search for resumes that match a job description using vector similarity.
    
    Args:
        job_description: The job description text to match against
        top_k: Number of top matches to return (1-20, default: 5)
        ctx: FastMCP context for logging (automatically injected)
    
    Returns:
        JSON string with matching resumes and similarity scores
    """
    try:
        if not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if not (1 <= top_k <= 20):
            raise ValueError("top_k must be between 1 and 20")
        
        if ctx:
            await ctx.info(f"Searching for top {top_k} matching resumes")
            await ctx.debug(f"Job description length: {len(job_description)} characters")
        else:
            logger.info(f"Searching for top {top_k} matching resumes")
        
        # Create search request
        request = SearchMatchesRequest(
            job_description=job_description,
            top_k=top_k
        )
        
        # Execute search
        if ctx:
            await ctx.debug("Generating embeddings and performing similarity search...")
        result = await resume_service.search_matching_resumes(request)
        
        # Store matches for later reference
        job_id = f"search_{datetime.now().isoformat()}"
        _matched_resumes[job_id] = result.matches
        
        if ctx:
            await ctx.info(f"Found {len(result.matches)} matches")
        else:
            logger.info(f"Found {len(result.matches)} matches")
        
        return json.dumps({
            "status": "success",
            "job_id": job_id,
            "matches": [match.dict() for match in result.matches],
            "total_found": result.total_found
        }, indent=2, default=str)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Search failed: {e}")
        else:
            logger.error(f"Search failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@mcp.tool()
async def list_matched_job_descriptions(ctx: Optional[Context] = None) -> str:
    """
    List all uploaded job descriptions with their match status.
    
    Args:
        ctx: FastMCP context for logging (automatically injected)
    
    Returns:
        JSON string with list of job descriptions
    """
    try:
        if ctx:
            await ctx.info("Listing job descriptions")
        else:
            logger.info("Listing job descriptions")
        
        job_list = []
        for job_id, job_data in _job_descriptions.items():
            matches = _matched_resumes.get(job_id, [])
            job_list.append({
                "job_id": job_id,
                "text_preview": job_data["text"][:100] + "..." if len(job_data["text"]) > 100 else job_data["text"],
                "uploaded_at": job_data["uploaded_at"],
                "input_type": job_data["input_type"],
                "has_matches": len(matches) > 0,
                "match_count": len(matches)
            })
        
        if ctx:
            await ctx.debug(f"Found {len(job_list)} job descriptions")
        
        return json.dumps({
            "status": "success",
            "total_jobs": len(job_list),
            "jobs": job_list
        }, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"List failed: {e}")
        else:
            logger.error(f"List failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@mcp.tool()
async def analyze_job_description(
    job_description: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Analyze a job description to extract key requirements and skills.
    
    Args:
        job_description: The job description text to analyze
        ctx: FastMCP context for logging (automatically injected)
    
    Returns:
        JSON string with extracted information
    """
    try:
        if not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if ctx:
            await ctx.info("Analyzing job description")
            await ctx.debug("Using LLM to extract key requirements")
        else:
            logger.info("Analyzing job description")
        
        # Execute analysis
        analysis = await resume_service.analyze_job_description(job_description)
        
        if ctx:
            await ctx.info("Analysis complete")
        
        return json.dumps({
            "status": "success",
            "analysis": analysis.dict()
        }, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Analysis failed: {e}")
        else:
            logger.error(f"Analysis failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@mcp.tool()
async def generate_resume(
    job_description: str,
    matched_resumes: List[dict],
    stream: bool = False,
    ctx: Optional[Context] = None
) -> str:
    """
    Generate an optimized resume based on job description and matched profiles.
    
    Args:
        job_description: The job description to tailor the resume for
        matched_resumes: List of matched resume profiles (as dicts)
        stream: Whether to stream the response (not supported in MCP tools, use resource instead)
        ctx: FastMCP context for logging (automatically injected)
    
    Returns:
        Generated resume text in markdown format
    """
    try:
        if not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if not matched_resumes:
            raise ValueError("matched_resumes cannot be empty")
        
        # Convert dicts to ResumeMatch objects
        resume_matches = []
        for resume_data in matched_resumes:
            try:
                resume_matches.append(ResumeMatch(**resume_data))
            except Exception as e:
                raise ValueError(f"Invalid resume data format: {e}")
        
        if ctx:
            await ctx.info(f"Generating resume for {len(resume_matches)} matched profiles")
            await ctx.debug("Building prompt and calling LLM service")
        else:
            logger.info(f"Generating resume for {len(resume_matches)} matched profiles")
        
        # Generate resume (non-streaming for tool response)
        resume_chunks = []
        chunk_count = 0
        async for chunk in resume_service.generate_optimized_resume(
            job_description,
            resume_matches,
            stream=False
        ):
            resume_chunks.append(chunk)
            chunk_count += 1
            if ctx and chunk_count % 10 == 0:
                await ctx.debug(f"Generated {chunk_count} chunks...")
        
        resume_text = "".join(resume_chunks)
        
        if ctx:
            await ctx.info(f"Resume generation complete ({len(resume_text)} characters)")
        else:
            logger.info("Resume generation complete")
        
        return resume_text
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Generation failed: {e}")
        else:
            logger.error(f"Generation failed: {e}")
        raise Exception(f"Failed to generate resume: {str(e)}")


# ============================================================================
# MCP RESOURCES
# ============================================================================

@mcp.resource("resume://matches/{job_id}")
async def matched_resumes_resource(job_id: str, ctx: Optional[Context] = None) -> str:
    """
    Resource for accessing matched resumes by job ID.
    
    URI format: resume://matches/{job_id}
    
    Args:
        job_id: Job description ID
        ctx: FastMCP context for logging (automatically injected)
    """
    try:
        if ctx:
            await ctx.debug(f"Accessing matches for job_id: {job_id}")
        
        if job_id not in _matched_resumes:
            if ctx:
                await ctx.warning(f"No matches found for job_id: {job_id}")
            return json.dumps({
                "status": "error",
                "message": f"No matches found for job_id: {job_id}"
            })
        
        matches = _matched_resumes[job_id]
        
        if ctx:
            await ctx.info(f"Retrieved {len(matches)} matches for job_id: {job_id}")
        
        return json.dumps({
            "status": "success",
            "job_id": job_id,
            "matches": [match.dict() for match in matches],
            "total": len(matches)
        }, indent=2, default=str)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Resource access failed: {e}")
        else:
            logger.error(f"Resource access failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@mcp.resource("resume://job/{job_id}")
async def job_description_resource(job_id: str, ctx: Optional[Context] = None) -> str:
    """
    Resource for accessing job descriptions by ID.
    
    URI format: resume://job/{job_id}
    
    Args:
        job_id: Job description ID
        ctx: FastMCP context for logging (automatically injected)
    """
    try:
        if ctx:
            await ctx.debug(f"Accessing job description for job_id: {job_id}")
        
        if job_id not in _job_descriptions:
            if ctx:
                await ctx.warning(f"Job description not found: {job_id}")
            return json.dumps({
                "status": "error",
                "message": f"Job description not found: {job_id}"
            })
        
        job_data = _job_descriptions[job_id]
        
        if ctx:
            await ctx.info(f"Retrieved job description: {job_id}")
        
        return json.dumps({
            "status": "success",
            "job": job_data
        }, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Resource access failed: {e}")
        else:
            logger.error(f"Resource access failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


# ============================================================================
# MCP PROMPTS
# ============================================================================

@mcp.prompt()
def resume_generation_prompt(
    job_description: str,
    matched_resumes: str
) -> str:
    """
    Prompt template for resume generation.
    
    Args:
        job_description: The job description text
        matched_resumes: JSON string of matched resumes
    
    Returns:
        Formatted prompt for LLM
    """
    return f"""Based on this job description and matched candidate profiles, generate an optimized resume.

Job Description:
{job_description}

Matched Candidate Profiles:
{matched_resumes}

Generate a professional resume that highlights relevant skills and experience for this role.
Include:
- Professional Summary
- Key Skills
- Work Experience (tailored to job requirements)
- Education
- Notable Achievements

Format in clean, professional markdown.
"""


@mcp.prompt()
def job_analysis_prompt(job_description: str) -> str:
    """
    Prompt template for job description analysis.
    
    Args:
        job_description: The job description text
    
    Returns:
        Formatted prompt for LLM
    """
    return f"""Analyze this job description and extract key information:

{job_description}

Extract and provide:
1. Required skills (list)
2. Experience level (Entry/Mid/Senior/Lead)
3. Key responsibilities (list)
4. Estimated match threshold (0.0-1.0)

Format as JSON.
"""


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server will run on http://{settings.host}:{settings.port}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    logger.info(f"MCP endpoint: http://{settings.host}:{settings.port}/mcp")
    
    # Run FastMCP server using StreamableHTTP transport
    # The host and port are set during FastMCP initialization above
    mcp.run(transport="streamable-http")

