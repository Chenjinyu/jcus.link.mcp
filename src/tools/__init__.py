# src/tools/__init__.py
"""Tools module - MCP tool implementations"""

from typing import Dict, List
from .base import BaseTool
from .search_tool import SearchMatchingResumesTool
from .analysis_tool import AnalyzeJobDescriptionTool
from .generation_tool import GenerateResumeTool

__all__ = [
    "BaseTool",
    "SearchMatchingResumesTool",
    "AnalyzeJobDescriptionTool",
    "GenerateResumeTool",
    "ToolRegistry",
    "get_tool_registry",
]


class ToolRegistry:
    """Registry for managing MCP tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        self.register(SearchMatchingResumesTool())
        self.register(AnalyzeJobDescriptionTool())
        self.register(GenerateResumeTool())
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self._tools.values())
    
    def has_tool(self, name: str) -> bool:
        """Check if tool exists"""
        return name in self._tools


# Singleton instance
_tool_registry = None


def get_tool_registry() -> ToolRegistry:
    """Get tool registry instance (singleton)"""
    global _tool_registry
    
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    
    return _tool_registry