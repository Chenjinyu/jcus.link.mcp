# Why Transport Configuration is Needed

## Overview

FastMCP supports **three different transport types** for communication between clients and servers. The transport determines **how MCP protocol messages are sent and received**. You must specify which transport to use because each has different characteristics and use cases.

## The Three Transport Types

### 1. **stdio** (Standard Input/Output) - Default
```python
mcp.run()  # Defaults to stdio
# or explicitly:
mcp.run(transport="stdio")
```

**How it works:**
- Uses standard input/output streams
- Messages sent via stdin/stdout
- **Use case**: Command-line tools, local scripts, CLI applications

**Example:**
```bash
# Server reads from stdin, writes to stdout
python server.py | client.py
```

**Characteristics:**
- ✅ Simple, no network setup needed
- ✅ Works for local tools
- ❌ Not suitable for web applications
- ❌ Can't be accessed via HTTP

---

### 2. **sse** (Server-Sent Events)
```python
mcp.run(transport="sse")
```

**How it works:**
- HTTP-based transport using Server-Sent Events (SSE)
- Client connects via HTTP GET to receive events
- Messages sent via HTTP POST
- **Use case**: Web applications, real-time updates

**Example:**
```python
# Client connects to: http://localhost:8000/sse
# Sends messages to: http://localhost:8000/messages/
```

**Characteristics:**
- ✅ Works over HTTP
- ✅ Real-time streaming via SSE
- ✅ Good for web applications
- ⚠️ Being superseded by streamable-http (newer standard)

---

### 3. **streamable-http** (Streamable HTTP) - **Recommended for Production**
```python
mcp.run(transport="streamable-http")
```

**How it works:**
- HTTP-based transport with streaming support
- Uses HTTP POST for requests
- Supports both JSON responses and SSE streaming
- **Use case**: Production web servers, scalable applications

**Example:**
```python
# Client connects to: http://localhost:8000/mcp
# Endpoint: http://localhost:8000/mcp
```

**Characteristics:**
- ✅ **Recommended for production** (per FastMCP docs)
- ✅ Works over HTTP/HTTPS
- ✅ Supports stateless operation (`stateless_http=True`)
- ✅ Can return JSON responses (`json_response=True`)
- ✅ Better scalability than SSE
- ✅ Modern MCP standard

---

## Why You Need to Specify Transport

### 1. **Different Communication Protocols**

Each transport uses a completely different communication method:

| Transport | Protocol | Network | Use Case |
|-----------|----------|---------|----------|
| `stdio` | stdin/stdout | ❌ No | CLI tools |
| `sse` | HTTP + SSE | ✅ Yes | Web apps (legacy) |
| `streamable-http` | HTTP + Streaming | ✅ Yes | Production web servers |

### 2. **Different Server Implementations**

FastMCP creates different server implementations based on transport:

```python
# stdio transport
async def run_stdio_async(self):
    # Uses stdin/stdout streams
    async with stdio_server() as (read, write):
        await self._mcp_server.run(read, write, ...)

# sse transport  
async def run_sse_async(self):
    # Creates Starlette app with SSE endpoints
    app = self.sse_app()
    uvicorn.run(app, host=..., port=...)

# streamable-http transport
async def run_streamable_http_async(self):
    # Creates Starlette app with HTTP endpoints
    app = self.streamable_http_app()
    uvicorn.run(app, host=..., port=...)
```

### 3. **Different Client Connection Methods**

Clients must use the matching transport:

**stdio:**
```python
# Not applicable - uses pipes
```

**sse:**
```python
from fastmcp import Client
client = Client("http://localhost:8000/sse")  # SSE endpoint
```

**streamable-http:**
```python
from fastmcp import Client
client = Client("http://localhost:8000/mcp")  # HTTP endpoint
```

### 4. **Different Endpoints and Paths**

Each transport exposes different endpoints:

| Transport | Endpoint | Path Configuration |
|-----------|----------|-------------------|
| `stdio` | N/A (pipes) | N/A |
| `sse` | `/sse` | `sse_path="/sse"` |
| `streamable-http` | `/mcp` | `streamable_http_path="/mcp"` |

---

## Why We Use `streamable-http` in This Project

### Your Use Case
You're building a **web application** (Next.js) that needs to:
- ✅ Connect to the MCP server via HTTP
- ✅ Upload job descriptions
- ✅ Receive streaming responses
- ✅ Scale in production

### Why `streamable-http` is Best

1. **Production Ready**
   - Recommended by FastMCP for production deployments
   - Better scalability than SSE
   - Supports stateless operation

2. **HTTP-Based**
   - Works with web applications
   - Can be accessed from browsers
   - Standard HTTP/HTTPS protocol

3. **Flexible Response Format**
   - Can use JSON responses (`json_response=True`)
   - Or SSE streaming for real-time updates
   - Better for API integrations

4. **Modern Standard**
   - Part of the latest MCP specification
   - SSE is being superseded by streamable-http

---

## What Happens Without Specifying Transport?

If you don't specify transport, FastMCP defaults to **`stdio`**:

```python
mcp.run()  # Defaults to "stdio"
```

**Problem:**
- Server tries to read from stdin/write to stdout
- **No HTTP server is created**
- Can't be accessed via web/HTTP
- Your Next.js app can't connect to it

**Error you'd see:**
- Server starts but no HTTP endpoints
- Client connection fails
- "Connection refused" or "No route found"

---

## Configuration in Your Project

### Current Setup

```python
# main_fastmcp.py
mcp = FastMCP(
    name=settings.app_name,
    version=settings.app_version,
    host=settings.host,        # HTTP server host
    port=settings.port,        # HTTP server port
    streamable_http_path="/mcp",  # Endpoint path
    # ... other settings
)

# run_server.py
mcp.run(transport="streamable-http")  # ✅ Use HTTP transport
```

### What This Does

1. **Creates HTTP Server**: FastMCP creates a Starlette/ASGI app
2. **Exposes Endpoint**: Available at `http://host:port/mcp`
3. **Handles Requests**: Processes MCP protocol messages over HTTP
4. **Supports Streaming**: Can stream responses for long operations

---

## Alternative: If You Want SSE Instead

If you preferred SSE (though not recommended), you'd use:

```python
mcp.run(transport="sse")
```

**Differences:**
- Endpoint would be at `/sse` instead of `/mcp`
- Uses Server-Sent Events for streaming
- Older standard, being phased out

---

## Summary

**Why specify transport?**
1. **Different protocols** - stdio vs HTTP vs SSE
2. **Different server types** - CLI vs Web server
3. **Different endpoints** - Different URL paths
4. **Different use cases** - Local tools vs Web apps

**Why `streamable-http` for your project?**
- ✅ You're building a web application
- ✅ Need HTTP access from Next.js
- ✅ Production-ready and scalable
- ✅ Modern MCP standard
- ✅ Recommended by FastMCP

**Without transport specification:**
- ❌ Defaults to stdio (CLI mode)
- ❌ No HTTP server created
- ❌ Can't connect from web applications

