# ADR 004: AI Chatbot Architecture with MCP and OpenAI Agents

## Status
Accepted

## Date
2026-02-05

## Context
For Phase III of the Todo application, we need to transform the existing full-stack web application into an AI-powered chatbot that allows users to manage their todos through natural language conversation. The system must maintain the architectural principles established in the Phase III constitution, specifically focusing on:

- Agent-first architecture where all task management logic is driven by AI agents via MCP tools
- Strict statelessness with no in-memory conversation or task state in backend services
- Tool-mediated actions where the AI agent interacts with tasks exclusively through MCP tools
- Natural language fidelity where user intent is interpreted and executed accurately through conversational input
- Clear separation of concerns between UI, agent logic, MCP tools, and persistence

The existing application already has a solid foundation with Next.js frontend, FastAPI backend, SQLModel ORM, and Neon PostgreSQL database, but we need to significantly alter the architecture to support AI-native interactions.

## Decision

We will implement an architecture that separates the system into four distinct layers with clear responsibilities:

### 1. Frontend Layer: OpenAI ChatKit UI
- Replace existing dashboard with OpenAI ChatKit for natural language interface
- Implement conversation display and real-time updates
- Handle API communication with token management

### 2. Backend Service Layer: FastAPI + MCP Integration
- Maintain stateless `/api/{user_id}/chat` endpoint
- Implement conversation history reconstruction from database
- Handle authentication validation
- Integrate with OpenAI Agents SDK
- Optionally embed MCP server or deploy separately

### 3. MCP Tooling Layer: Official MCP SDK
- Expose all task operations as callable tools (add, list, update, complete, delete)
- Implement strict parameter validation
- Perform all database operations through MCP tools
- Maintain complete statelessness
- Define clear tool contracts with input/output schemas

### 4. Data Layer: Neon Serverless PostgreSQL
- Extend schema for conversation storage and message history
- Implement user-scoped isolation
- Support role-based attribution (user/assistant/tool)
- Enable deterministic conversation reconstruction

## Alternatives Considered

### Alternative 1: Direct Database Access by AI Agent
Instead of using MCP tools, allow the AI agent to directly interact with the database.

**Pros:**
- Fewer layers and potentially better performance
- Simpler architecture with fewer moving parts

**Cons:**
- Violates Phase III constitution requirement for tool-mediated actions only
- Breaks separation of concerns principle
- Reduces auditability and tool invocation transparency
- Makes it difficult to enforce business logic and validation rules

### Alternative 2: Stateful Agent with Memory
Maintain agent state in memory between requests for better context awareness.

**Pros:**
- Potentially better conversation context retention
- Faster response times without database lookups
- More natural conversation flow

**Cons:**
- Violates strict statelessness requirement in constitution
- Doesn't scale horizontally well
- Conversations would be lost on server restarts
- Breaks deterministic conversation reconstruction requirement

### Alternative 3: Rule-Based Intent Classification
Implement custom NLP for intent classification instead of relying on OpenAI agent's natural language processing.

**Pros:**
- More predictable and controllable behavior
- Potentially more cost-effective
- Better for handling specific, structured commands

**Cons:**
- Violates constitution's principle of natural language fidelity
- Requires extensive manual rule maintenance
- Less flexible for natural conversation patterns
- Doesn't leverage AI capabilities effectively

## Consequences

### Positive Consequences
- **Scalability**: Stateless architecture enables horizontal scaling
- **Robustness**: Conversations survive server restarts due to persistent storage
- **Auditability**: All actions are logged through tool invocation records
- **Separation of Concerns**: Clear boundaries between UI, agent logic, tools, and data
- **AI-Native Experience**: Natural language interface feels intuitive to users
- **Maintainability**: Each layer has distinct, well-defined responsibilities

### Negative Consequences
- **Complexity**: Additional layers and infrastructure components increase system complexity
- **Performance**: Database lookups for each request may impact response times
- **Cost**: Additional API calls to OpenAI and potential MCP infrastructure costs
- **Latency**: Multiple network hops between components may increase latency

## Implementation Approach

### Phase 1: Infrastructure Setup
- Extend database schema for conversation history
- Implement MCP tool server with task operation tools
- Set up OpenAI agent with tool configurations

### Phase 2: Core Integration
- Connect FastAPI chat endpoint to OpenAI agent
- Implement conversation history reconstruction
- Add authentication validation

### Phase 3: UI Enhancement
- Replace existing UI with OpenAI ChatKit
- Add conversation display and input handling
- Show tool invocations in chat interface

### Phase 4: Testing & Optimization
- Comprehensive testing of natural language commands
- Performance optimization for conversation reconstruction
- Error handling and edge case validation

## Technical Details

### MCP Tool Contracts
- `add_task(title: str, description: Optional[str]) -> TaskResponse`
- `list_tasks() -> List[TaskResponse]`
- `update_task(task_id: str, title: Optional[str], description: Optional[str]) -> TaskResponse`
- `complete_task(task_id: str) -> TaskResponse`
- `delete_task(task_id: str) -> dict`

### Database Extensions
- `conversations` table with user_id, conversation_id, created_at
- `messages` table with conversation_id, role, content, timestamp
- `tool_invocations` table with conversation_id, tool_name, parameters, result

### API Endpoint
- `POST /api/{user_id}/chat` - Stateless chat endpoint
- Request: `{message: str}`
- Response: `{conversation_id: str, response: str, tool_calls: List[dict]}`

## Validation Criteria

- All task operations work through natural language commands
- Conversations resume correctly after server restarts
- Tool calls are logged and returned in API responses
- Backend remains stateless between requests
- Authentication is properly enforced
- System handles ambiguous or invalid inputs gracefully

## Notes
This ADR aligns with the Phase III constitution and ensures that the implementation maintains agent-first architecture, strict statelessness, and proper separation of concerns while enabling rich natural language interactions for todo management.