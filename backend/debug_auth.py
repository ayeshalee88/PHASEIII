#!/usr/bin/env python3
"""
Debug script to test the auth module directly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test importing the modules
try:
    from api.auth import signup, login
    print("[OK] Successfully imported auth functions")
except Exception as e:
    print(f"[ERR] Error importing auth functions: {e}")
    import traceback
    traceback.print_exc()

# Test importing dependencies
try:
    from models.user_model import User, UserCreate, UserResponse
    print("[OK] Successfully imported user models")
except Exception as e:
    print(f"[ERR] Error importing user models: {e}")
    import traceback
    traceback.print_exc()

try:
    from auth.utils import verify_password, get_password_hash, create_access_token
    print("[OK] Successfully imported auth utils")
except Exception as e:
    print(f"[ERR] Error importing auth utils: {e}")
    import traceback
    traceback.print_exc()

try:
    from database.config import get_session
    print("[OK] Successfully imported database config")
except Exception as e:
    print(f"[ERR] Error importing database config: {e}")
    import traceback
    traceback.print_exc()

# Test creating a user object
try:
    user_data = UserCreate(email="test@example.com", password="password123")
    print(f"[OK] Successfully created UserCreate object: {user_data}")
except Exception as e:
    print(f"[ERR] Error creating UserCreate object: {e}")
    import traceback
    traceback.print_exc()

# Test password hashing
try:
    hashed = get_password_hash("password123")
    print(f"[OK] Successfully hashed password: {len(hashed)} chars")
except Exception as e:
    print(f"[ERR] Error hashing password: {e}")
    import traceback
    traceback.print_exc()

print("\nDebugging complete.")