#!/usr/bin/env python3
"""
Test script to verify MCP server can start without import errors
"""
import sys
import os

# Add parent directory to Python path to test imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    print("Testing imports...")
    
    # Test the shared database import
    from mcp_server.shared_database import get_session, engine
    print("✓ Successfully imported shared_database")
    
    # Test the models import
    from backend.models.task_models import Task
    print("✓ Successfully imported Task model")
    
    from backend.models.user_model import User
    print("✓ Successfully imported User model")
    
    from backend.models.conversation_models import Conversation
    print("✓ Successfully imported Conversation model")
    
    print("\nAll imports successful! The MCP server should start without import errors.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)