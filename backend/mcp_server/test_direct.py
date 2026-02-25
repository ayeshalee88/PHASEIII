from shared_database import get_direct_session
from backend.models.task_models import Task
from sqlmodel import select

session = get_direct_session()
try:
    # Try to query existing tasks
    statement = select(Task).limit(5)
    tasks = session.exec(statement).all()
    print(f"Found {len(tasks)} tasks")
    if tasks:
        print("First task:", tasks[0].title, tasks[0].id)
    
    # Try to create a new task
    from datetime import datetime
    import uuid
    
    new_task = Task(
        title="Test from direct connection",
        description="Testing direct connection",
        user_id="c8675942-e120-472d-8eb6-4e6acab1596c",
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    print(f"Created task with ID: {new_task.id}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()