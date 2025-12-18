# Architecture Diagram - MCP Resume Server

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                      │
│  (TypeScript Backend, Web Browser, Mobile App, CLI Tools)       │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTP/SSE
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Server                          │
│                          (main.py)                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CORS Middleware                                         │   │
│  │  Route Registration                                      │   │
│  │  Lifespan Management                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────┬─────────────────────────────────┬───────────────────┘
            │                                 │
   ┌────────▼──────────┐           ┌──────────▼─────────┐
   │  MCP Protocol     │           │   HTTP REST        │
   │  /mcp/message     │           │   Endpoints        │
   └────────┬──────────┘           └─────────┬──────────┘
            │                                │
            ↓                                ↓
┌───────────────────────┐         ┌───────────────────────┐
│   handlers/           │         │   handlers/           │
│   mcp_handler.py      │         │   http_handler.py     │
│                       │         │                       │
│  - handle_message()   │         │  - handle_upload()    │
│  - route methods      │         │  - handle_search()    │
│  - error handling     │         │  - handle_generate()  │
└──────────┬────────────┘         └──────────┬────────────┘
           │                                 │
           │    ┌────────────────────────────┘
           │    │
           ↓    ↓
┌──────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              services/resume_service.py                │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  - search_matching_resumes()                     │  │  │
│  │  │  - analyze_job_description()                     │  │  │
│  │  │  - generate_optimized_resume()                   │  │  │
│  │  │  - process_job_description_workflow()            │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └─────────────────┬──────────────────┬───────────────────┘  │
│                    │                  │                      │
│         ┌──────────▼─────┐  ┌─────────▼──────┐              │
│         │  LLM Service   │  │ Vector Service │              │
│         │                │  │                │              │
│         └────────────────┘  └────────────────┘              │
└──────────────────────────────────────────────────────────────┘
           │                  │
           │                  │
┌──────────▼──────────┐  ┌────▼──────────────┐
│  services/          │  │  services/        │
│  llm_service.py     │  │  vector_service.py│
│                     │  │                   │
│  ┌──────────────┐   │  │  ┌─────────────┐  │
│  │ Anthropic    │   │  │  │ ChromaDB    │  │
│  │ (Claude)     │   │  │  │             │  │
│  └──────────────┘   │  │  └─────────────┘  │
│                     │  │                   │
│  ┌──────────────┐   │  │  ┌─────────────┐  │
│  │ OpenAI       │   │  │  │ Pinecone    │  │
│  │ (GPT)        │   │  │  │             │  │
│  └──────────────┘   │  │  └─────────────┘  │
└─────────────────────┘  └───────────────────┘
           │                       │
           ↓                       ↓
┌─────────────────────┐  ┌────────────────────┐
│  External APIs      │  │  Vector Database   │
│  - Anthropic API    │  │  - Embeddings      │
│  - OpenAI API       │  │  - Similarity      │
└─────────────────────┘  └────────────────────┘
```

## 🔧 Tool Execution Flow

```
MCP Request → mcp_handler.py → ToolRegistry
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ↓                ↓                ↓
          ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐
          │  search_tool.py │ │ analysis_    │ │ generation_   │
          │                 │ │ tool.py      │ │ tool.py       │
          │  - get_def()    │ │              │ │               │
          │  - execute()    │ │ - get_def()  │ │ - get_def()   │
          └────────┬────────┘ │ - execute()  │ │ - execute()   │
                   │          └──────┬───────┘ └───────┬───────┘
                   │                 │                 │
                   └─────────────────┼─────────────────┘
                                     ↓
                           resume_service.py
                                     │
                    ┌────────────────┼────────────────┐
                    ↓                ↓                ↓
            llm_service.py   vector_service.py   (orchestration)
```

## 📦 Module Dependencies

```
main.py
  ├── config/settings.py
  ├── handlers/mcp_handler.py
  │     ├── core/mcp_protocol.py
  │     ├── core/exceptions.py
  │     └── tools/ (registry)
  │           ├── tools/base.py
  │           ├── tools/search_tool.py
  │           ├── tools/analysis_tool.py
  │           └── tools/generation_tool.py
  │                 └── services/resume_service.py
  │                       ├── services/llm_service.py
  │                       │     └── config/settings.py
  │                       └── services/vector_service.py
  │                             └── config/settings.py
  └── handlers/http_handler.py
        ├── services/resume_service.py
        ├── models/domain_models.py
        └── core/exceptions.py
```

## 🔄 Request Flow Examples

### Example 1: Search Resumes (HTTP)

```
1. HTTP POST /search-matches
   ↓
2. main.py → http_handler.handle_search_matches()
   ↓
3. http_handler → resume_service.search_matching_resumes()
   ↓
4. resume_service → vector_service.embed_text()
   ↓
