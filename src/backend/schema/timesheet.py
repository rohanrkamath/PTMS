from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

class TimeSheetStatus(str, Enum):
    reviewing = "Reviewing"
    approved = "Approved"
    denied = "Denied"

class TimesheetEntry(BaseModel):
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    status: TimeSheetStatus = TimeSheetStatus.reviewing

    class Config:
        orm_mode = True

class TimeSheetinDB(TimesheetEntry):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user: str

