/sp.constitution

## Project
Phase III – Todo AI Chatbot (MCP + OpenAI Agents)

---

## Vision
To design and implement an AI-native todo application that demonstrates:
- agent-first architecture using MCP tools,
- stateless backend design suitable for horizontal scaling,
- natural language interaction patterns,
- and modern AI integration practices.

The system must enable full todo management through conversational AI while maintaining clear architectural separation between UI, agent logic, MCP tools, and persistence.

---

## Core Principles

### 1. Agent-First Architecture
- All task management logic must be driven by AI agents via MCP tools
- Backend services must not store in-memory conversation or task state
- The AI agent may interact with tasks exclusively through MCP tools

### 2. Strict Statelessness
- Backend services must not store in-memory conversation or task state
- MCP tools must be stateless and rely solely on database reads/writes
- Server restarts must not affect ongoing conversations

### 3. Tool-Mediated Actions Only
- The AI agent may interact with tasks exclusively through MCP tools
- No direct database access is allowed from the agent outside MCP tools
- All task operations must be exposed as MCP tools using the Official MCP SDK

### 4. Natural Language Fidelity
- User intent must be interpreted and executed accurately through conversational input
- The agent must confirm every action in natural language after tool execution
- Error cases (missing task, invalid input) must be handled gracefully and conversationally

### 5. Separation of Concerns
- UI, agent logic, MCP tools, and persistence must remain decoupled
- Frontend communicates only with /api/{user_id}/chat
- Agent communicates only with MCP tools
- MCP server communicates only with the database

### 6. Deterministic Persistence
- Conversation history must be persisted and reconstructed from the database on every request
- Conversation reconstruction must be deterministic and reproducible
- Database is the single source of truth

---

## Key Standards

### General Standards
- All task operations must be exposed as MCP tools using the Official MCP SDK
- The AI agent must be implemented using the OpenAI Agents SDK
- The FastAPI backend must expose one stateless chat endpoint only
- MCP tools fully control task lifecycle

### Architecture Standards
- No manual task routing logic (e.g., if/else intent handling outside the agent)
- No in-memory session storage, caches, or globals for conversation state
- No UI-side business logic for task management
- No direct CRUD endpoints for tasks exposed to the frontend
- Agent must be able to chain multiple MCP tools in one turn

### Data Integrity Standards
- Every user message must be persisted before agent execution
- Every assistant response must be persisted after agent execution
- Tool invocations must be logged and returned in API responses
- Every user message must be persisted before agent execution

---

## Constraints

- No implementation work may begin outside the Spec-Kit workflow order
- Claude Code is the only mechanism allowed for implementation steps
- Backend framework: Python FastAPI only
- AI framework: OpenAI Agents SDK only
- MCP implementation: Official MCP SDK only
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth

---

## Documentation Requirements

- MCP tools must have clear contracts and signatures
- Agent behavior boundaries must be well-defined
- Database interaction model must be documented for stateless chat
- API responses must include conversation_id, assistant response, and tool_calls

---

## Success Criteria

### Functional Success
- Users can manage todos entirely through natural language conversation
- AI agent correctly interprets intent and invokes appropriate MCP tools
- All task operations (add, list, update, complete, delete) work conversationally
- Agent responses include clear confirmations of actions taken

### Architectural Success
- Backend remains stateless between requests
- Conversation context persists across requests and server restarts
- Tool calls are observable and returned in API responses
- System scales horizontally with no shared memory

### Integration Success
- Conversations resume correctly after server restarts
- The chatbot behaves consistently across identical requests
- All natural language commands map to correct MCP tools
- System behavior aligns with these constitutional principles

---

## Non-Goals

- Building traditional command-based interfaces (purely conversational)
- Direct database access from AI agents (MCP tools only)
- In-memory session storage (strictly stateless)
- Manual intent classification outside the agent
- Complex authentication schemes beyond Better Auth

---

## Guiding Metaphor
This system is an **orchestra, not a solo act**.
The AI agent conducts the symphony through MCP tools, with each service playing its designated role in harmony.
