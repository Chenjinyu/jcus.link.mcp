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

echo "Step 4: List all tools"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/list"
  }')

echo "Tools list result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "Step 5: Call a tool (search_matching_resumes)"
echo "=============================================="

RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
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

echo "Step 6: List all resources"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "resources/list"
  }')

echo "Resources list result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "Step 7: List matched job descriptions (to get a job_id)"
echo "=============================================="
# First, get a list of available job descriptions to extract a job_id
JOB_LIST_RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "list_matched_job_descriptions"
    }
  }')

echo "Job descriptions list:"
echo "$JOB_LIST_RESULT" | jq '.' 2>/dev/null || echo "$JOB_LIST_RESULT"
echo ""

# Try to extract a job_id from the response (fallback to default if not found)
JOB_ID=$(echo "$JOB_LIST_RESULT" | jq -r '.result.content[0].text' 2>/dev/null | jq -r '.jobs[0].job_id' 2>/dev/null || echo "job_123")
echo "Using job_id: $JOB_ID"
echo ""

echo "Step 8: Read a resource (job description)"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 8,
    \"method\": \"resources/read\",
    \"params\": {
      \"uri\": \"resume://job/${JOB_ID}\"
    }
  }")

echo "Resource read result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "Step 9: Read a resource (matched resumes)"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 9,
    \"method\": \"resources/read\",
    \"params\": {
      \"uri\": \"resume://matches/${JOB_ID}\"
    }
  }")

echo "Matched resumes resource result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "Step 10: List all prompts"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "prompts/list"
  }')

echo "Prompts list result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "Step 11: Get a prompt (job_analysis_prompt)"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 11,
    "method": "prompts/get",
    "params": {
      "name": "job_analysis_prompt",
      "arguments": {
        "job_description": "We are looking for a Senior Python Developer with 5+ years of experience in FastAPI, async programming, and vector databases."
      }
    }
  }')

echo "Prompt result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "Step 12: Get a prompt (resume_generation_prompt)"
echo "=============================================="
RESULT=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "mcp-protocol-version: ${PROTOCOL_VERSION:-2024-11-05}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 12,
    "method": "prompts/get",
    "params": {
      "name": "resume_generation_prompt",
      "arguments": {
        "job_description": "Senior Python Developer with FastAPI experience",
        "matched_resumes": "[{\"resume_id\": \"resume_1\", \"skills\": [\"Python\", \"FastAPI\"], \"experience_years\": 5}]"
      }
    }
  }')

echo "Prompt result:"
echo "$RESULT" | jq '.' 2>/dev/null || echo "$RESULT"
echo ""

echo "✅ All requests completed!"

