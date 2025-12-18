# src/handlers/mcp_handler.py
"""
MCP Protocol Handler - Handles MCP protocol messages
"""

import logging
from typing import Dict, Any

from ..config import settings
from ..core import (
    MCPRequest,
    MCPResponse,
    MCPError,
    InitializeResult,
    ToolsListResult,
    ToolCallParams,
    ServerInfo,
    ServerCapabilities,
    MCPMethod,
)
from ..core.exceptions import (
    ToolNotFoundException,
    ToolExecutionException,
    InvalidParametersException,
)
from ..tools import get_tool_registry

logger = logging.getLogger(__name__)


class MCPHandler:
    """Handler for MCP protocol messages"""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
    
    async def handle_message(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP message"""
        
        try:
            method = request.method
            params = request.params or {}
            
            logger.info(f"Handling MCP method: {method}")
            
            if method == MCPMethod.INITIALIZE:
                result = await self._handle_initialize(params)
            elif method == MCPMethod.TOOLS_LIST:
                result = await self._handle_tools_list(params)
            elif method == MCPMethod.TOOLS_CALL:
                result = await self._handle_tools_call(params)
            else:
                return MCPResponse(
                    id=request.id,
                    error=MCPError(
                        code=-32601,
                        message=f"Method not found: {method}"
                    )
                )
            
            return MCPResponse(
                id=request.id,
                result=result
            )
        
        except ToolNotFoundException as e:
            logger.error(f"Tool not found: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(code=e.code, message=e.message)
            )
        
        except ToolExecutionException as e:
            logger.error(f"Tool execution failed: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(code=e.code, message=e.message)
            )
        
        except InvalidParametersException as e:
            logger.error(f"Invalid parameters: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(code=e.code, message=e.message)
            )
        
        except Exception as e:
            logger.error(f"Unexpected error handling MCP message: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=-32603,
                    message=f"Internal error: {str(e)}"
                )
            )
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        
        logger.info("Initializing MCP connection")
        
        result = InitializeResult(
            protocolVersion=settings.mcp_protocol_version,
            capabilities=ServerCapabilities(
                tools={}
            ),
            serverInfo=ServerInfo(
                name=settings.app_name,
                version=settings.app_version
            )
        )
        
        return result.dict()
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        
        logger.info("Listing available tools")
        
        tools = self.tool_registry.list_tools()
        tool_definitions = [tool.definition for tool in tools]
        
        result = ToolsListResult(tools=tool_definitions)
        
        return result.dict()
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        
        try:
            # Parse parameters
            tool_call = ToolCallParams(**params)
            
            logger.info(f"Calling tool: {tool_call.name}")
            
            # Get tool
            tool = self.tool_registry.get_tool(tool_call.name)
            if not tool:
                raise ToolNotFoundException(tool_call.name)
            
            # Execute tool
            response = await tool.execute(tool_call.arguments)
            
            return response.dict()
        
        except Exception as e:
            if isinstance(e, ToolNotFoundException):
                raise
            raise ToolExecutionException(
                params.get("name", "unknown"),
                str(e)
            )


# Singleton instance
_mcp_handler = None


def get_mcp_handler() -> MCPHandler:
    """Get MCP handler instance (singleton)"""
    global _mcp_handler
    
    if _mcp_handler is None:
        _mcp_handler = MCPHandler()
    
    return _mcp_handler