# database/config.py - Updated to use DATABASE_URL environment variable
from sqlmodel import SQLModel, create_engine, Session
from core.config import settings
import os

# Import all models to register them with SQLModel
from models.user_model import User
from models.task_models import Task
from models.conversation_models import Conversation, Message, ToolInvocation

print(f"DEBUG: settings.database_url = '{settings.database_url}'")
print(f"DEBUG: DATABASE_URL env var = '{os.getenv('DATABASE_URL')}'")

# Ensure we have a valid database URL - prioritize environment variable
database_url = os.getenv("DATABASE_URL") or settings.database_url or "sqlite:///./todo.db"

if not database_url or database_url.strip() == "":
    database_url = "sqlite:///./todo.db"
    print(f"WARNING: Using fallback database URL: {database_url}")

print(f"DEBUG: Final database_url = '{database_url}'")

# Create database engine
engine = create_engine(
    database_url,
    echo=False,  # Set to False to reduce logs
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    pool_pre_ping=True  # Helps with connection issues
)


# Create all tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Session generator
def get_session():
    with Session(engine) as session:
        yield session