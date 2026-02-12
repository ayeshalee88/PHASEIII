"""
Database migration script for the Todo application
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import SQLModel
# ✅ Import from the correct model files
from models.user_model import User
from models.task_models import Task
from database.config import engine

def create_tables():
    """
    Create all tables in the database
    """
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully!")
    print(f"Tables created: {list(SQLModel.metadata.tables.keys())}")

if __name__ == "__main__":
    create_tables()