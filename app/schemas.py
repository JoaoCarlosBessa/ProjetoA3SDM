from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None


class TaskRead(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime
