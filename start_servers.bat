@echo off
REM Batch script to start both servers for the Todo Application

echo Starting Todo Application Servers...
echo =====================================

REM Start MCP server in a new window
start "MCP Server" cmd /k "cd /d "%~dp0mcp_server" && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a bit for the MCP server to start
timeout /t 3 /nobreak >nul

REM Start Backend server in a new window
start "Backend Server" cmd /k "cd /d "%~dp0backend" && python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"

echo Both servers started in separate windows.
echo MCP Server: http://localhost:8001
echo Backend Server: http://localhost:8000
pause