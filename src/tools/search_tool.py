# src/tools/search_tool.py
"""
Resume Search Tool - Find matching resumes
"""

import json
import logging
from typing import Dict, Any

from .base import BaseTool
from ..core import Tool, ToolResponse, ToolInputSchema
from ..services import get_resume_service
from ..models import SearchMatchesRequest

logger = logging.getLogger(__name__)


class SearchMatchingResumesTool(BaseTool):
    """Tool for searching matching resumes based on job description"""
    
    def __init__(self):
        self.resume_service = get_resume_service()
        super().__init__()
    
    def get_definition(self) -> Tool:
        """Get tool definition"""
        return Tool(
            name="search_matching_resumes",
            description=(
                "Search for resumes that match a job description using "
                "vector similarity. Returns top K most relevant candidates "
                "with similarity scores."
            ),
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "job_description": {
                        "type": "string",
                        "description": "The job description to match against"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top matches to return (1-20)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5
                    }
                },
                required=["job_description"]
            )
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute resume search"""
        
        try:
            # Extract arguments
            job_description = arguments.get("job_description")
            top_k = arguments.get("top_k", 5)
            
            if not job_description:
                return self.create_text_response(
                    "Error: job_description is required",
                    is_error=True
                )
            
            # Validate top_k
            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return self.create_text_response(
                    "Error: top_k must be an integer between 1 and 20",
                    is_error=True
                )
            
            logger.info(f"Searching for top {top_k} matching resumes")
            
            # Create request
            request = SearchMatchesRequest(
                job_description=job_description,
                top_k=top_k
            )
            
            # Execute search
            result = await self.resume_service.search_matching_resumes(request)
            
            # Format response
            response_data = {
                "matches": [match.dict() for match in result.matches],
                "total_found": result.total_found
            }
            
            return self.create_text_response(
                json.dumps(response_data, indent=2)
            )
        
        except Exception as e:
            logger.error(f"Search tool execution failed: {e}")
            return self.create_text_response(
                f"Error: {str(e)}",
                is_error=True
            )