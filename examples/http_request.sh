#!/bin/bash
# Example: Making HTTP requests to FastMCP server using curl
# 
# FastMCP streamable-http transport requires session management:
# 1. First, send an "initialize" request to get a session ID
# 2. Use that session ID in subsequent requests

SERVER_URL="http://localhost:8000/mcp"

echo "==========================initialize method to get session ID=============================="
echo "Step 1: Initialize session to get session ID"


# Step 1: Initialize the session
INIT_RESPONSE=$(curl -s -X POST "$SERVER_URL" \
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
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }')

echo "=========================initialize response========================="
echo "$INIT_RESPONSE"

echo "Initialize response:"
echo "$INIT_RESPONSE" | jq '.' 2>/dev/null || echo "$INIT_RESPONSE"
echo ""

# Extract session ID from response headers (if using SSE, it's in headers)
# For JSON response, check the response body
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -i "mcp-session-id" | head -1 | cut -d: -f2 | tr -d ' \r\n' || echo "")

# Alternative: Extract from response if it's in the body
# For streamable-http, session ID is usually in response headers
# Let's get it from the actual HTTP headers
echo "==========================initialize method to get session ID from headers=============================="
echo "Step 2: Get session ID from headers"
INIT_HEADERS=$(curl -s -i -X POST "$SERVER_URL" \
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
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }')

echo "=========================INIT_HEADERS========================="
echo "$INIT_HEADERS"

SESSION_ID=$(echo "$INIT_HEADERS" | grep -i "mcp-session-id:" | head -1 | cut -d: -f2 | tr -d ' \r\n')
PROTOCOL_VERSION=$(echo "$INIT_HEADERS" | grep -i "mcp-protocol-version:" | head -1 | cut -d: -f2 | tr -d ' \r\n')

echo "Session ID: $SESSION_ID"
echo "Protocol Version: $PROTOCOL_VERSION"
echo ""

if [ -z "$SESSION_ID" ]; then
  echo "❌ Error: Could not extract session ID. Response:"
  echo "$INIT_HEADERS"
  exit 1
fi

echo "Step 3: Send initialized notification"
echo "==========================Send initialized notification=============================="
curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }' > /dev/null

echo "✅ Initialized notification sent"
echo ""

echo "Step 4: Call a tool (search_matching_resumes)"
echo "=============================================="

RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_matching_resumes",
      "arguments": {
        "job_description": "Python developer with FastAPI experience",
        "top_k": 5
      }
    }
  }')

echo "Tool call result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "✅ Request completed!"

