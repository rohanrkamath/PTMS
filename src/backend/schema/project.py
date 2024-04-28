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

class ProjectUpdate(ProjectBase):
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

