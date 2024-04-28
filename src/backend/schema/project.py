from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4

class Active(str, Enum):
    ongoing = "ongoing"
    completed = "completed"

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    members: Optional[List[str]] = None
    active: Optional[Active] = Active.ongoing

class ProjectCreate(ProjectBase):
    pass

class NameUpdate(BaseModel):
    new_name: str

class DescriptionUpdate(BaseModel):
    new_description: str

class StartDateUpdate(BaseModel):
    new_start_date: datetime

class EndDateUpdate(BaseModel):
    new_end_date: datetime

class MembersUpdate(BaseModel):
    new_members: List[str]

class StatusUpdate(BaseModel):
    new_status: str

class ProjectInDB(ProjectBase):
    project_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    updated_by: Optional[str]
    created_by: Optional[str]



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
