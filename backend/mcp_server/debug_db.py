from shared_database import get_current_engine, SQLModel
from backend.models.task_models import Task

engine = get_current_engine()
print("Engine URL:", engine.url)

# Check if the Task model is properly configured
print("Task table name:", getattr(Task, '__tablename__', 'NO TABLENAME'))
print("Task metadata tables:", list(SQLModel.metadata.tables.keys()))

# Try to reflect the actual database tables
from sqlalchemy import inspect
inspector = inspect(engine)
db_tables = inspector.get_table_names()
print("Actual database tables:", db_tables)