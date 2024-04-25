from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4

class Status(str, Enum):
    to_do = "to_do"
    doing = "doing"
    done = "done"

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class SubTaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: str
    epic_id: str
    task_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Status
    priority: Priority
    members: Optional[List[str]] = None

class SubTaskCreate(SubTaskBase):
    pass

class SubTaskUpdate(SubTaskBase):
    pass

class SubTaskInDB(SubTaskBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    subtask_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    created_by: str