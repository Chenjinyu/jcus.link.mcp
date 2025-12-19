# Migration Guide: From Monolithic to Modular Structure

This guide explains how the original monolithic `mcp_resume_server.py` was refactored into a modular, production-ready structure.

## Before vs After

### Before (Single File: ~500 lines)
```
mcp_resume_server.py  (Everything in one file)
├── Imports
├── VectorDatabase class
├── LLMService class
├── TOOLS list
├── handle_tools_list()
├── handle_tool_call()
├── handle_initialize()
├── HTTP endpoints
└── if __name__ == "__main__"
```

### After (Modular Structure)
```
mcp-resume-server/
├── src/
│   ├── config/          # Configuration
│   ├── core/            # Protocol & exceptions
│   ├── services/        # Business logic
│   ├── handlers/        # Request handling
│   ├── tools/           # MCP tools
│   ├── models/          # Data models
│   └── main.py          # Application entry
```

## Key Changes

### 1. Configuration Management

**Before:**
```python
# Hardcoded values scattered throughout
llm_model = "claude-sonnet-4-20250514"
max_tokens = 2000
collection_name = "resumes"
```

**After:**
```python
# src/config/settings.py
class Settings(BaseSettings):
    llm_model: str = "claude-sonnet-4-20250514"
    llm_max_tokens: int = 2000
    vector_db_collection: str = "resumes"
    
    class Config:
        env_file = ".env"

settings = get_settings()
```

**Benefits:**
- ✅ All config in one place
- ✅ Environment variable support
- ✅ Type validation
- ✅ Easy to change without code modification

---

### 2. Service Layer Extraction

**Before:**
```python
class VectorDatabase:
    def __init__(self):
        self.resumes = [...]  # Hardcoded
    
    async def embed_text(self, text: str):
        return np.random.rand(384)
    
    async def similarity_search(self, query_embedding, top_k):
        # Implementation

class LLMService:
    def __init__(self):
        self.api_key = "..."  # Hardcoded
    
    async def generate_resume(self, ...):
        # Implementation

# Global instances
vector_db = VectorDatabase()
llm_service = LLMService()
```

**After:**
```python
# src/services/vector_service.py
class BaseVectorService(ABC):  # Abstract base
    @abstractmethod
    async def similarity_search(self, ...): pass

class ChromaDBVectorService(BaseVectorService):
    # ChromaDB implementation

class PineconeVectorService(BaseVectorService):
    # Pinecone implementation

# Factory pattern
def get_vector_service() -> BaseVectorService:
    return VectorServiceFactory.create()

# src/services/llm_service.py
class BaseLLMService(ABC):
    @abstractmethod
    async def generate_resume(self, ...): pass

class AnthropicLLMService(BaseLLMService):
    # Anthropic implementation

class OpenAILLMService(BaseLLMService):
    # OpenAI implementation

def get_llm_service() -> BaseLLMService:
    return LLMServiceFactory.create()
```

**Benefits:**
- ✅ Easy to swap implementations
- ✅ Can test with mock services
- ✅ Support multiple providers
- ✅ Clear interfaces

---

### 3. MCP Protocol Handling

**Before:**
```python
# Inline functions
async def handle_tools_list(request_id: int) -> MCPResponse:
    return MCPResponse(...)

async def handle_tool_call(request_id: int, tool_name: str, arguments: Dict):
    if tool_name == "search_matching_resumes":
        # Inline implementation
    elif tool_name == "generate_resume":
        # Inline implementation

@app.post("/mcp/message")
async def handle_mcp_message(request: MCPRequest):
    if method == "tools/list":
        return await handle_tools_list(request.id)
    elif method == "tools/call":
        return await handle_tool_call(...)
```

**After:**
```python
# src/handlers/mcp_handler.py
class MCPHandler:
    def __init__(self):
        self.tool_registry = get_tool_registry()
    
    async def handle_message(self, request: MCPRequest) -> MCPResponse:
        method = request.method
        
        if method == MCPMethod.TOOLS_LIST:
            return await self._handle_tools_list(...)
        # ... other methods

# src/main.py
mcp_handler = get_mcp_handler()

@app.post("/mcp/message")
async def handle_mcp_message(request: MCPRequest):
    return await mcp_handler.handle_message(request)
```

**Benefits:**
- ✅ Centralized protocol handling
- ✅ Better error handling
- ✅ Easier to test
- ✅ Clean separation from HTTP layer

---

### 4. Tool Implementation

**Before:**
```python
# Tools defined as dicts
TOOLS = [
    Tool(
        name="search_matching_resumes",
        description="...",
        inputSchema={...}
    ),
    # ... more tools
]

# Tool execution mixed with handler
async def handle_tool_call(request_id, tool_name, arguments):
    if tool_name == "search_matching_resumes":
        query_embedding = await vector_db.embed_text(job_description)
        matches = await vector_db.similarity_search(query_embedding)
        return MCPResponse(...)
    elif tool_name == "generate_resume":
        # Implementation here
```

