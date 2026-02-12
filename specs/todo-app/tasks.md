# Phase III Todo AI Chatbot - Task Breakdown

## Overview
This document breaks down the implementation of the Todo AI Chatbot using MCP and OpenAI Agents into testable, manageable tasks with clear acceptance criteria.

---

## Phase 1: Infrastructure Setup

### Task 1.1: Extend Database Schema for Conversations
**Description**: Add tables and models for storing conversation history, messages, and tool invocations
- Create `Conversation` model with user_id, conversation_id, created_at
- Create `Message` model with conversation_id, role, content, timestamp
- Create `ToolInvocation` model with conversation_id, tool_name, parameters, result
- Update Alembic migrations to include new tables
- Ensure proper foreign key relationships

**Acceptance Criteria**:
- [X] New models are defined with proper relationships
- [X] Alembic migration creates tables successfully
- [X] Database can store and retrieve conversation history
- [X] Foreign key constraints prevent orphaned records

### Task 1.2: Implement MCP Server with Task Tools
**Description**: Create MCP server with all required task operation tools
- Implement `add_task` tool with proper validation
- Implement `list_tasks` tool with user scoping
- Implement `update_task` tool with proper error handling
- Implement `complete_task` tool
- Implement `delete_task` tool
- Add MCP server startup and configuration

**Acceptance Criteria**:
- [X] All 5 task operation tools are available via MCP
- [X] Tools properly validate inputs before database operations
- [X] Tools respect user permissions and task ownership
- [X] MCP server starts successfully and is accessible

### Task 1.3: Set Up OpenAI Agent Configuration
**Description**: Configure OpenAI Agent with MCP tools and proper system instructions
- Initialize OpenAI Agent with MCP tools
- Define system instructions for the agent
- Set up API key configuration and environment variables
- Configure agent parameters for optimal performance

**Acceptance Criteria**:
- [X] OpenAI Agent initializes successfully
- [X] Agent has access to all required MCP tools
- [X] System instructions properly configured
- [X] Environment variables are properly loaded

---

## Phase 2: Core Integration

### Task 2.1: Create Stateless Chat Endpoint
**Description**: Implement the `/api/{user_id}/chat` endpoint that reconstructs conversation history and processes user messages
- Implement conversation history reconstruction from database
- Integrate with OpenAI Agent for message processing
- Implement response aggregation including tool calls
- Add authentication validation using Better Auth

**Acceptance Criteria**:
- [X] Endpoint accepts user messages and user_id
- [X] Conversation history is reconstructed from database
- [X] OpenAI Agent processes messages with context
- [X] Response includes conversation_id, message, and tool calls
- [X] Authentication validation works properly

### Task 2.2: Implement Conversation Persistence
**Description**: Add logic to persist conversations, messages, and tool invocations to database
- Save new conversations to database
- Log user messages to message history
- Log agent responses to message history
- Log tool invocations with parameters and results

**Acceptance Criteria**:
- [X] New conversations are saved to database
- [X] User messages are stored in message history
- [X] Agent responses are stored in message history
- [X] Tool invocations are logged with parameters and results
- [X] All timestamps are correctly recorded

### Task 2.3: Add Authentication Integration
**Description**: Integrate authentication validation with Better Auth into the chat endpoint
- Validate JWT tokens in chat endpoint
- Extract user_id from authenticated requests
- Handle unauthorized requests appropriately
- Ensure user isolation for task access

**Acceptance Criteria**:
- [X] JWT tokens are validated in chat endpoint
- [X] User_id is extracted correctly from authenticated requests
- [X] Unauthorized requests return appropriate error codes
- [X] Users can only access their own tasks and conversations

---

## Phase 3: UI Enhancement

### Task 3.1: Replace Dashboard with ChatKit UI
**Description**: Replace the existing dashboard with OpenAI ChatKit interface
- Install OpenAI ChatKit dependencies
- Replace dashboard.tsx with ChatKit-based UI
- Implement user authentication with ChatKit
- Connect ChatKit to the new chat endpoint

**Acceptance Criteria**:
- [X] ChatKit UI is implemented and functional
- [X] User authentication works with new UI
- [X] Chat interface connects to `/api/{user_id}/chat` endpoint
- [X] Messages display properly in chat interface

### Task 3.2: Add Conversation Display Features
**Description**: Enhance the ChatKit UI to show conversation history and tool invocations
- Load conversation history on initial load
- Display conversation history in chat interface
- Show tool invocations alongside messages
- Implement proper message formatting for tool calls

**Acceptance Criteria**:
- [X] Conversation history loads on initial page load
- [X] Previous messages display in chronological order
- [X] Tool invocations are clearly shown in the chat
- [X] Message formatting distinguishes between user, assistant, and tool messages

### Task 3.3: Implement Chat Input and Submission
**Description**: Handle user input and submission in the ChatKit UI
- Implement message submission to backend
- Handle loading states during agent processing
- Display agent responses and tool calls appropriately
- Handle error states and error messages

**Acceptance Criteria**:
- [X] User can submit messages through UI
- [X] Loading states are shown during processing
- [X] Agent responses are displayed properly
- [X] Error states are handled gracefully

---

## Phase 4: Testing & Optimization

### Task 4.1: Test Natural Language Commands
**Description**: Validate that all natural language commands work through the AI interface
- Test "add a task" commands work correctly
- Test "show my tasks" commands work correctly
- Test "update task" commands work correctly
- Test "complete task" commands work correctly
- Test "delete task" commands work correctly

**Acceptance Criteria**:
- [X] All natural language commands trigger correct MCP tools
- [X] Task operations work correctly through conversation
- [X] Error handling works for invalid commands
- [X] Agent responses are natural and helpful

### Task 4.2: Validate Conversation Persistence
**Description**: Verify that conversations persist across server restarts
- Restart server during active conversation
- Verify conversation history is restored correctly
- Test continued conversation after restart
- Verify no data loss occurs during restart

**Acceptance Criteria**:
- [X] Conversations survive server restarts
- [X] Conversation history is properly reconstructed
- [X] Users can continue conversations after restart
- [X] No data is lost during restart process

### Task 4.3: Performance and Error Testing
**Description**: Conduct performance testing and error handling validation
- Test performance under load
- Validate error handling for invalid inputs
- Test tool invocation logging and monitoring
- Verify rate limiting and security measures

**Acceptance Criteria**:
- [X] System performs well under expected load
- [X] Invalid inputs are handled gracefully
- [X] Tool invocations are properly logged
- [X] Security measures are effective

---

## Out of Scope Tasks
These are intentionally NOT being implemented:
- [X] Voice input or speech-to-text functionality
- [X] Multi-user shared conversations
- [X] Real-time streaming responses
- [X] Advanced agent memory beyond persisted chat history
- [X] Custom UI styling beyond ChatKit default

---

## Prerequisites
Before starting these tasks, ensure:
- [X] Existing Phase II backend is functioning properly
- [X] Database connection is working
- [X] Authentication system is operational
- [X] Development environment has necessary API keys
- [X] OpenAI account and MCP SDK access is available