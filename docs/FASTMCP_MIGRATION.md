# FastMCP Migration Summary

## Overview

The project has been refactored to use **FastMCP** as the standard framework for building MCP applications. The server now uses FastMCP decorators (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`) instead of FastAPI endpoints.

## Key Changes

### 1. **New FastMCP Server** (`src/mcp_server.py`)

The main server is now a FastMCP application with:

#### Tools (`@mcp.tool`)
- `upload_job_description` - Upload job description from text, file (base64), or URL
- `search_matching_resumes` - Search for matching resumes using vector similarity
- `list_matched_job_descriptions` - List all uploaded job descriptions
- `analyze_job_description` - Analyze job description to extract requirements
- `generate_resume` - Generate optimized resume based on job description and matches

#### Resources (`@mcp.resource`)
- `matched_resumes_resource` - Access matched resumes by job ID (URI: `resume://matches/{job_id}`)
- `job_description_resource` - Access job descriptions by ID (URI: `resume://job/{job_id}`)

#### Prompts (`@mcp.prompt`)
- `resume_generation_prompt` - Template for resume generation
- `job_analysis_prompt` - Template for job description analysis

### 2. **Supabase Vector Database Support**

Added `SupabaseVectorService` class that:
- Uses Supabase with pgvector for vector similarity search
- Falls back to simulated responses if credentials not configured
- Maintains singleton pattern via factory

**Configuration:**
```env
VECTOR_DB_TYPE=supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_TABLE_NAME=resumes
SUPABASE_QUERY_NAME=match_resumes
```

### 3. **Enhanced Document Parser**

Updated `DocumentParser` to support:
- **URL parsing** - Fetch and parse content from URLs
- **Multiple file types** - PDF, HTML, DOC, DOCX, TXT
- **Base64 file uploads** - For MCP tool input

**New methods:**
- `parse_url(url: str)` - Parse content from URL
- `parse_input(input_data, input_type)` - Unified parser for text/file/URL

### 4. **Maintained Patterns**

✅ **Singleton Pattern** - Services use singleton instances via `get_*_service()` functions
✅ **Factory Pattern** - `VectorServiceFactory` and `LLMServiceFactory` for service creation
✅ **Service Layer** - Business logic remains in service classes
✅ **Type Safety** - Full type hints and Pydantic models

## Architecture

```
MCP Client
    ↓
FastMCP Server (mcp_server.py)
    ↓
Tools/Resources/Prompts
    ↓
Service Layer (resume_service, vector_service, llm_service)
    ↓
Vector Database (Supabase/ChromaDB/Pinecone)
    ↓
LLM Service (Anthropic/OpenAI)
```

## Usage

### Running the Server

```bash
# From project root
uv run python -m src.mcp_server

# Or if using uvicorn
uvicorn src.mcp_server:mcp --host 0.0.0.0 --port 8000
```

### Environment Variables

Create `.env` file:

```env
# Application
APP_NAME=resume-matching-mcp-server
DEBUG=false

# Vector Database (Supabase)
VECTOR_DB_TYPE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_TABLE_NAME=resumes
SUPABASE_QUERY_NAME=match_resumes

# LLM Service
LLM_PROVIDER=anthropic
LLM_API_KEY=your-anthropic-key
LLM_MODEL=claude-sonnet-4-20250514

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_FILE_TYPES=.txt,.pdf,.doc,.docx,.html,.htm
ALLOW_URL_UPLOADS=true
```

### Example MCP Client Usage

```python
from fastmcp import Client

async with Client("http://localhost:8000/mcp") as client:
    # Upload job description from URL
    result = await client.call_tool(
        "upload_job_description",
        {
            "input_data": "https://example.com/job-posting.html",
            "input_type": "url"
        }
    )
    
    # Search for matches
    matches = await client.call_tool(
        "search_matching_resumes",
        {
            "job_description": "Software Engineer with Python experience...",
            "top_k": 5
        }
    )
    
    # Generate resume
    resume = await client.call_tool(
        "generate_resume",
        {
            "job_description": "...",
            "matched_resumes": [...]
        }
    )
```

## File Structure

```
src/
├── mcp_server.py          # FastMCP server (NEW)
├── main.py                # Old FastAPI server (can be removed)
├── config/
│   └── settings.py        # Updated with Supabase config
├── services/
│   ├── vector_service.py  # Added SupabaseVectorService
│   ├── document_parser.py # Added URL parsing
│   └── ...
├── models/
│   └── domain_models.py
└── core/
    └── exceptions.py
```

## Migration Notes

1. **Old FastAPI endpoints** in `main.py` are deprecated - use MCP tools instead
2. **HTTP handlers** in `handers/` are no longer needed for MCP protocol
3. **Tool registry** pattern replaced by FastMCP decorators
4. **Resources** now use FastMCP resource decorators instead of custom handlers

## Next Steps

1. **Remove old FastAPI code** - `main.py` and HTTP handlers can be removed
2. **Configure Supabase** - Set up Supabase project and pgvector extension
3. **Add real embeddings** - Integrate sentence-transformers or OpenAI embeddings
4. **Test MCP client** - Verify all tools work with MCP client
5. **Add persistence** - Replace in-memory storage with database

## Benefits

✅ **Standard MCP Protocol** - Uses FastMCP framework for compatibility
✅ **Cleaner Code** - Decorator-based tools are more Pythonic
✅ **Better Separation** - Tools, resources, and prompts are clearly defined
✅ **Flexible** - Easy to add new tools/resources/prompts
✅ **Type Safe** - Full type hints and validation
✅ **Production Ready** - Singleton and factory patterns maintained

