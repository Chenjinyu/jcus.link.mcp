# MCP Resume Server - Project Structure

## Best Practice Folder Structure

```
mcp-resume-server/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuration and environment variables
│   ├── core/
│   │   ├── __init__.py
│   │   ├── mcp_protocol.py          # MCP protocol models and types
│   │   └── exceptions.py            # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py           # LLM integration
│   │   ├── vector_service.py        # Vector database operations
│   │   └── resume_service.py        # Resume generation logic
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── mcp_handler.py           # MCP protocol handlers
│   │   └── http_handler.py          # HTTP endpoint handlers
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base tool class
│   │   ├── search_tool.py           # Resume search tool
│   │   ├── analysis_tool.py         # Job analysis tool
│   │   └── generation_tool.py       # Resume generation tool
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mcp_models.py            # MCP data models
│   │   └── domain_models.py         # Domain-specific models
│   └── utils/
│       ├── __init__.py
│       ├── logging.py               # Logging configuration
│       └── helpers.py               # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_services/
│   ├── test_handlers/
│   └── test_tools/
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── README.md
└── pyproject.toml                   # Modern Python project config
```

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Services are injected, not hardcoded
3. **Single Source of Truth**: Configuration in one place
4. **Testability**: Easy to mock and test each component
5. **Scalability**: Easy to add new tools and services
6. **Type Safety**: Full type hints throughout

## Module Responsibilities

### src/config/
- Environment variables
- Application settings
- Feature flags
- API keys management

### src/core/
- Core business logic
- Protocol definitions
- Shared exceptions
- Base classes

### src/services/
- External service integrations
- Business logic
- Stateful operations
- Database connections

### src/handlers/
- Request handling
- Response formatting
- Protocol translation
- HTTP/MCP routing

### src/tools/
- MCP tool implementations
- Tool registration
- Tool execution logic

### src/models/
- Data models
- Pydantic schemas
- Type definitions
- Validation logic

### src/utils/
- Helper functions
- Utilities
- Decorators
- Common operations