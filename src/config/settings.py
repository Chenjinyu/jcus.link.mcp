# src/config/settings.py
"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "resume-matching-mcp-server"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # MCP Protocol
    mcp_protocol_version: str = "2024-11-05"
    
    # Vector Database
    vector_db_type: str = "chromadb"  # chromadb, pinecone, weaviate
    vector_db_host: Optional[str] = None
    vector_db_port: Optional[int] = None
    vector_db_collection: str = "resumes"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # LLM Service
    llm_provider: str = "anthropic"  # anthropic, openai
    llm_model: str = "claude-sonnet-4-20250514"
    llm_api_key: Optional[str] = None
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.7
    
    # OpenAI (alternative)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list[str] = [".txt", ".pdf", ".doc", ".docx"]
    
    # Resume Generation
    default_top_k: int = 5
    min_similarity_threshold: float = 0.5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience function to get settings
settings = get_settings()