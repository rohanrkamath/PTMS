from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import List

class SprintStatus(str, Enum):
    active = "Active"
    completed = "Completed"
    planned = "Planned"

class SprintBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: SprintStatus
    project_id: str  
    sprint_goal: Optional[str] = None

class SprintCreate(SprintBase):
    pass

class SprintUpdate(SprintBase):
    pass

class SprintInDB(SprintBase):
    members: Optional[List[str]] = []
    sprint_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    updated_by: Optional[str]
    created_by: str

# one epic -> many tasks; taskid contains epic id
# one sprint -> many tasks; taskid contains sprintid