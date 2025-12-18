# src/main.py
"""
Main application entry point
"""

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.config import settings
from src.core import MCPRequest
from src.handlers import get_mcp_handler, get_http_handler
from src.models import SearchMatchesRequest, AnalyzeJobRequest, GenerateResumeRequest

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"MCP Protocol Version: {settings.mcp_protocol_version}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Initialize handlers
mcp_handler = get_mcp_handler()
http_handler = get_http_handler()


# ============================================================================
# MCP PROTOCOL ENDPOINTS
# ============================================================================

@app.post("/mcp/message")
async def handle_mcp_message(request: MCPRequest):
    """Handle MCP protocol messages"""
    response = await mcp_handler.handle_message(request)
    return response


# ============================================================================
# HTTP REST ENDPOINTS
# ============================================================================

@app.post("/upload-job-description")
async def upload_job_description(file: UploadFile = File(...)):
    """Upload job description file and get matching resumes"""
    try:
        result = await http_handler.handle_file_upload(file)
        return result
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search-matches")
async def search_matches(request: SearchMatchesRequest):
    """Search for matching resumes"""
    try:
        return await http_handler.handle_search_matches(request)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-job")
async def analyze_job(request: AnalyzeJobRequest):
    """Analyze job description"""
    try:
        return await http_handler.handle_analyze_job(request)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-resume")
async def generate_resume(request: GenerateResumeRequest):
    """Generate optimized resume (non-streaming)"""
    try:
        return await http_handler.handle_generate_resume(request)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-resume-stream")
async def generate_resume_stream(request: GenerateResumeRequest):
    """Generate resume with streaming"""
    
    async def event_stream():
        try:
            async for chunk in http_handler.stream_resume_generation(
                request.job_description,
                request.matched_resumes
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "protocol": settings.mcp_protocol_version,
        "endpoints": {
            "mcp": "/mcp/message",
            "upload": "/upload-job-description",
            "search": "/search-matches",
            "analyze": "/analyze-job",
            "generate": "/generate-resume",
            "stream": "/generate-resume-stream",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": settings.app_name,
        "version": settings.app_version,
        "protocol": settings.mcp_protocol_version
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )