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
    task_type: Optional[TaskType] = TaskType.task
    project_id: str
    epic_id: str
    sprint_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[Status] = Status.to_do
    priority: Optional[Priority] = Priority.low
    members: Optional[List[str]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskInDB(TaskBase):
    task_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    updated_by: Optional[str]
    created_by: str

# class NameUpdate(BaseModel):
#     new_name: str

# class DescriptionUpdate(BaseModel):
#     new_description: str

# class TaskTypeUpdate(BaseModel):
#     new_task_type: TaskType

# class SprintIdUpdate(BaseModel):
#     new_sprint_id: str

# class DateUpdate(BaseModel):
#     new_date: datetime

# class StatusUpdate(BaseModel):
#     new_status: Status

# class PriorityUpdate(BaseModel):
#     new_priority: Priority

# class MembersUpdate(BaseModel):
#     new_members: List[EmailStr]
