from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus
    priority: int = Field(..., ge=1, le=5)

    @field_validator('title')
    def validate_title(cls, v):
        if len(v) < 3:
            raise ValueError('title must be at least 3 characters')
        return v

class Task(TaskCreate):
    id: int
    owner_id: int

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class User(BaseModel):
    id: int
    role: str

class Message(BaseModel):
    type: str
    text: Optional[str] = None
    username: Optional[str] = None
    room_id: Optional[str] = None
    detail: Optional[str] = None