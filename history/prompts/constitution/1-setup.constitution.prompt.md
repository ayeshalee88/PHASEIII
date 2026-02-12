---
id: 1
title: Setup constitution
stage: constitution
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution, setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - CLAUDE.md
tests:
---

## Prompt

/sp.constitution
Phase II – Full-Stack Todo Web Application

## Authority
This document defines the mandatory rules governing all Phase II work.
All specifications, plans, tasks, and implementations must comply with these rules.

---

## Development Rules

- Development must follow the Spec-Kit workflow:
  constitution → specification → plan → task → implementation
- No phase may be skipped
- No implementation may begin before tasks are approved
- Manual coding by humans is prohibited
- Claude Code is the only entity allowed to generate or modify code

---

## Spec Governance Rules

- Specifications are the single source of truth
- Code must follow specifications exactly
- Specifications may not be changed during implementation
- Any required change must restart the workflow at specification

---

## Architecture Rules

- Frontend, backend, and database must be logically separated
- No business logic may exist in the frontend
- Backend must not depend on frontend runtime behavior

---

## Security Rules

- All backend API endpoints require authentication
- Authentication must be verified server-side
- Backend must not trust client-supplied user identifiers
- Authorization decisions must be enforced on every request

---

## Data Isolation Rules

- Each task belongs to exactly one user
- Users may only access their own tasks
- Data ownership must be enforced at query level

---

## Technology Constraints

- Frontend: Next.js (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon PostgreSQL
- Authentication: Better Auth with JWT

---

## Repository Rules

- Monorepo structure is mandatory
- Frontend and backend reside in separate directories
- All specifications live under `/specs`
- Specs must be referenced using Spec-Kit paths

---

## Completion Rules

- Phase II is complete only when all specified features work end-to-end
- All rules in this constitution must be satisfied

---

End of `/sp.constitution`

## Response snapshot

I'll help you work with the constitution for your Phase II Full-Stack Todo Web Application. This document establishes the mandatory rules that govern all development work.

Let me create a Prompt History Record (PHR) for this constitution work as required by the Claude Code Rules:

## Outcome

- ✅ Impact: Constitution document created and PHR recorded
- 🧪 Tests: No tests needed for constitution setup
- 📁 Files: .specify/memory/constitution.md, CLAUDE.md
- 🔁 Next prompts: Specification creation for the todo app
- 🧠 Reflection: Constitution follows Spec-Kit workflow requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin specification phase