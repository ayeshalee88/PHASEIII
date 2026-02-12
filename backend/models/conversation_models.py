from sqlmodel import SQLModel, Field
from sqlalchemy import Text
from typing import Optional
from datetime import datetime
import uuid
import json


# Conversation models
class ConversationBase(SQLModel):
    pass


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(SQLModel):
    pass


class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_at: datetime


# Database model for conversations
class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Message models
class MessageBase(SQLModel):
    role: str  # 'user', 'assistant', 'tool'
    content: str


class MessageCreate(MessageBase):
    conversation_id: str


class MessageUpdate(SQLModel):
    content: Optional[str] = None


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    timestamp: datetime


# Database model for messages
class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    conversation_id: str = Field(foreign_key="conversations.id")
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Tool Invocation models
class ToolInvocationBase(SQLModel):
    pass


class ToolInvocationCreate(SQLModel):
    conversation_id: str
    tool_name: str
    parameters_json: str
    result_json: Optional[str] = None


class ToolInvocationUpdate(SQLModel):
    result_json: Optional[str] = None


class ToolInvocationResponse(SQLModel):
    id: str
    conversation_id: str
    tool_name: str
    parameters_json: str
    executed_at: datetime
    result_json: Optional[str]


# Database model for tool invocations
class ToolInvocation(SQLModel, table=True):
    __tablename__ = "tool_invocations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    conversation_id: str = Field(foreign_key="conversations.id")
    tool_name: str
    parameters_json: str = Field(sa_column=Text)
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    result_json: Optional[str] = Field(default=None, sa_column=Text)