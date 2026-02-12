#!/usr/bin/env python3
"""
Simple test to check if the database operations work
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.user_model import User, UserCreate
from database.config import engine
from sqlmodel import Session, select

# Create a new session
with Session(engine) as session:
    print("Checking if user exists in database...")
    
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == "test@example.com")
    ).first()
    
    if existing_user:
        print(f"User already exists: {existing_user.email}")
        # Delete the existing user
        session.delete(existing_user)
        session.commit()
        print("Deleted existing user")
    else:
        print("No existing user found")
    
    print("Creating new user...")
    # Create a new user directly
    from auth.utils import get_password_hash
    
    hashed_password = get_password_hash("password123")
    new_user = User(
        email="test@example.com",
        password=hashed_password,  # This should map to password_hash in DB
        name="Test User"
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    print(f"User created successfully: {new_user.email}, ID: {new_user.id}")
    
    # Verify the user was created
    retrieved_user = session.exec(
        select(User).where(User.email == "test@example.com")
    ).first()
    
    if retrieved_user:
        print(f"User verified in database: {retrieved_user.email}")
        print(f"User ID: {retrieved_user.id}")
        print(f"Has password hash: {'yes' if retrieved_user.password else 'no'}")
        print(f"Has name: {retrieved_user.name}")
    else:
        print("User not found in database after creation!")