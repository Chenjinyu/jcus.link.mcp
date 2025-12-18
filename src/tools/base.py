# src/tools/base.py
"""
Base tool class for MCP tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from ..core import Tool, ToolResponse, TextContent


class BaseTool(ABC):
    """Abstract base class for MCP tools"""
    
    def __init__(self):
        self._tool_definition = self.get_definition()
    
    @property
    def name(self) -> str:
        """Get tool name"""
        return self._tool_definition.name
    
    @property
    def definition(self) -> Tool:
        """Get tool definition"""
        return self._tool_definition
    
    @abstractmethod
    def get_definition(self) -> Tool:
        """Return tool definition for MCP protocol"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute the tool with given arguments"""
        pass
    
    def create_text_response(self, text: str, is_error: bool = False) -> ToolResponse:
        """Helper to create text response"""
        return ToolResponse(
            content=[TextContent(type="text", text=text)],
            isError=is_error
        )