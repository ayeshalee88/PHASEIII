from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from typing import Optional
from datetime import datetime
import uuid

# Base models for requests/responses
class UserBase(SQLModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    name: Optional[str] = None


class UserLoginResponse(UserResponse):
    access_token: str
    refresh_token: str
    token_type: str

# Database model - simplified to work with either SQLite or PostgreSQL
class User(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    password: str = Field(sa_column=Column("password_hash", String, nullable=False))  # Maps to password_hash column in DB
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    name: Optional[str] = Field(default=None, sa_column=Column("name", String, nullable=True))  # Optional field