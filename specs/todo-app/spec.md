# Phase III – Todo AI Chatbot using MCP and OpenAI Agents

## Target Audience
Developers and evaluators assessing AI-native, agent-driven backend architectures using MCP and stateless design

## Focus
Natural-language task management via AI agents using MCP tools, with stateless backend architecture and persistent conversation memory

---

## Success Criteria

- Users can manage todos entirely through natural language conversation
- AI agent correctly interprets intent and invokes appropriate MCP tools
- All task operations (add, list, update, complete, delete) work conversationally
- Conversation context persists across requests and server restarts
- Agent responses include clear confirmations of actions taken
- Tool calls are observable and returned in API responses

---

## Functional Scope

- Conversational interface for todo management
- Stateless chat API endpoint backed by persistent storage
- AI agent orchestration using OpenAI Agents SDK
- MCP server exposing task operations as tools
- Database-backed conversation and message history
- Frontend chat UI using OpenAI ChatKit

---

## Non-Functional Requirements

- Stateless backend suitable for horizontal scaling
- Deterministic conversation reconstruction per request
- Clear separation between UI, agent logic, MCP tools, and database
- Graceful error handling for ambiguous or invalid user requests
- Professional, minimal chat UI consistent with modern SaaS standards

---

## Constraints

- Backend framework: Python FastAPI only
- AI framework: OpenAI Agents SDK only
- MCP implementation: Official MCP SDK only
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth
- Single chat endpoint (POST /api/{user_id}/chat)
- No manual intent classification or rule-based NLP outside the agent

---

## Data Requirements

- Tasks stored with full lifecycle metadata
- Conversations stored independently per user
- Messages stored with role-based attribution
- Tool invocation metadata captured per assistant response

---

## Out of Scope / Not Building

- Voice input or speech-to-text
- Multi-user shared conversations
- Real-time streaming responses
- Analytics dashboards or reporting
- Task reminders, scheduling, or notifications
- Advanced agent memory beyond persisted chat history
- UI customization beyond professional baseline ChatKit setup

---

## Completion Definition

- A working chatbot that manages todos through conversation
- MCP tools fully control task state
- Backend remains stateless between requests
- Conversations resume correctly after restart
- System behavior aligns with the Phase III constitution

---

End of `/sp.specification`