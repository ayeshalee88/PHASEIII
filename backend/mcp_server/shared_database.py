from sqlmodel import SQLModel, create_engine, Session
from typing import Optional
from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Calculate the absolute path to the backend database
project_root = Path(__file__).parent.parent  # Go up two levels to project root
backend_db_path = project_root / "backend" / "todo.db"

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{backend_db_path.as_posix()}"  # Point to backend's database file
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        
# Create settings instance and ensure database_url is correct
settings = Settings()
# Override the database_url to ensure it always points to the backend database
settings.database_url = f"sqlite:///{backend_db_path.as_posix()}"

import sys
from pathlib import Path
import os
# Add parent directory to Python path
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# Also add the project root to Python path to ensure proper imports
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

# Import all models to register them with SQLModel
from backend.models.task_models import Task
from backend.models.user_model import User
from backend.models.conversation_models import Conversation, Message, ToolInvocation

# Create a function to get the current engine with updated settings
def get_current_engine():
    return create_engine(
        settings.database_url,
        echo=False,  # Set to False to reduce logs
        connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )

# Create all tables
def create_db_and_tables():
    engine = get_current_engine()
    SQLModel.metadata.create_all(engine)

# Session generator
def get_session():
    engine = get_current_engine()
    with Session(engine) as session:
        yield session

# Direct session getter for async contexts
def get_direct_session():
    engine = get_current_engine()
    return Session(engine)