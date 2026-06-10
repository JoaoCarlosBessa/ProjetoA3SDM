from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = None
    priority: Literal["low", "medium", "high"] = "medium"


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    completed: Optional[bool] = None


class TaskRead(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Literal["low", "medium", "high"]
    completed: bool
    created_at: datetime
    updated_at: datetime