**After:**
```python
# src/tools/base.py
class BaseTool(ABC):
    @abstractmethod
    def get_definition(self) -> Tool: pass
    
    @abstractmethod
    async def execute(self, arguments: Dict) -> ToolResponse: pass

# src/tools/search_tool.py
class SearchMatchingResumesTool(BaseTool):
    def __init__(self):
        self.resume_service = get_resume_service()
    
    def get_definition(self) -> Tool:
        return Tool(name="search_matching_resumes", ...)
    
    async def execute(self, arguments: Dict) -> ToolResponse:
        # Implementation using resume_service

# src/tools/__init__.py
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.register(SearchMatchingResumesTool())
        self.register(AnalyzeJobDescriptionTool())
        self.register(GenerateResumeTool())
```

**Benefits:**
- ✅ Each tool is self-contained
- ✅ Easy to add new tools
- ✅ Tools are independently testable
- ✅ Clear tool interface

---

### 5. Data Models

**Before:**
```python
# Inline dictionaries
result = {
    "matches": [
        {
            "resume_id": "...",
            "content": "...",
            "skills": [...],
            # No validation
        }
    ]
}
```

**After:**
```python
# src/models/domain_models.py
class ResumeMatch(BaseModel):
    resume_id: str
    content: str
    skills: List[str]
    experience_years: int
    similarity_score: float = Field(ge=0.0, le=1.0)

class SearchMatchesResponse(BaseModel):
    matches: List[ResumeMatch]
    total_found: int

# Usage
result = SearchMatchesResponse(
    matches=[ResumeMatch(...), ...],
    total_found=5
)
```

**Benefits:**
- ✅ Automatic validation
- ✅ Type safety
- ✅ Better IDE support
- ✅ Clear data contracts

---

### 6. Error Handling

**Before:**
```python
# Generic try-catch
try:
    result = await some_operation()
    return result
except Exception as e:
    return {"error": str(e)}
```

**After:**
```python
# src/core/exceptions.py
class MCPServerException(Exception):
    def __init__(self, message: str, code: int = -32603):
        self.message = message
        self.code = code

class ToolNotFoundException(MCPServerException):
    def __init__(self, tool_name: str):
        super().__init__(
            message=f"Tool not found: {tool_name}",
            code=-32601
        )

# Usage
try:
    tool = self.tool_registry.get_tool(name)
    if not tool:
        raise ToolNotFoundException(name)
except ToolNotFoundException as e:
    return MCPResponse(
        id=request_id,
        error=MCPError(code=e.code, message=e.message)
    )
```

**Benefits:**
- ✅ Specific error types
- ✅ MCP-compliant error codes
- ✅ Better error messages
- ✅ Easier debugging

---

## Migration Steps

If you're migrating from the monolithic version:

### Step 1: Copy Configuration
```bash
# Extract all hardcoded values to .env
cp .env.example .env
# Edit with your values
```

### Step 2: Update Imports
```python
# Old
from mcp_resume_server import VectorDatabase, LLMService

# New
from src.services import get_vector_service, get_llm_service
```

### Step 3: Update Service Usage
```python
# Old
vector_db = VectorDatabase()
result = await vector_db.similarity_search(...)

# New
vector_service = get_vector_service()
result = await vector_service.similarity_search(...)
```

### Step 4: Run Tests
```bash
pytest tests/
```

### Step 5: Update Deployment
```bash
# Old
python mcp_resume_server.py

# New
python -m src.main
# or
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## Code Comparison Examples

### Example 1: Searching Resumes

**Before:**
```python
@app.post("/mcp/message")
async def handle_mcp_message(request: MCPRequest):
    if request.method == "tools/call":
        if params.get("name") == "search_matching_resumes":
            job_description = arguments.get("job_description")
            query_embedding = await vector_db.embed_text(job_description)
            matches = await vector_db.similarity_search(query_embedding)
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": json.dumps(matches)}]}
            )
```

**After:**
```python
# src/tools/search_tool.py
class SearchMatchingResumesTool(BaseTool):
    async def execute(self, arguments: Dict) -> ToolResponse:
        request = SearchMatchesRequest(**arguments)
        result = await self.resume_service.search_matching_resumes(request)
        return self.create_text_response(json.dumps(result.dict()))

# Automatically handled by:
# src/handlers/mcp_handler.py
# src/tools/__init__.py (registry)
```

---

### Example 2: Configuration

**Before:**
```python
# Scattered throughout file
PORT = 8000
LLM_MODEL = "claude-sonnet-4-20250514"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
```

**After:**
```python
# .env
PORT=8000
LLM_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Accessed via:
from src.config import settings
port = settings.port
```

---

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Lines per file** | 500+ | 50-200 |
| **Testability** | Hard to test | Easy to test each module |
| **Configurability** | Hardcoded | Environment variables |
| **Maintainability** | Single point of failure | Modular |
| **Scalability** | Tight coupling | Loose coupling |
| **Provider Support** | Single | Multiple (Anthropic, OpenAI, etc.) |
| **Error Handling** | Generic | Specific, MCP-compliant |
| **Type Safety** | Minimal | Full type hints |

---

## Conclusion

The refactored structure provides:

1. **Better Organization**: Clear module boundaries
2. **Easier Maintenance**: Find and fix bugs quickly
3. **Greater Flexibility**: Swap implementations easily
4. **Improved Testing**: Test components independently
5. **Production Ready**: Proper configuration, logging, error handling
6. **Team Friendly**: Multiple developers can work simultaneously

The modular structure follows Python best practices and industry standards, making it suitable for production deployment and team collaboration.