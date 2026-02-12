---
title: "Backend-Frontend-Database Tech Stack Selection"
status: "Accepted"
date: "2026-01-11"
---

# Backend-Frontend-Database Tech Stack Selection

## Context

The project requires evolving from a Phase I console-based Python app to a full-stack web application with authentication and persistent storage. We need to select technology stacks for the backend, frontend, and database that align with the project constitution and requirements.

## Decision

We will use the following integrated technology stack:
- **Backend**: FastAPI with SQLModel for API development and database modeling
- **Frontend**: Next.js (App Router) for the user interface
- **Database**: Neon Serverless PostgreSQL for data persistence
- **Structure**: Monorepo with separate backend and frontend directories

## Status

Accepted

## Date

2026-01-11

## Context

- Need to build a modern, scalable full-stack application
- Requirements specify FastAPI + SQLModel backend, Next.js frontend, and PostgreSQL
- Must maintain incremental evolution from Phase I Python foundation
- Need to ensure real-world alignment with industry practices
- Must support authentication and user-scoped data access

## Decision

The technology stack will consist of:

**Backend**: FastAPI framework with SQLModel ORM
- FastAPI for high-performance API development with automatic documentation
- SQLModel for typed database models and queries
- Pydantic for request/response validation

**Frontend**: Next.js with App Router
- Next.js 14 with App Router for modern React development
- Server Components for optimized rendering
- Built-in API routes for backend communication

**Database**: Neon Serverless PostgreSQL
- PostgreSQL for robust relational data storage
- Neon's serverless offering for automatic scaling
- Support for advanced SQL features and ACID transactions

**Repository Structure**: Monorepo with separate services
- Clear separation of concerns between frontend and backend
- Single repository for easier coordination and deployment
- Independent deployability while maintaining coordination

## Consequences

### Positive
- FastAPI provides automatic API documentation and validation
- Next.js offers excellent developer experience and performance
- PostgreSQL provides mature, reliable data storage
- Type safety across the stack with TypeScript/Python typing
- Strong ecosystem and community support
- Good performance characteristics for both backend and frontend
- Easy integration between components

### Negative
- Learning curve for team members unfamiliar with these technologies
- Potential complexity in local development setup
- Vendor lock-in risk with Neon's serverless PostgreSQL features
- Larger initial setup compared to simpler stacks

## Alternatives

### Alternative 1: Different Backend Framework
- Express.js with Sequelize ORM
- Pros: Simpler, more familiar to many developers
- Cons: Less automatic validation and documentation, more boilerplate code

### Alternative 2: Different Frontend Framework
- React with Vite + vanilla REST client
- Pros: More flexibility, lighter weight
- Cons: Less integrated solution, more manual work for routing and optimization

### Alternative 3: Different Database Solution
- MongoDB with Prisma ORM
- Pros: Flexible schema, good for unstructured data
- Cons: Doesn't align with requirements specifying PostgreSQL, different query paradigm

## References

- specs/main/plan.md
- specs/main/research.md
- specs/main/data-model.md