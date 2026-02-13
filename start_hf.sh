#!/bin/bash

# Startup script for FastAPI backend + MCP server on Hugging Face Spaces

echo "Starting FastAPI backend + MCP server..."

# Start MCP server in the background on port 8001
echo "Starting MCP server on port 8001..."
cd /app/mcp_server
python server.py &
MCP_PID=$!

# Wait a moment for the MCP server to start
sleep 3

# Check if MCP server started successfully
if ps -p $MCP_PID > /dev/null; then
    echo "MCP server started successfully with PID $MCP_PID"
else
    echo "WARNING: MCP server may not have started properly"
fi

# Start FastAPI on port 7860 (required by Hugging Face)
echo "Starting FastAPI server on port 7860..."
cd /app/backend
exec uvicorn src.app:app --host 0.0.0.0 --port 7860