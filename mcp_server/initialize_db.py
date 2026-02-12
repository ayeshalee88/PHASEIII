import sys
import os
# Add the backend directory to the Python path to import models
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from shared_database import create_db_and_tables

if __name__ == "__main__":
    print("Initializing database tables for MCP server...")
    create_db_and_tables()
    print("Database tables created successfully!")
    print("- Tasks table")
    print("- Users table")
    print("- Conversations table")
    print("- Messages table")
    print("- ToolInvocations table")