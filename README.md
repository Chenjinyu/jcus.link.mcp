# MCP Resume Server

A production-ready Model Context Protocol (MCP) server for AI-powered resume matching and generation.

## Features

- 🔍 **Vector Similarity Search**: Find the best matching candidates for job descriptions
- 🤖 **AI-Powered Resume Generation**: Generate optimized resumes using LLMs
- 📊 **Job Analysis**: Extract key requirements and skills from job descriptions
- 🚀 **MCP Protocol Support**: Full implementation of MCP 2024-11-05 specification
- 🌐 **HTTP/SSE Transport**: RESTful API with streaming support
- 🎯 **Modular Architecture**: Clean, maintainable, and testable code structure

## Project Structure

```
mcp-resume-server/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── mcp_protocol.py          # MCP protocol models
│   │   └── exceptions.py            # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py           # LLM integration (Anthropic/OpenAI)
│   │   ├── vector_service.py        # Vector database operations
│   │   └── resume_service.py        # Business logic
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── mcp_handler.py           # MCP protocol handler
│   │   └── http_handler.py          # HTTP endpoints handler
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base tool class
│   │   ├── search_tool.py           # Resume search tool
│   │   ├── analysis_tool.py         # Job analysis tool
│   │   └── generation_tool.py       # Resume generation tool
│   └── models/
│       ├── __init__.py
│       └── domain_models.py         # Domain data models
├── tests/                           # Test suite
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Design Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- **Config**: Application settings and environment variables
- **Core**: Protocol definitions and shared exceptions
- **Services**: Business logic and external integrations
- **Handlers**: Request/response processing
- **Tools**: MCP tool implementations
- **Models**: Data structures and validation

### 2. **Dependency Injection**
Services are created via factories and injected where needed:
```python
# Services are singletons accessed via getters
llm_service = get_llm_service()
vector_service = get_vector_service()
```

### 3. **Abstract Base Classes**
Easy to swap implementations:
```python
class BaseLLMService(ABC):
    # Can use Anthropic, OpenAI, or custom LLM
    
class BaseVectorService(ABC):
    # Can use ChromaDB, Pinecone, Weaviate, etc.
```

### 4. **Type Safety**
Full type hints throughout the codebase using Pydantic models.

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd mcp-resume-server
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set API keys**
```bash
# In .env file
LLM_API_KEY=your_anthropic_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Server

### Development Mode
```bash
# From project root
python -m src.main

# Or with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Usage

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. MCP Protocol - List Tools
```bash
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### 3. Upload Job Description
```bash
curl -X POST http://localhost:8000/upload-job-description \
  -F "file=@job_description.txt"
```

### 4. Search Matching Resumes
```bash
curl -X POST http://localhost:8000/search-matches \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Python Developer with 5+ years experience...",
    "top_k": 5
  }'
```

### 5. Analyze Job Description
```bash
curl -X POST http://localhost:8000/analyze-job \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Senior Software Engineer..."
  }'
```

### 6. Generate Resume (Non-Streaming)
```bash
curl -X POST http://localhost:8000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Developer position...",
    "matched_resumes": [...],
    "stream": false
  }'
```

### 7. Generate Resume (Streaming)
```bash
curl -N -X POST http://localhost:8000/generate-resume-stream \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Developer position...",
    "matched_resumes": [...]
  }'
```

## Configuration

All configuration is managed through environment variables in `.env`:

### Core Settings
- `APP_NAME`: Application name
- `DEBUG`: Enable debug mode
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### LLM Configuration
- `LLM_PROVIDER`: anthropic or openai
- `LLM_MODEL`: Model to use
- `LLM_API_KEY`: API key for LLM provider

### Vector Database
- `VECTOR_DB_TYPE`: chromadb, pinecone, or weaviate
- `EMBEDDING_MODEL`: Sentence transformer model
- `MIN_SIMILARITY_THRESHOLD`: Minimum similarity score (0.0-1.0)

## Adding New Features

### Adding a New Tool

1. Create tool class in `src/tools/`:
```python
# src/tools/my_new_tool.py
from .base import BaseTool
from ..core import Tool, ToolResponse, ToolInputSchema

class MyNewTool(BaseTool):
    def get_definition(self) -> Tool:
        return Tool(
            name="my_new_tool",
            description="What this tool does",
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "param1": {"type": "string", "description": "..."}
                },
                required=["param1"]
            )
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        # Implementation
        return self.create_text_response("Result")
```

2. Register in `src/tools/__init__.py`:
```python
from .my_new_tool import MyNewTool

class ToolRegistry:
    def _register_default_tools(self):
        # ... existing tools ...
        self.register(MyNewTool())
```

### Adding a New LLM Provider

1. Create service in `src/services/llm_service.py`:
```python
class CustomLLMService(BaseLLMService):
    async def generate_resume(self, ...) -> AsyncIterator[str]:
        # Implementation
        pass
```

2. Update factory:
```python
class LLMServiceFactory:
    @staticmethod
    def create() -> BaseLLMService:
        if provider == "custom":
            return CustomLLMService()
```

### Adding a New Vector Database

Similar pattern to LLM providers - extend `BaseVectorService` and update factory.

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mcp-resume-server .
docker run -p 8000:8000 --env-file .env mcp-resume-server
```

### Cloud Deployment

**Railway/Render:**
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically

**AWS/GCP:**
Use Docker container or deploy to serverless platforms.

## Architecture Benefits

### ✅ Maintainability
- Clear module boundaries
- Easy to locate and fix bugs
- Self-documenting code structure

### ✅ Testability
- Each component can be tested independently
- Easy to mock services and dependencies
- Clear interfaces between modules

### ✅ Scalability
- Services can be extracted into microservices
- Easy to add new features without breaking existing code
- Support for multiple LLM and vector DB providers

### ✅ Type Safety
- Pydantic models catch errors at runtime
- Type hints help with IDE autocomplete
- Reduces bugs and improves code quality

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request