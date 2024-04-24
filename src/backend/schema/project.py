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

# class User(BaseModel):
#     user_id: str

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    members: Optional[List[str]] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDB(ProjectBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    created_by: str



# class Epic(BaseModel):
#     _id: str = Field(..., alias="id")
#     name: str
#     description: Optional[str]
#     project_id: str
#     start_date: Optional[datetime]
#     end_date: Optional[datetime]

# class EpicCreate(Epic):
#     pass

# class EpicUpdate(Epic):
#     pass

# class Task(BaseModel):
#     _id: str = Field(..., alias="id")
#     name: str
#     description: Optional[str]
#     task_type: str
#     project_id: str
#     epic_id: str
#     status: Status
#     priority: Priority 
#     assignee: User
#     members: Optional[List[User]]

# class TaskCreate(Task):
#     pass

# class TaskUpdate(Task):
#     pass

# class SubTask(BaseModel):
#     _id: str = Field(..., alias="id")
#     name: str
#     description: Optional[str]
#     project_id: str
#     epic_id: str
#     task_id: str
#     time_to_be_spent: int
#     status: Status 
#     priority: Priority 
#     assignee: User
#     members: Optional[List[User]]

# class SubTaskCreate(SubTask):
#     pass

# class SubTaskUpdate(SubTask):
#     pass

# class Sprint(BaseModel):
#     _id: str = Field(..., alias="id")
#     name: str
#     goal: str
#     start_date: datetime
#     end_date: datetime
#     associated_tasks: List[Task]

# class Timesheet(BaseModel):
#     _id: str = Field(..., alias="id")
#     user_id: User
#     # subtask_id: Subtask
#     hours_worked: int
#     date: datetime
#     is_billable: bool
#     status: Status
