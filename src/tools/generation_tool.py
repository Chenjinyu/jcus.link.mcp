# src/tools/generation_tool.py
"""
Resume Generation Tool - Generate optimized resumes
"""

import json
import logging
from typing import Dict, Any, List

from .base import BaseTool
from ..core import Tool, ToolResponse, ToolInputSchema
from ..services import get_resume_service
from ..models import ResumeMatch

logger = logging.getLogger(__name__)


class GenerateResumeTool(BaseTool):
    """Tool for generating optimized resumes based on job description"""
    
    def __init__(self):
        self.resume_service = get_resume_service()
        super().__init__()
    
    def get_definition(self) -> Tool:
        """Get tool definition"""
        return Tool(
            name="generate_resume",
            description=(
                "Generate an optimized resume based on a job description "
                "and matched candidate profiles. Returns a professional "
                "resume tailored to the job requirements."
            ),
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "job_description": {
                        "type": "string",
                        "description": "The job description to tailor the resume for"
                    },
                    "matched_resumes": {
                        "type": "array",
                        "description": "List of matched resume profiles to base generation on",
                        "items": {
                            "type": "object",
                            "properties": {
                                "resume_id": {"type": "string"},
                                "content": {"type": "string"},
                                "skills": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "experience_years": {"type": "integer"},
                                "similarity_score": {"type": "number"}
                            }
                        }
                    },
                    "stream": {
                        "type": "boolean",
                        "description": "Whether to stream the response (use HTTP endpoint for streaming)",
                        "default": False
                    }
                },
                required=["job_description", "matched_resumes"]
            )
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute resume generation"""
        
        try:
            # Extract arguments
            job_description = arguments.get("job_description")
            matched_resumes_data = arguments.get("matched_resumes", [])
            stream = arguments.get("stream", False)
            
            if not job_description:
                return self.create_text_response(
                    "Error: job_description is required",
                    is_error=True
                )
            
            if not matched_resumes_data:
                return self.create_text_response(
                    "Error: matched_resumes is required and must not be empty",
                    is_error=True
                )
            
            # Convert to ResumeMatch objects
            matched_resumes: List[ResumeMatch] = []
            for resume_data in matched_resumes_data:
                try:
                    matched_resumes.append(ResumeMatch(**resume_data))
                except Exception as e:
                    return self.create_text_response(
                        f"Error: Invalid resume data format: {e}",
                        is_error=True
                    )
            
            logger.info(f"Generating resume for {len(matched_resumes)} matched profiles")
            
            if stream:
                # For streaming, indicate that client should use HTTP endpoint
                return self.create_text_response(
                    "STREAM_RESPONSE: Use /generate-resume-stream HTTP endpoint for streaming"
                )
            else:
                # Generate resume (non-streaming)
                resume_chunks = []
                async for chunk in self.resume_service.generate_optimized_resume(
                    job_description,
                    matched_resumes,
                    stream=False
                ):
                    resume_chunks.append(chunk)
                
                resume = "".join(resume_chunks)
                
                return self.create_text_response(resume)
        
        except Exception as e:
            logger.error(f"Generation tool execution failed: {e}")
            return self.create_text_response(
                f"Error: {str(e)}",
                is_error=True
            )