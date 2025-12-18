"""FastAPI server for resume matching MCP service."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.config import settings
from src.models.mcp_models import MCPRequest, MCPResponse
from src.database.vector_database import VectorDatabase
from src.services.resume_generator import LLMService
from src.services.document_parser import DocumentParser
from src.mcp_resume_server import (
    handle_initialize,
    handle_tools_list,
    handle_tool_call,
    TOOLS,
    initialize_services,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Matching MCP Server",
    version="1.0.0",
    description="MCP server for job description matching and resume generation",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
vector_db = VectorDatabase()
llm_service = LLMService()
document_parser = DocumentParser()

# Initialize MCP services
initialize_services(vector_db, llm_service)


@app.post("/mcp/message")
async def handle_mcp_message(request: MCPRequest) -> MCPResponse:
    """
    Handle MCP protocol messages.

    Args:
        request: MCP request with method and parameters

    Returns:
        MCPResponse with result or error
    """
    try:
        method = request.method
        params = request.params or {}

        if method == "initialize":
            return await handle_initialize(request.id)

        elif method == "tools/list":
            return await handle_tools_list(request.id)

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing required parameter: name",
                    },
                )

            return await handle_tool_call(request.id, tool_name, arguments)

        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            )

    except Exception as e:
        logger.exception(f"Error handling MCP message: {e}")
        return MCPResponse(
            id=request.id or 0,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}",
            },
        )

class UploadResponse(BaseModel):
    """Response model for file upload."""

    status: str
    job_description: str
    matches: List[Dict[str, Any]]
    upload_time: str
    filename: str
    file_type: str


@app.post("/upload-job-description", response_model=UploadResponse)
async def upload_job_description(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload job description file (PDF, HTML, DOC, DOCX, TXT).

    Args:
        file: Uploaded file

    Returns:
        UploadResponse with parsed content and matches

    Raises:
        HTTPException: If file processing fails
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            )

        # Validate file size
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE} bytes",
            )

        # Parse document
        logger.info(f"Parsing file: {file.filename} ({file.content_type})")
        job_description = await document_parser.parse_file(
            content, file.filename, file.content_type or ""
        )

        if not job_description.strip():
            raise HTTPException(
                status_code=400, detail="Could not extract text from file"
            )

        # Generate embedding
        query_embedding = await vector_db.embed_text(job_description)

        # Search for matches
        matches = await vector_db.similarity_search(query_embedding, top_k=5)

        logger.info(f"Found {len(matches)} matches for {file.filename}")

        return UploadResponse(
            status="success",
            job_description=job_description,
            matches=matches,
            upload_time=datetime.now().isoformat(),
            filename=file.filename,
            file_type=file_extension,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

class GenerateResumeRequest(BaseModel):
    """Request model for resume generation."""

    job_description: str
    matched_resumes: List[Dict[str, Any]]


@app.post("/generate-resume-stream")
async def generate_resume_stream(request: GenerateResumeRequest) -> StreamingResponse:
    """
    Stream resume generation based on job description and matched resumes.

    Args:
        request: GenerateResumeRequest with job description and matches

    Returns:
        StreamingResponse with SSE-formatted resume chunks
    """
    async def event_stream():
        try:
            async for chunk in llm_service.generate_resume(
                request.job_description,
                request.matched_resumes,
                stream=True,
            ):
                # Send as SSE format
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Send completion marker
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.exception("Error generating resume stream:")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "resume-matching-mcp-server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "Resume Matching MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp/message",
            "upload": "/upload-job-description",
            "stream": "/generate-resume-stream",
            "health": "/health"
        },
        "tools": [tool.name for tool in TOOLS]
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="debug" if settings.DEBUG else "info",
    )
