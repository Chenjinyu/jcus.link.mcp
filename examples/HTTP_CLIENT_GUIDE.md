# HTTP Client Guide for FastMCP Server

## Problem: "Missing session ID" Error

FastMCP's `streamable-http` transport requires **session management**. You cannot directly call tools without first establishing a session.

## Solution: Two-Step Process

### Step 1: Initialize Session

First, send an `initialize` request to get a session ID:

```bash
curl -i -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "my-client",
        "version": "1.0.0"
      }
    }
  }'
```

**Response Headers:**
- `mcp-session-id: <session-id>` - Extract this!
- `mcp-protocol-version: <version>` - Extract this!

### Step 2: Send Initialized Notification

After initialize, send the `notifications/initialized` notification:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <SESSION_ID_FROM_STEP_1>" \
  -H "mcp-protocol-version: <VERSION_FROM_STEP_1>" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

### Step 3: Call Tools

Now you can call tools using the session ID:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <SESSION_ID>" \
  -H "mcp-protocol-version: <VERSION>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_matching_resumes",
      "arguments": {
        "job_description": "Python developer",
        "top_k": 5
      }
    }
  }'
```

## Complete Example Script

See `examples/http_request.sh` for a complete bash script that:
1. Initializes the session
2. Extracts session ID from headers
3. Sends initialized notification
4. Calls a tool

## Why Session Management?

FastMCP's streamable-http transport uses sessions to:
- **Track client state** across multiple requests
- **Support streaming responses** (SSE)
- **Enable resumability** (reconnect and resume)
- **Manage protocol version negotiation**

## Alternative: Use FastMCP Client

Instead of raw HTTP, use the FastMCP Python client which handles all this automatically:

```python
from fastmcp import Client

async with Client("http://localhost:8000/mcp") as client:
    result = await client.call_tool("search_matching_resumes", {
        "job_description": "Python developer",
        "top_k": 5
    })
```

## Headers Required

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | ✅ Yes | Must be `application/json` |
| `Accept` | ✅ Yes | Should be `application/json, text/event-stream` |
| `mcp-session-id` | ✅ After init | Session ID from initialize response |
| `mcp-protocol-version` | ✅ After init | Protocol version from initialize response |

## Response Formats

### JSON Response (if `json_response=True` in FastMCP config)
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [...]
  }
}
```

### SSE Response (default)
Server-Sent Events stream with events like:
```
event: message
data: {"jsonrpc": "2.0", "id": 2, "result": {...}}
```

## Troubleshooting

### Error: "Missing session ID"
- **Cause**: You're calling a tool before initializing
- **Fix**: Send `initialize` request first, extract session ID

### Error: "Session has been terminated"
- **Cause**: Session expired or was closed
- **Fix**: Initialize a new session

### Error: "Invalid session ID"
- **Cause**: Session ID format is wrong
- **Fix**: Use the exact session ID from initialize response headers




