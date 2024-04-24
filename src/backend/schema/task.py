from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4

class TaskType(str, Enum):
    task = "Task"
    story = "Story"
    bug = "Bug"

class Status(str, Enum):
    to_do = "to_do"
    doing = "doing"
    done = "done"

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    task_type: TaskType
    project_id: str
    epic_id: str
    status: Status
    priority: Priority
    members: Optional[List[str]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskInDB(TaskBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    created_by: str
