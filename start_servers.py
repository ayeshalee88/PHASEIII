#!/usr/bin/env python3
"""
Start script for Todo Application Servers
Starts both the FastAPI backend and MCP server simultaneously
"""
import subprocess
import sys
import os
import signal
import time
from threading import Thread
import argparse


def run_server(command, name):
    """Run a server process"""
    print(f"Starting {name}...")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Print output in real-time
        for line in process.stdout:
            print(f"[{name}] {line.strip()}")
        
        process.wait()
        return process.returncode
    except KeyboardInterrupt:
        print(f"\nShutting down {name}...")
        return 0


def start_mcp_server():
    """Start the MCP server on port 8001"""
    cmd = "cd mcp_server && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
    return run_server(cmd, "MCP Server (8001)")


def start_backend_server():
    """Start the main backend server on port 8000"""
    cmd = "cd backend && python main.py"
    return run_server(cmd, "Backend Server (8000)")


def start_both_servers():
    """Start both servers in separate threads"""
    print("Starting Todo Application Servers...")
    print("=====================================")
    
    # Start MCP server thread
    mcp_thread = Thread(target=start_mcp_server, daemon=True)
    mcp_thread.start()
    
    # Give MCP server a moment to start
    time.sleep(2)
    
    # Start backend server thread
    backend_thread = Thread(target=start_backend_server, daemon=True)
    backend_thread.start()
    
    try:
        # Wait for both threads to complete
        mcp_thread.join()
        backend_thread.join()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Shutting down servers...")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='Start Todo Application Servers')
    parser.add_argument('--mcp-only', action='store_true', help='Start only the MCP server')
    parser.add_argument('--backend-only', action='store_true', help='Start only the backend server')
    
    args = parser.parse_args()
    
    if args.mcp_only:
        start_mcp_server()
    elif args.backend_only:
        start_backend_server()
    else:
        start_both_servers()


if __name__ == "__main__":
    main()