from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from models.task_models import Task, TaskCreate, TaskUpdate, TaskResponse
from database.config import get_session
from core.exceptions import TaskNotFoundException

router = APIRouter()


@router.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
def get_tasks(user_id: str, session: Session = Depends(get_session)):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()


@router.post("/users/{user_id}/tasks", response_model=TaskResponse)
def create_task(
    user_id: str,
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    # Create task with user_id
    db_task = Task(**task.model_dump(), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str,
    task_id: str,
    session: Session = Depends(get_session)
):
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise TaskNotFoundException(task_id)

    return task


@router.put("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    db_task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not db_task:
        raise TaskNotFoundException(task_id)

    for k, v in task_update.dict(exclude_unset=True).items():
        setattr(db_task, k, v)

    db_task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(db_task)
    return db_task


@router.delete("/users/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: str,
    session: Session = Depends(get_session)
):
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise TaskNotFoundException(task_id)

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.patch(
    "/users/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse
)
def update_task_completion(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise TaskNotFoundException(task_id)

    task.completed = task_update.completed
    task.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(task)
    return task


# Health check endpoint
@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "tasks-api"}
