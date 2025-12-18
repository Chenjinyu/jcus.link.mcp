"""MCP protocol handlers for resume matching server."""

import json
import logging
from typing import Dict, List, Any

from src.models.mcp_models import Tool, MCPResponse
from src.database.vector_database import VectorDatabase
from src.services.resume_generator import LLMService

logger = logging.getLogger(__name__)

# Global service instances (will be injected via dependency injection in production)
vector_db: VectorDatabase | None = None
llm_service: LLMService | None = None


def initialize_services(vdb: VectorDatabase, llm: LLMService) -> None:
    """Initialize global service instances."""
    global vector_db, llm_service
    vector_db = vdb
    llm_service = llm

# ============================================================================
# MCP TOOLS DEFINITION
# ============================================================================

TOOLS = [
    Tool(
        name="search_matching_resumes",
        description="Search for resumes that match a job description using vector similarity",
        inputSchema={
            "type": "object",
            "properties": {
                "job_description": {
                    "type": "string",
                    "description": "The job description to match against"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top matches to return",
                    "default": 5
                }
            },
            "required": ["job_description"]
        }
    ),
    Tool(
        name="generate_resume",
        description="Generate an optimized resume based on job description and matched profiles",
        inputSchema={
            "type": "object",
            "properties": {
                "job_description": {
                    "type": "string",
                    "description": "The job description to tailor the resume for"
                },
                "matched_resumes": {
                    "type": "array",
                    "description": "List of matched resume profiles",
                    "items": {"type": "object"}
                },
                "stream": {
                    "type": "boolean",
                    "description": "Whether to stream the response",
                    "default": True
                }
            },
            "required": ["job_description", "matched_resumes"]
        }
    ),
    Tool(
        name="analyze_job_description",
        description="Extract key requirements and skills from a job description",
        inputSchema={
            "type": "object",
            "properties": {
                "job_description": {
                    "type": "string",
                    "description": "The job description to analyze"
                }
            },
            "required": ["job_description"]
        }
    )
]

# ============================================================================
# MCP PROTOCOL HANDLERS
# ============================================================================

async def handle_tools_list(request_id: int) -> MCPResponse:
    """Handle tools/list request"""
    return MCPResponse(
        id=request_id,
        result={
            "tools": [tool.dict() for tool in TOOLS]
        }
    )

async def handle_tool_call(request_id: int, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
    """Handle tools/call request."""
    if vector_db is None or llm_service is None:
        return MCPResponse(
            id=request_id,
            error={
                "code": -32603,
                "message": "Services not initialized"
            }
        )

    try:
        if tool_name == "search_matching_resumes":
            job_description = arguments.get("job_description")
            if not job_description:
                return MCPResponse(
                    id=request_id,
                    error={
                        "code": -32602,
                        "message": "Missing required parameter: job_description"
                    }
                )

            top_k = arguments.get("top_k", 5)
            
            # Generate embedding for job description
            query_embedding = await vector_db.embed_text(job_description)
            
            # Search for similar resumes
            matches = await vector_db.similarity_search(query_embedding, top_k)
            
            return MCPResponse(
                id=request_id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "matches": matches,
                                "total_found": len(matches)
                            }, indent=2)
                        }
                    ]
                }
            )
        
        elif tool_name == "generate_resume":
            job_description = arguments.get("job_description")
            matched_resumes = arguments.get("matched_resumes", [])
            
            if not job_description:
                return MCPResponse(
                    id=request_id,
                    error={
                        "code": -32602,
                        "message": "Missing required parameter: job_description"
                    }
                )

            if not matched_resumes:
                return MCPResponse(
                    id=request_id,
                    error={
                        "code": -32602,
                        "message": "Missing required parameter: matched_resumes"
                    }
                )

            stream = arguments.get("stream", False)
            
            if stream:
                # For streaming, we'll return a special marker
                # Actual streaming happens via SSE endpoint
                return MCPResponse(
                    id=request_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": "STREAM_RESPONSE:Use /generate-resume-stream endpoint"
                            }
                        ]
                    }
                )
            else:
                # Non-streaming response
                resume_parts = []
                async for chunk in llm_service.generate_resume(
                    job_description, 
                    matched_resumes, 
                    stream=False
                ):
                    resume_parts.append(chunk)
                
                return MCPResponse(
                    id=request_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": "".join(resume_parts)
                            }
                        ]
                    }
                )
        
        elif tool_name == "analyze_job_description":
            job_description = arguments.get("job_description")
            
            if not job_description:
                return MCPResponse(
                    id=request_id,
                    error={
                        "code": -32602,
                        "message": "Missing required parameter: job_description"
                    }
                )

            # Use LLM service to analyze job description
            try:
                analysis = await llm_service.analyze_job_description(job_description)
                
                return MCPResponse(
                    id=request_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(analysis, indent=2)
                            }
                        ]
                    }
                )
            except Exception as e:
                logger.error(f"Error analyzing job description: {e}")
                # Fallback to simple analysis
                analysis = {
                    "required_skills": [],
                    "experience_level": "Unknown",
                    "key_responsibilities": [],
                    "estimated_match_threshold": 0.5,
                    "error": "LLM analysis failed, using fallback"
                }
                
                return MCPResponse(
                    id=request_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(analysis, indent=2)
                            }
                        ]
                    }
                )
        
        else:
            return MCPResponse(
                id=request_id,
                error={
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            )
    
    except Exception as e:
        logger.exception(f"Error executing tool {tool_name}: {e}")
        return MCPResponse(
            id=request_id,
            error={
                "code": -32603,
                "message": f"Tool execution error: {str(e)}"
            }
        )

async def handle_initialize(request_id: int) -> MCPResponse:
    """Handle initialize request"""
    return MCPResponse(
        id=request_id,
        result={
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "resume-matching-server",
                "version": "1.0.0"
            }
        }
    )