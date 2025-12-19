# Quick Reference Card - MCP Resume Server

## 🚀 Quick Start Commands

```bash
# Setup
./setup.sh

# Development
python -m src.main
uvicorn src.main:app --reload

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Test
curl http://localhost:8000/health
```

## 📁 Where to Find What

| Need to... | Go to... |
|------------|----------|
| **Change config** | `src/config/settings.py` or `.env` |
| **Add new tool** | Create in `src/tools/`, register in `__init__.py` |
| **Add LLM provider** | Add class in `src/services/llm_service.py` |
| **Add vector DB** | Add class in `src/services/vector_service.py` |
| **Change HTTP endpoints** | `src/main.py` |
| **Change MCP handling** | `src/handlers/mcp_handler.py` |
| **Add data model** | `src/models/domain_models.py` |
| **Add exception type** | `src/core/exceptions.py` |
| **Change business logic** | `src/services/resume_service.py` |

## 🔧 Common Tasks

### Add a New MCP Tool

```python
# 1. Create src/tools/my_tool.py
from .base import BaseTool
from ..core import Tool, ToolResponse, ToolInputSchema

class MyTool(BaseTool):
    def get_definition(self) -> Tool:
        return Tool(
            name="my_tool",
            description="What it does",
            inputSchema=ToolInputSchema(
                type="object",
                properties={"param": {"type": "string"}},
                required=["param"]
            )
        )
    
    async def execute(self, arguments: dict) -> ToolResponse:
        result = f"Processed: {arguments['param']}"
        return self.create_text_response(result)

# 2. Register in src/tools/__init__.py
def _register_default_tools(self):
    self.register(MyTool())  # Add this line
```

### Add Environment Variable

```python
# 1. Add to .env
MY_NEW_SETTING=value

# 2. Add to src/config/settings.py
class Settings(BaseSettings):
    my_new_setting: str = "default"

# 3. Use anywhere
from src.config import settings
value = settings.my_new_setting
```

### Add HTTP Endpoint

```python
# In src/main.py
@app.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    result = await http_handler.handle_my_request(request)
    return result

# Add handler in src/handlers/http_handler.py
async def handle_my_request(self, request: MyRequest):
    # Implementation
    pass
```

## 📊 Module Cheat Sheet

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| **config/** | Settings | `Settings`, `get_settings()` |
| **core/** | Protocol & errors | `MCPRequest`, `MCPResponse`, exceptions |
| **services/** | Business logic | `ResumeService`, `LLMService`, `VectorService` |
| **handlers/** | Request handling | `MCPHandler`, `HTTPHandler` |
| **tools/** | MCP tools | `BaseTool`, tool implementations |
| **models/** | Data models | `ResumeMatch`, `JobAnalysis` |

## 🎯 Architecture Layers

```
main.py (FastAPI)
    ↓
handlers/ (Request routing)
    ↓
services/ (Business logic)
    ↓
External APIs (LLM, Vector DB)
```

## 🔍 Debugging Tips

### Enable Debug Logging
```bash
# In .env
LOG_LEVEL=DEBUG
DEBUG=true
```

### Check Service Health
```bash
curl http://localhost:8000/health
```

### View Available Tools
```bash
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Test Tool Execution
```bash
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"analyze_job_description",
      "arguments":{"job_description":"We need a Python developer..."}
    }
  }'
```

## 📝 Configuration Reference

### Required Environment Variables
```bash
LLM_API_KEY=your_anthropic_or_openai_key
```

### Optional Environment Variables
```bash
LLM_PROVIDER=anthropic          # or openai
LLM_MODEL=claude-sonnet-4-20250514
VECTOR_DB_TYPE=chromadb         # or pinecone
PORT=8000
LOG_LEVEL=INFO
```

## 🎨 Design Patterns Quick Reference

| Pattern | Where Used | Why |
|---------|------------|-----|
| **Factory** | `LLMServiceFactory`, `VectorServiceFactory` | Easy provider switching |
| **Singleton** | `get_llm_service()`, `get_vector_service()` | Single instance |
| **Strategy** | `BaseLLMService`, `BaseVectorService` | Multiple implementations |
| **Registry** | `ToolRegistry` | Dynamic tool management |
| **ABC** | All base classes | Enforce interface |

## 🚨 Common Issues & Solutions

### Issue: ModuleNotFoundError
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: Configuration not loading
```bash
# Solution: Check .env exists
cp .env.example .env
# Edit .env with your values
```

### Issue: API key errors
```bash
# Solution: Set API key in .env
LLM_API_KEY=your_actual_key_here
```

### Issue: Port already in use
```bash
# Solution: Change port in .env or command
PORT=8001 python -m src.main
# or
uvicorn src.main:app --port 8001
```

## 📚 Documentation Map

```
Start Here
    ↓
README.md (Overview & usage)
    ↓
PROJECT_STRUCTURE.md (Architecture)
    ↓
FILE_STRUCTURE.md (Detailed breakdown)
    ↓
ARCHITECTURE.md (Diagrams)
    ↓
MIGRATION_GUIDE.md (Before/after details)
```

## 🔗 Important URLs (When Running)

- **Main App**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (if enabled)
- **MCP Endpoint**: http://localhost:8000/mcp/message

## 💡 Pro Tips

1. **Use Type Hints** - IDE autocomplete works great
2. **Read Docstrings** - Every class/function has docs
3. **Check Logs** - Structured logging at each layer
4. **Use Pydantic** - Automatic validation
5. **Follow Patterns** - Look at existing code for examples

## 📦 Key Dependencies

```
fastapi        # Web framework
uvicorn        # ASGI server
pydantic       # Data validation
anthropic      # Claude AI
openai         # GPT
chromadb       # Vector database
sentence-transformers  # Embeddings
```

## 🎯 Testing Checklist

- [ ] Health check responds
- [ ] MCP tools/list works
- [ ] File upload works
- [ ] Search returns results
- [ ] Resume generation works
- [ ] Streaming works
- [ ] Error handling works

---

**Keep this card handy for quick reference!** 📋