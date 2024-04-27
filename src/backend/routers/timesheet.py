from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List

from schema.timesheet import TimeSheetinDB, TimesheetEntry
from utils.jwt_validation import get_current_user
from utils.memberCheck import validate_project_members
from utils.idCollectionCheck import check_id_exists, check_epic_belongs_to_project
from database import db, get_db

timesheet = APIRouter(
    prefix="/timesheet",
    tags=["timesheets"],
    dependencies=[Depends(get_current_user)]
)

timesheets_collection = db.timesheet

@timesheet.post("/start", response_model=TimeSheetinDB)
def start_timesheet(timesheet: TimesheetEntry, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    timesheet_data = timesheet.dict()
    timesheet_data["_id"] = uuid4.hex()
    timesheet_data["user"] = current_user

    try:
        result = timesheets_collection.insert_one(timesheet_data)
        if result.inserted_id:
            timesheet_data["id"] = timesheet_data.pop("_id")
            return TimeSheetinDB(**timesheet_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Timesheet: {str(e)}")

    raise HTTPException(status_code=500, detail="Timesheet could not be created")

# @timesheet.post("/stop", response_model=TimeSheetinDB)
# def stop_timesheet(time: TimesheetEntry, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
