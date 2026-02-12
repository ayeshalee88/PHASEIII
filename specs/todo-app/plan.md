# Phase III Implementation Plan - Todo AI Chatbot using MCP and OpenAI Agents

## Current State Analysis

Based on review of existing frontend and backend structure:
- **Frontend**: Next.js app with dashboard, login, signup pages
- **Backend**: FastAPI with SQLModel, supporting task CRUD operations and authentication
- **Database**: Neon PostgreSQL with task and user models
- **Authentication**: Better Auth integration

## High-Level Architecture Sketch

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Frontend Layer                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  OpenAI ChatKit UI                    │                                         │
│  - Natural language interface         │                                         │
│  - Conversation display               │                                         │
│  - Real-time updates                  │                                         │
│                                       │                                         │
│  API Client                          │                                         │
│  - /api/{user_id}/chat endpoint      │                                         │
│  - Token management                  │                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Backend Service Layer                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  FastAPI Backend                     │  │  MCP Server                          │
│  - /api/{user_id}/chat endpoint     │  │  - Tool definitions                   │
│  - Stateless conversation handler   │  │  - Task operation tools              │
│  - Request reconstruction            │  │  - Database operations               │
│  - Response aggregation             │  │  - Statelessness guarantee           │
│  - Authentication validation        │  │                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             Data Layer                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Neon Serverless PostgreSQL          │                                         │
│  - Conversation storage              │                                         │
│  - Message history                   │                                         │
│  - Task data with lifecycle meta     │                                         │
│  - User authentication data         │                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AI Agent Layer                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  OpenAI Agents SDK                   │                                         │
│  - Natural language processing       │                                         │
│  - Tool selection logic              │                                         │
│  - Action orchestration              │                                         │
│  - Response generation              │                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## System Responsibilities

### Chat Handling (FastAPI Backend)
- **Stateless chat endpoint** (`POST /api/{user_id}/chat`)
  - Accept user messages and user_id
  - Reconstruct conversation history from database
  - Invoke OpenAI agent with conversation context
  - Aggregate responses and tool calls
  - Persist conversation history to database
- **Authentication validation** via Better Auth tokens
- **Request/response structure** includes conversation_id, messages, and tool invocations

### Agent Orchestration (OpenAI Agents SDK)
- **Natural language intent interpretation** from user messages
- **Tool selection** based on conversation context and intent
- **Action orchestration** through chained MCP tool calls
- **Response generation** with natural language confirmations
- **Error handling** for ambiguous or invalid requests

### MCP Tooling (Official MCP SDK)
- **Expose task operations** as callable tools (add, list, update, complete, delete)
- **Parameter validation** for all tool inputs
- **Database operations** for task management
- **Statelessness** - no session or in-memory storage
- **Tool contracts** with clear input/output schemas

### Persistence (Neon Serverless PostgreSQL + SQLModel)
- **Conversation storage** with user-scoped isolation
- **Message history** with role-based attribution (user/assistant/tool)
- **Tool invocation logs** for audit and debugging
- **Deterministic reconstruction** of conversation context

## Development Approach

### Research-Concurrent Development Approach

#### Research Areas to Investigate While Building:
1. **OpenAI Agents SDK Patterns** - Best practices for tool orchestration
   - Reference: OpenAI API Documentation (OpenAI, 2023)
2. **MCP SDK Implementation** - Official Model Context Protocol patterns
   - Reference: MCP Specification (Anthropic, 2024)
3. **ChatKit Integration** - Optimal conversational UI patterns
   - Reference: OpenAI ChatKit Documentation (OpenAI, 2024)

#### Foundation Phase:
- MCP tool contracts definition
- Database schema extensions for conversations
- Agent initialization and configuration
- Authentication integration points

#### Analysis Phase:
- Natural language intent mapping
- Error handling strategies
- Performance considerations for state reconstruction
- Scalability assessment

#### Synthesis Phase:
- End-to-end flow validation
- Performance tuning
- Production readiness checks

## Key Decisions Requiring Documentation

| Decision | Options | Tradeoffs | Recommendation |
|----------|---------|-----------|----------------|
| MCP Server Deployment | Separate server vs Embedded in FastAPI | Modularity vs Complexity | Embedded initially, separate later |
| Conversation Reconstruction | Full history vs Windowed context | Completeness vs Performance | Windowed with configurable size |
| Tool Call Transparency | Visible in UI vs Internal logging | Transparency vs UI Cleanliness | Both - visible to user, logged internally |
| Authentication Boundary | Chat endpoint vs MCP tools | Simplicity vs Security | Chat endpoint for simplicity |
| Agent State Management | Persistent agent vs New instance per request | Performance vs Statelessness | New instance per request (stateless) |

## Testing Strategy

| Test Category | Validation Method | Success Criteria |
|---------------|-------------------|------------------|
| Natural Language Processing | Send varied commands ("add a task", "show my tasks", "mark #1 complete") | Agent selects correct MCP tools |
| Task Lifecycle Operations | Full CRUD via conversation | All operations work through AI interface |
| Conversation Persistence | Server restart test | Conversations resume correctly |
| Authentication | Unauthorized requests | Proper rejection of unauthenticated access |
| Tool Invocation | Monitor tool call logs | All actions map to valid MCP tools |
| Error Handling | Invalid inputs and commands | Graceful handling without crashes |

## Quality Validation Framework

Based on the Phase III Constitution, validation will ensure:
- ✅ **Agent-First Architecture**: All task operations via MCP tools
- ✅ **Strict Statelessness**: No in-memory conversation storage
- ✅ **Natural Language Fidelity**: Intent correctly interpreted
- ✅ **Separation of Concerns**: Clear boundaries maintained
- ✅ **Deterministic Persistence**: Reliable conversation reconstruction

## Technical Implementation Phases

### Phase 1: Infrastructure Setup
- Extend database schema for conversation history
- Implement MCP tool server with task operations
- Set up OpenAI agent configuration

### Phase 2: Core Integration
- Connect FastAPI chat endpoint to OpenAI agent
- Implement conversation history reconstruction
- Add authentication validation

### Phase 3: UI Enhancement
- Replace existing UI with OpenAI ChatKit
- Add conversation display and input handling
- Show tool invocations in chat interface

### Phase 4: Testing & Optimization
- Comprehensive testing of all natural language commands
- Performance optimization for conversation reconstruction
- Error handling and edge case validation

## References
- Anthropic. (2024). *Model Context Protocol Specification*. Anthropic.
- OpenAI. (2023). *OpenAI API Documentation*. OpenAI.
- OpenAI. (2024). *OpenAI ChatKit Documentation*. OpenAI.