5. resume_service → vector_service.similarity_search()
   ↓
6. vector_service → ChromaDB/Pinecone
   ↓
7. Results flow back up the chain
   ↓
8. HTTP Response with ResumeMatch[]
```

### Example 2: Generate Resume (MCP)

```
1. MCP Request: tools/call (generate_resume)
   ↓
2. main.py → mcp_handler.handle_message()
   ↓
3. mcp_handler → tool_registry.get_tool("generate_resume")
   ↓
4. tool_registry → generation_tool.execute()
   ↓
5. generation_tool → resume_service.generate_optimized_resume()
   ↓
6. resume_service → llm_service.generate_resume()
   ↓
7. llm_service → Anthropic/OpenAI API
   ↓
8. Stream chunks back through the chain
   ↓
9. MCP Response with generated resume
```

## 🎯 Configuration Flow

```
Environment Variables (.env)
          ↓
config/settings.py (Pydantic validation)
          ↓
     Settings singleton
          ↓
   ┌──────┴──────┐
   │             │
   ↓             ↓
LLM Service   Vector Service
   │             │
   ↓             ↓
Anthropic     ChromaDB
/OpenAI       /Pinecone
```

## 🏛️ Layered Architecture

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                  │
│  (main.py, HTTP endpoints, MCP protocol)    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Handler Layer                       │
│  (mcp_handler.py, http_handler.py)          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Business Logic Layer                │
│  (resume_service.py, tool implementations)  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Service Layer                       │
│  (llm_service.py, vector_service.py)        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Integration Layer                   │
│  (External APIs, Databases)                 │
└─────────────────────────────────────────────┘
```

## 🔐 Security Layers

```
Request
  ↓
CORS Middleware
  ↓
Input Validation (Pydantic)
  ↓
Business Logic
  ↓
API Key Management (env vars)
  ↓
External Services
  ↓
Response
```

## 💾 Data Flow

```
Job Description (Text)
         ↓
  vector_service.embed_text()
         ↓
   Embedding (Vector)
         ↓
  vector_service.similarity_search()
         ↓
  ResumeMatch[] (Ranked)
         ↓
  llm_service.generate_resume()
         ↓
  Generated Resume (Text)
```

## 🎨 Factory Pattern Implementation

```
                 Factory
                    │
        ┌───────────┴───────────┐
        │                       │
    LLMServiceFactory    VectorServiceFactory
        │                       │
    ┌───┴───┐              ┌────┴────┐
    │       │              │         │
Anthropic OpenAI      ChromaDB  Pinecone
```

## 🔄 Singleton Pattern

```
First Call:
  get_llm_service() → Create instance → Store globally → Return

Subsequent Calls:
  get_llm_service() → Return cached instance
```

## 📊 Component Communication

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│  Tool   │ ──────→ │ Service │ ──────→ │ External│
│  Layer  │         │  Layer  │         │   API   │
└─────────┘         └─────────┘         └─────────┘
    ↑                    ↑                    ↓
    │                    │                    │
    │                    └────────────────────┘
    │                         (Async)
    │
    └──── Registry (manages tool instances)
```

## 🚀 Deployment Architecture

```
                Load Balancer
                      │
         ┌────────────┼────────────┐
         ↓            ↓            ↓
    Instance 1   Instance 2   Instance 3
    (Worker 1)   (Worker 2)   (Worker 3)
         │            │            │
         └────────────┼────────────┘
                      │
         ┌────────────┼────────────┐
         ↓            ↓            ↓
    Anthropic     ChromaDB      Redis
       API         Cloud        Cache
```

## 📈 Scalability Points

1. **Horizontal Scaling**: Multiple worker processes
2. **Service Isolation**: Can separate vector DB to different server
3. **Caching Layer**: Redis for frequently accessed embeddings
4. **Load Balancing**: Distribute requests across instances
5. **Async Operations**: Non-blocking I/O throughout

## 🎯 Key Design Decisions

1. **Why Abstract Base Classes?**
   - Easy to swap implementations (e.g., switch from Anthropic to OpenAI)
   - Enforces consistent interface
   - Simplifies testing with mocks

2. **Why Singleton Services?**
   - Avoid recreating expensive connections
   - Centralized state management
   - Resource efficiency

3. **Why Factory Pattern?**
   - Configuration-driven initialization
   - Hide implementation details
   - Easy to extend with new providers

4. **Why Separate Handlers?**
   - Clean separation of concerns
   - Protocol-specific logic isolated
   - Easy to test independently

5. **Why Tool Registry?**
   - Dynamic tool discovery
   - Easy to add new tools
   - Centralized tool management

---

This architecture provides a **clean, maintainable, and scalable** foundation for the MCP Resume Server! 🚀