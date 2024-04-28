from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

class TimeSheetStatus(str, Enum):
    reviewing = "Reviewing"
    approved = "Approved"
    denied = "Denied"

class TimeSheetStatusUpdate(BaseModel):
    status: TimeSheetStatus 

# class TimesheetEntry(BaseModel):
#     start_time: datetime
#     end_time: Optional[datetime]
#     status: TimeSheetStatus = None

#     class Config:
#         orm_mode = True

# class TimeSheetinDB(TimesheetEntry):
#     user: str
#     duration: Optional[timedelta]

