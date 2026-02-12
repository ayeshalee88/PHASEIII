---
title: "RESTful API Design with User-Scoped Endpoints"
status: "Accepted"
date: "2026-01-11"
---

# RESTful API Design with User-Scoped Endpoints

## Context

The backend API needs to provide secure access to task management functionality while enforcing proper authorization to ensure users can only access their own data. We need to define a consistent API design pattern that supports these requirements.

## Decision

We will implement a RESTful API design with user-scoped endpoints that enforce authentication and authorization at the route level. This approach provides clear, predictable endpoints with proper security boundaries.

## Status

Accepted

## Date

2026-01-11

## Context

- Need to provide CRUD operations for task management
- Must enforce user-scoped access to data
- Requirements specify RESTful API design with proper status codes
- Need to integrate with JWT-based authentication
- Must support all required operations: create, read, update, delete, toggle completion

## Decision

The API will follow these design patterns:

**RESTful Endpoint Structure**
- Use standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Resource-based URL patterns with user scoping
- Consistent response formats using JSON
- Standard HTTP status codes (200, 201, 204, 400, 401, 404, etc.)

**User-Scoped Endpoints**
- All endpoints include user_id in path: `/api/users/{user_id}/tasks/...`
- Authorization enforced to ensure user_id matches authenticated user
- Users can only access their own tasks

**Security Patterns**
- JWT authentication required for all endpoints
- Authorization checks at endpoint level
- Proper input validation and sanitization
- Consistent error response format

**Supported Operations**
- GET /api/users/{user_id}/tasks - List user's tasks
- POST /api/users/{user_id}/tasks - Create new task
- GET /api/users/{user_id}/tasks/{task_id} - Get specific task
- PUT /api/users/{user_id}/tasks/{task_id} - Update task
- DELETE /api/users/{user_id}/tasks/{task_id} - Delete task
- PATCH /api/users/{user_id}/tasks/{task_id}/complete - Toggle completion

## Consequences

### Positive
- Clear, predictable API structure following REST conventions
- Explicit user scoping prevents unauthorized access
- Standard HTTP methods and status codes
- Good discoverability and ease of use
- Aligns with industry best practices

### Negative
- More verbose URLs due to user scoping
- Potential confusion about user_id in path vs JWT claims
- Slightly more complex authorization logic required

## Alternatives

### Alternative 1: Resource-Only Endpoints
- Use endpoints like /api/tasks with user lookup from JWT
- Pros: Cleaner URLs
- Cons: Less explicit about user scoping, harder to audit

### Alternative 2: GraphQL API
- Use GraphQL for more flexible querying
- Pros: More efficient data fetching, fewer endpoints
- Cons: Doesn't meet requirement specifying RESTful design

### Alternative 3: RPC-Style Endpoints
- Use action-oriented URLs like /api/toggle_task_completion
- Pros: Clear about the action being performed
- Cons: Doesn't follow REST conventions, less discoverable

## References

- specs/main/plan.md
- specs/main/research.md
- specs/main/contracts/todo-api-contract.md