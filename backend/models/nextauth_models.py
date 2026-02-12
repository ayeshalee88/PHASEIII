from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, String, Boolean, Integer
from sqlalchemy.sql import func


class User(SQLModel, table=True):
    __tablename__ = "User"  # Match Prisma schema

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: Optional[str] = Field(sa_column=Column(String))
    email: str = Field(sa_column=Column(String, unique=True, nullable=False))
    emailVerified: Optional[datetime] = Field(sa_column=Column(DateTime))
    image: Optional[str] = Field(sa_column=Column(String))
    password: Optional[str] = Field(sa_column=Column(String))  # Store hashed password
    createdAt: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updatedAt: datetime = Field(sa_column=Column(DateTime, default=func.now(), onupdate=func.now()))


class Account(SQLModel, table=True):
    __tablename__ = "Account"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    userId: str = Field(sa_column=Column(String, nullable=False))
    type: str = Field(sa_column=Column(String, nullable=False))
    provider: str = Field(sa_column=Column(String, nullable=False))
    providerAccountId: str = Field(sa_column=Column(String, nullable=False))
    refresh_token: Optional[str] = Field(sa_column=Column(String))
    access_token: Optional[str] = Field(sa_column=Column(String))
    expires_at: Optional[int] = Field(sa_column=Column(Integer))
    token_type: Optional[str] = Field(sa_column=Column(String))
    scope: Optional[str] = Field(sa_column=Column(String))
    id_token: Optional[str] = Field(sa_column=Column(String))
    session_state: Optional[str] = Field(sa_column=Column(String))


class Session(SQLModel, table=True):
    __tablename__ = "Session"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    sessionToken: str = Field(sa_column=Column(String, unique=True, nullable=False))
    userId: str = Field(sa_column=Column(String, nullable=False))
    expires: datetime = Field(sa_column=Column(DateTime, nullable=False))


class VerificationToken(SQLModel, table=True):
    __tablename__ = "VerificationToken"

    id: Optional[str] = Field(default=None, primary_key=True)
    identifier: str = Field(sa_column=Column(String, nullable=False))
    token: str = Field(sa_column=Column(String, unique=True, nullable=False))
    expires: datetime = Field(sa_column=Column(DateTime, nullable=False))