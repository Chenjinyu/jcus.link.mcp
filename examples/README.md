# MCP Client Examples

This directory contains examples for connecting to the MCP server using different client libraries.

## Prerequisites

### Python Client
```bash
# Install dependencies (if not already installed)
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
uv sync

# The fastmcp package includes the client
```

### TypeScript Client
```bash
# Install MCP SDK
npm install @modelcontextprotocol/sdk

# Or using yarn
yarn add @modelcontextprotocol/sdk

# For running TypeScript files
npm install -g ts-node
# or
npm install -g tsx
```

## Running the Server

### Option 1: Using the run script
```bash
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
uv run python run_server.py
```

### Option 2: Direct Python module
```bash
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
uv run python -m src.mcp_server
```

### Option 3: Using uvicorn directly
```bash
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
uv run uvicorn src.mcp_server:mcp.app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000` with the MCP endpoint at `http://localhost:8000/mcp`.

## Running the Examples

### Python Client Example

```bash
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
uv run python examples/python_client.py
```

This will:
1. Connect to the MCP server
2. Upload a job description
3. Search for matching resumes
4. Analyze the job description
5. List all job descriptions
6. Read a resource

### TypeScript Client Example

```bash
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
npx ts-node examples/typescript_client.ts
# or
tsx examples/typescript_client.ts
```

## Server Endpoints

- **MCP Endpoint**: `http://localhost:8000/mcp`
- **SSE Endpoint**: `http://localhost:8000/mcp` (GET for SSE)
- **HTTP POST**: `http://localhost:8000/mcp` (POST for messages)

## Available Tools

1. **upload_job_description** - Upload a job description (text, file, or URL)
2. **search_matching_resumes** - Search for resumes matching a job description
3. **list_matched_job_descriptions** - List all uploaded job descriptions
4. **analyze_job_description** - Analyze a job description to extract requirements
5. **generate_resume** - Generate an optimized resume based on job description

## Available Resources

1. **resume://matches/{job_id}** - Get matched resumes for a job
2. **resume://job/{job_id}** - Get a job description by ID

## Available Prompts

1. **resume_generation_prompt** - Template for generating resumes
2. **job_analysis_prompt** - Template for analyzing job descriptions

## Environment Variables

Create a `.env` file in the project root:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# LLM Configuration
LLM_PROVIDER=anthropic
LLM_API_KEY=your_anthropic_api_key
LLM_MODEL=claude-sonnet-4-20250514

# Vector Database
VECTOR_DB_TYPE=supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# File Upload
ALLOW_URL_UPLOADS=true
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## Troubleshooting

### Connection Issues

1. **Server not running**: Make sure the server is running on `http://localhost:8000`
2. **CORS errors**: Check that CORS is configured correctly in settings
3. **Transport errors**: FastMCP uses SSE (Server-Sent Events) by default

### TypeScript Client Issues

1. **Module not found**: Make sure `@modelcontextprotocol/sdk` is installed
2. **Transport errors**: The TypeScript SDK may need different transport configuration for FastMCP

### Python Client Issues

1. **Import errors**: Make sure you're using `uv run` or have activated the virtual environment
2. **Connection refused**: Check that the server is running and accessible

## Next Steps

- Customize the examples for your use case
- Add error handling and retry logic
- Implement progress callbacks for long-running operations
- Add authentication if your server requires it

