#!/usr/bin/env python3
"""
Run the FastMCP server
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.main_fastmcp import mcp, settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server will run on http://{settings.host}:{settings.port}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    logger.info(f"MCP endpoint: http://{settings.host}:{settings.port}/mcp")
    
    # Run FastMCP server using StreamableHTTP transport
    # The host and port are set during FastMCP initialization in main_fastmcp.py
    mcp.run(transport="streamable-http")

