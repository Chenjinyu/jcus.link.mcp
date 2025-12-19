# Quick Start Guide

## Running the MCP Server

### Step 1: Install Dependencies

```bash
cd /Users/jinyuchen/ForFamilyPrjs/jcus.link.mcp
uv sync
```

### Step 2: Configure Environment (Optional)

Create a `.env` file:

```env
# Server
HOST=0.0.0.0
PORT=8000

# LLM (optional - will use simulated responses if not set)
LLM_PROVIDER=anthropic
LLM_API_KEY=your_key_here

# Vector DB (optional - will use simulated data if not set)
VECTOR_DB_TYPE=supabase
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

### Step 3: Start the Server

```bash
# Option 1: Using the run script
uv run python run_server.py

# Option 2: Direct module execution
uv run python -m src.mcp_server

# Option 3: Using uvicorn
uv run uvicorn src.mcp_server:mcp.app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000` with the MCP endpoint at `http://localhost:8000/mcp`.

## Example 1: Python FastMCP Client

### Run the Example

```bash
uv run python examples/python_client.py
```

### Code Example

```python
import asyncio
import json
from fastmcp import Client

async def main():
    server_url = "http://localhost:8000/mcp"
    
    async with Client(server_url) as client:
        # Upload job description
        result = await client.call_tool(
            "upload_job_description",
            arguments={
                "input_data": "Looking for Python developer...",
                "input_type": "text"
            }
        )
        
        # Parse response
        response = json.loads(result.content[0].text)
        print(f"Job ID: {response['job_id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Example 2: TypeScript Client

### Install Dependencies

```bash
npm install @modelcontextprotocol/sdk
# or
yarn add @modelcontextprotocol/sdk
```

### Run the Simple Example (using fetch API)

```bash
npx ts-node examples/typescript_client_simple.ts
# or
tsx examples/typescript_client_simple.ts
```

### Code Example (Simple - using fetch)

```typescript
class SimpleMCPClient {
  constructor(private baseUrl: string) {}

  async callTool(name: string, args: Record<string, any>) {
    const response = await fetch(`${this.baseUrl}/messages/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "tools/call",
        params: { name, arguments: args }
      })
    });
    return await response.json();
  }
}

// Usage
const client = new SimpleMCPClient("http://localhost:8000");
const result = await client.callTool("upload_job_description", {
  input_data: "Looking for Python developer...",
  input_type: "text"
});
```

### Run the Full SDK Example

```bash
npx ts-node examples/typescript_client.ts
```

## Available Tools

1. **upload_job_description** - Upload job description (text, file, or URL)
2. **search_matching_resumes** - Search for matching resumes
3. **list_matched_job_descriptions** - List all uploaded jobs
4. **analyze_job_description** - Analyze job requirements
5. **generate_resume** - Generate optimized resume

## Available Resources

- `resume://matches/{job_id}` - Get matched resumes
- `resume://job/{job_id}` - Get job description

## Testing the Server

### Using curl

```bash
# List tools
curl -X POST http://localhost:8000/mcp/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool
curl -X POST http://localhost:8000/mcp/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "upload_job_description",
      "arguments": {
        "input_data": "Looking for Python developer",
        "input_type": "text"
      }
    }
  }'
```

## Troubleshooting

1. **Server won't start**: Check if port 8000 is available
2. **Connection refused**: Make sure the server is running
3. **Import errors**: Make sure dependencies are installed with `uv sync`
4. **TypeScript errors**: Make sure `@modelcontextprotocol/sdk` is installed

## Next Steps

- See `examples/README.md` for detailed documentation
- Customize the examples for your use case
- Add authentication if needed
- Configure vector database and LLM providers

