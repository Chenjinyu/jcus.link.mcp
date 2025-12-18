"""Configuration management for the application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS Configuration
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")

    # Vector Database Configuration
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "memory")  # memory, chroma, etc.
    CHROMA_DB_PATH: Optional[str] = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_EXTENSIONS: set[str] = {
        ".pdf",
        ".doc",
        ".docx",
        ".html",
        ".htm",
        ".txt",
    }

    @classmethod
    def validate(cls) -> None:
        """Validate that required settings are present."""
        if not cls.ANTHROPIC_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError(
                "Either ANTHROPIC_API_KEY or OPENAI_API_KEY must be set in environment variables"
            )


# Global settings instance
settings = Settings()

