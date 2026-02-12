#!/usr/bin/env python3
"""
Test script to call the signup function directly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.auth import signup
from models.user_model import UserCreate
from database.config import create_db_and_tables
from sqlmodel import Session
from database.config import engine

# Just ensure tables exist (don't recreate)
print("Ensuring database tables exist...")
# Note: create_db_and_tables() might insert default data, so we skip it for this test
print("Using existing database tables.")

# Create a session
with Session(engine) as session:
    print("Testing signup function...")
    try:
        user_create = UserCreate(email="test@example.com", password="password123")
        result = signup(user_create, session)
        print(f"Signup successful: {result}")
    except Exception as e:
        print(f"Signup failed: {e}")
        import traceback
        traceback.print_exc()