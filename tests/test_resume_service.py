# tests/conftest.py
"""
Pytest configuration and fixtures
"""

import pytest
from typing import AsyncGenerator

from src.config import settings
from src.services import get_llm_service, get_vector_service, get_resume_service
from src.tools import get_tool_registry
from src.handlers import get_mcp_handler, get_http_handler


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    return settings


@pytest.fixture
def llm_service():
    """Get LLM service instance"""
    return get_llm_service()


@pytest.fixture
def vector_service():
    """Get vector service instance"""
    return get_vector_service()


@pytest.fixture
def resume_service():
    """Get resume service instance"""
    return get_resume_service()


@pytest.fixture
def tool_registry():
    """Get tool registry instance"""
    return get_tool_registry()


@pytest.fixture
def mcp_handler():
    """Get MCP handler instance"""
    return get_mcp_handler()


@pytest.fixture
def http_handler():
    """Get HTTP handler instance"""
    return get_http_handler()


@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    We are looking for a Senior Software Engineer with:
    - 5+ years of experience with Python and TypeScript
    - Experience with FastAPI and React
    - Cloud deployment experience (AWS/GCP)
    - Strong problem-solving skills
    """


@pytest.fixture
def sample_resume_matches():
    """Sample resume matches for testing"""
    from src.models import ResumeMatch
    
    return [
        ResumeMatch(
            resume_id="resume_1",
            content="Senior Software Engineer with 5 years Python experience",
            skills=["Python", "FastAPI", "AWS"],
            experience_years=5,
            similarity_score=0.92
        ),
        ResumeMatch(
            resume_id="resume_2",
            content="Full Stack Developer with TypeScript and React",
            skills=["TypeScript", "React", "Node.js"],
            experience_years=3,
            similarity_score=0.85
        )
    ]


@pytest.fixture
def sample_mcp_request():
    """Sample MCP request for testing"""
    from src.core import MCPRequest
    
    return MCPRequest(
        jsonrpc="2.0",
        id=1,
        method="tools/list"
    )


# Async fixtures
@pytest.fixture
async def async_llm_service() -> AsyncGenerator:
    """Async LLM service fixture"""
    service = get_llm_service()
    yield service
    # Cleanup if needed


@pytest.fixture
async def async_vector_service() -> AsyncGenerator:
    """Async vector service fixture"""
    service = get_vector_service()
    yield service
    # Cleanup if needed