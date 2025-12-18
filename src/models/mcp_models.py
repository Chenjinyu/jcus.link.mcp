from typing import Optional, Dict
from pydantic import BaseModel



class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Optional[Dict] = None
    
    
class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Optional[Dict] = None
    error: Optional[Dict] = None
    
    
class MCPError(BaseModel):
    code: int
    message: str
    data: Optional[Dict] = None
    

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Optional[Dict] = None
    
    
class ToolResult(BaseModel):
    result: Optional[Dict] = None
    error: Optional[Dict] = None
    
    
class ToolError(BaseModel):
    code: int
    message: str
    data: Optional[Dict] = None
    
    
class ToolResultContent(BaseModel):
    result: Optional[Dict] = None
    error: Optional[Dict] = None
    
    
class ToolUseContent(BaseModel):
    name: str
    parameters: Optional[Dict] = None
    
    
class ToolUseResult(BaseModel):
    result: Optional[Dict] = None
    error: Optional[Dict] = None
    
    
class ToolUseResultContent(BaseModel):
    result: Optional[Dict] = None
    error: Optional[Dict] = None