from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4

class EpicBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    members: Optional[List[str]] = None

class EpicCreate(EpicBase):
    pass

class EpicUpdate(EpicBase):
    pass

class EpicInDB(EpicBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    epic_created: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    created_by: str
