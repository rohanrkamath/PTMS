from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4

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
    id: str = Field(default_factory=lambda: str(uuid4()))
    sprint_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    created_by: str

# one epic -> many tasks; taskid contains epic id
# one sprint -> many tasks; taskid contains sprintid