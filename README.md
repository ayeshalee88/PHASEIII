# Full-Stack Todo Web Application

This is a monorepo containing both the frontend and backend for a todo application.

## Overview

This is a full-stack todo application built with:
- **Backend**: FastAPI with SQLModel and PostgreSQL
- **Frontend**: Next.js with TypeScript
- **Authentication**: JWT-based authentication
- **Database**: Neon Serverless PostgreSQL

The application supports multi-user functionality with secure authentication and authorization.

## Features

- User authentication (sign up and sign in)
- Create, read, update, and delete tasks
- Track task completion status
- Multi-user support with data isolation
- RESTful API design
- Modern web interface

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.13+ (for backend)
- PostgreSQL database (Neon recommended)

## Project Structure

```
todo-app/
├── backend/              # FastAPI backend
│   ├── src/              # Main application code
│   ├── api/              # API routes
│   ├── models/           # Data models
│   ├── database/         # Database configuration
│   ├── auth/             # Authentication utilities
│   └── core/             # Core configuration
├── frontend/             # Next.js frontend
│   ├── pages/            # Next.js pages
│   ├── components/       # React components
│   ├── styles/           # CSS styles
│   ├── public/           # Static assets
│   └── lib/              # Utility functions
├── specs/                # Specification files
└── history/              # Prompt history records
```

## Getting Started

### Backend
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run the server: `uvicorn src.main:app --reload`

### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`

## Environment Variables

Create a `.env` file in the backend directory with the following:

```
DATABASE_URL=postgresql://username:password@localhost/todo_db
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login

### Task Management
- `GET /api/users/{user_id}/tasks` - Get all tasks for a user
- `POST /api/users/{user_id}/tasks` - Create a new task
- `GET /api/users/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/users/{user_id}/tasks/{task_id}` - Update a task
- `DELETE /api/users/{user_id}/tasks/{task_id}` - Delete a task
- `PATCH /api/users/{user_id}/tasks/{task_id}/complete` - Update task completion status