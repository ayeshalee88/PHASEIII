# MCP Server Setup Guide

This document explains how to set up and run the MCP (Model Context Protocol) server for the Todo AI Chatbot.

## Server Configuration

- **MCP Server**: Runs on port 8001
- **Backend Server**: Runs on port 8000
- **Database**: Uses shared SQLite database at `backend/todo.db`

## Available Tools

The MCP server provides the following tools for the AI agent:

1. **add_task** - Add a new task to the user's todo list
2. **list_tasks** - List all tasks for a user with position numbers
3. **update_task** - Update an existing task by position number
4. **complete_task** - Mark a task as complete/incomplete by position number
5. **delete_task** - Delete a task by position number

## Starting the Servers

### Method 1: Using Python Script (Recommended)

```bash
# Install dependencies for MCP server
cd mcp_server
pip install -r requirements.txt

# Install dependencies for backend
cd ../backend
pip install -r requirements.txt

# Go back to main directory and start both servers
cd ..
python start_servers.py
```

### Method 2: Using Batch Script (Windows)

```bash
# Run the batch script to start both servers in separate windows
start_servers.bat
```

### Method 3: Manual Start

Start each server separately:

```bash
# Terminal 1: Start MCP server
cd mcp_server
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Start Backend server
cd backend
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

### Common Issues:

1. **Connection refused errors**: Make sure the MCP server is running on port 8001
2. **Database connection errors**: Verify that the `backend/todo.db` file exists
3. **Import errors**: Ensure all dependencies are installed in both servers

### Verifying Server Status:

- MCP Server health check: `http://localhost:8001/docs`
- Backend Server health check: `http://localhost:8000/docs`

## Environment Variables

The servers use the following environment variables:

- `MCP_SERVER_URL`: Should be set to `http://localhost:8001` (used by backend to call MCP tools)
- Database configuration is handled automatically through shared database file

## Auto-Restart

The Python script (`start_servers.py`) will keep the servers running. If you need auto-restart functionality on crashes, consider using process managers like `supervisor` or `pm2`.

For development, the `--reload` flag will automatically restart the servers when code changes are detected.