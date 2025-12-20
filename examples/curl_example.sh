#!/bin/bash
# Simple curl example for FastMCP server
# 
# The issue: FastMCP requires session initialization before calling tools

SERVER="http://localhost:8000/mcp"

echo "=== Step 1: Initialize Session ==="
# Initialize and capture headers
INIT_RESPONSE=$(curl -s -i -X POST "$SERVER" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl", "version": "1.0"}
    }
  }')

# Extract session ID from headers
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -i "mcp-session-id:" | cut -d: -f2 | tr -d ' \r\n')
PROTOCOL_VERSION=$(echo "$INIT_RESPONSE" | grep -i "mcp-protocol-version:" | cut -d: -f2 | tr -d ' \r\n')

echo "Session ID: $SESSION_ID"
echo "Protocol Version: $PROTOCOL_VERSION"
echo ""

if [ -z "$SESSION_ID" ]; then
  echo "❌ Failed to get session ID. Full response:"
  echo "$INIT_RESPONSE"
  exit 1
fi

echo "=== Step 2: Send Initialized Notification ==="
curl -s -X POST "$SERVER" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }' > /dev/null
echo "✅ Initialized"
echo ""

echo "=== Step 3: Call Tool ==="
curl -X POST "$SERVER" \
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
  }'

echo ""
echo ""
echo "✅ Done!"

