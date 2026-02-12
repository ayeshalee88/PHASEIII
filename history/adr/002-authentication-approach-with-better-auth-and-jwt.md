---
title: "Authentication Approach with Better Auth and JWT"
status: "Accepted"
date: "2026-01-11"
---

# Authentication Approach with Better Auth and JWT

## Context

The application requires secure user authentication with proper authorization to ensure users can only access their own data. We need to select an authentication solution that integrates well with the chosen tech stack and meets security requirements.

## Decision

We will use Better Auth with JWT tokens for stateless authentication across the application. This approach provides a complete authentication solution with secure token management.

## Status

Accepted

## Date

2026-01-11

## Context

- Need to authenticate users for task management functionality
- Requirements specify using Better Auth
- Must ensure user-scoped data access
- Need stateless authentication between frontend and backend
- Must integrate seamlessly with Next.js frontend and FastAPI backend

## Decision

The authentication system will be implemented using:

**Better Auth Library**
- Comprehensive authentication solution with email/password signup/login
- Support for social authentication providers
- Secure password hashing and storage
- Session management capabilities

**JWT Token Strategy**
- Stateless authentication using JSON Web Tokens
- Tokens issued upon successful authentication
- Tokens validated on backend API requests
- Proper token expiration and refresh mechanisms

**Integration Pattern**
- Frontend handles user authentication flow
- JWT tokens stored securely in browser (HTTP-only cookies or secure localStorage)
- Backend validates JWT tokens on all protected endpoints
- User identity derived exclusively from JWT claims

## Consequences

### Positive
- Better Auth provides battle-tested authentication patterns
- JWT enables stateless, scalable authentication
- Good integration with Next.js and FastAPI ecosystems
- Secure token-based authentication without server-side sessions
- Supports both traditional and social login methods

### Negative
- Additional dependency to manage
- Complexity around token security and storage
- Need to handle token expiration and refresh
- Potential for token hijacking if not implemented securely

## Alternatives

### Alternative 1: NextAuth.js
- Popular Next.js authentication solution
- Pros: Great Next.js integration, extensive provider support
- Cons: Doesn't meet requirement specifying Better Auth

### Alternative 2: Custom JWT Implementation
- Build authentication from scratch
- Pros: Complete control over implementation
- Cons: Higher security risk, more development time, reinventing the wheel

### Alternative 3: Session-Based Authentication
- Traditional server-side session storage
- Pros: Simpler token management
- Cons: Doesn't align with stateless architecture requirement, requires server-side storage

## References

- specs/main/plan.md
- specs/main/research.md
- specs/main/contracts/todo-api-contract.md