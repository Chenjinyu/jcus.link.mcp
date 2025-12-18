# src/tools/analysis_tool.py
"""
Job Analysis Tool - Analyze job descriptions
"""

import json
import logging
from typing import Dict, Any

from .base import BaseTool
from ..core import Tool, ToolResponse, ToolInputSchema
from ..services import get_resume_service

logger = logging.getLogger(__name__)


class AnalyzeJobDescriptionTool(BaseTool):
    """Tool for analyzing job descriptions to extract key requirements"""
    
    def __init__(self):
        self.resume_service = get_resume_service()
        super().__init__()
    
    def get_definition(self) -> Tool:
        """Get tool definition"""
        return Tool(
            name="analyze_job_description",
            description=(
                "Extract key requirements and skills from a job description. "
                "Returns structured information including required skills, "
                "experience level, responsibilities, and match threshold."
            ),
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "job_description": {
                        "type": "string",
                        "description": "The job description text to analyze"
                    }
                },
                required=["job_description"]
            )
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute job description analysis"""
        
        try:
            # Extract arguments
            job_description = arguments.get("job_description")
            
            if not job_description:
                return self.create_text_response(
                    "Error: job_description is required",
                    is_error=True
                )
            
            logger.info("Analyzing job description")
            
            # Execute analysis
            analysis = await self.resume_service.analyze_job_description(
                job_description
            )
            
            # Format response
            response_data = analysis.dict()
            
            return self.create_text_response(
                json.dumps(response_data, indent=2)
            )
        
        except Exception as e:
            logger.error(f"Analysis tool execution failed: {e}")
            return self.create_text_response(
                f"Error: {str(e)}",
                is_error=True
            )