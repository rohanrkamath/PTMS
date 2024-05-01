from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List
from pymongo.errors import PyMongoError
from bson import ObjectId

from schema.timesheet import TimeSheetStatus, TimeSheetStatusUpdate
# from utils.jwt_validation import get_current_user, get_current_admin_or_hr
from utils.dependency_injection.dependency import require_role
# from utils.memberCheck import validate_project_members
# from utils.idCollectionCheck import check_id_exists, check_epic_belongs_to_project
from database import db

timesheet_prime = APIRouter(
    prefix="/timesheet",
    tags=["timesheets"],
    dependencies=[Depends(require_role("timesheet_prime_router"))] 
)

timesheet = APIRouter(
    prefix="/timesheet",
    tags=["timesheets"],
    dependencies=[Depends(require_role("timesheet_router"))]
)

timesheets_collection = db.timesheet

@timesheet.post("/start")
async def start_timesheet(current_user: dict = Depends(require_role("timesheet_router"))):
    #     "start_time": datetime.now(),
    #     "end_time": None,
    #     "status": None,
    #     "user": current_user['email'],
    #     "duration": None
    # }

    print(current_user)

    timesheet_data = {
        "start_time": datetime.now(),
        "status": None,
        "user": current_user["email"]
    }

    try:
        result = timesheets_collection.insert_one(timesheet_data)
        if result.inserted_id:
            return {"message": "Timesheet started", "timesheet_id": str(result.inserted_id)}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    raise HTTPException(status_code=500, detail="Failed to start timesheet")

@timesheet.post("/stop/{timesheet_id}", response_model=dict)
async def stop_timesheet(timesheet_id: str, current_user: dict = Depends(require_role("timesheet_router"))):
    # Existing code for checking active timesheets...

    timesheet = timesheets_collection.find_one({"_id": ObjectId(timesheet_id)})
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    if "end_time" in timesheet and timesheet["end_time"] is not None:
        raise HTTPException(status_code=400, detail="Timesheet already stopped")

    end_time = datetime.now()  # Use datetime.now() directly after correcting the import
    if "start_time" not in timesheet or not timesheet["start_time"]:
        raise HTTPException(status_code=400, detail="Timesheet start time is missing")

    duration = end_time - timesheet["start_time"]
    duration_hours = duration.total_seconds() / 3600  # Convert seconds to hours

    update_data = {
        "end_time": end_time,
        "duration": duration_hours,  # Store duration in hours
        "status": TimeSheetStatus.reviewing.value  # Use the enum value
    }

    try:
        result = timesheets_collection.update_one(
            {"_id": ObjectId(timesheet_id)},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="No changes were made to the timesheet.")

        updated_timesheet = timesheets_collection.find_one({"_id": ObjectId(timesheet_id)})
        if not updated_timesheet:
            raise HTTPException(status_code=404, detail="Failed to retrieve updated timesheet.")
        
        return {"message": "Timesheet stopped", "timesheet_id": str(timesheet_id), "duration_hours": updated_timesheet["duration"]}

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@timesheet_prime.patch("/{timesheet_id}/check", response_model=dict)
async def change_timesheet_status(
    timesheet_id: str = Path(...), status_update: TimeSheetStatusUpdate = Body(...), current_user: dict = Depends(require_role("timesheet_prime_router"))):

    try:
        result = timesheets_collection.update_one(
            {"_id": ObjectId(timesheet_id)},
            {"$set": {
                "status": status_update.status.value, 
                "updated_at": datetime.now(),
                "updated_by": current_user['email'] 
            }}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Timesheet not found or no changes made")

        return {"message": f"Timesheet {timesheet_id} has been checked. Status updated to: {status_update.status.value}"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
'''
TODO
1. add check to at some interval to check if start time hasnt been stopped for a prolonged periods of time, lets say 8hrs
'''


# @timesheet.post("/start", response_model=TimeSheetinDB)
# def start_timesheet(timesheet: TimesheetEntry, current_user = Depends(get_current_user)):
#     timesheet_data = timesheet.dict()
#     timesheet_data["user"] = current_user

#     try:
#         result = timesheets_collection.insert_one(timesheet_data)
#         if result.inserted_id:
#             timesheet_data["id"] = timesheet_data.pop("_id")
#             return TimeSheetinDB(**timesheet_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create Timesheet: {str(e)}")

#     raise HTTPException(status_code=500, detail="Timesheet could not be created")

# @timesheet.post("/stop", response_model=TimeSheetinDB)
# def stop_timesheet(time: TimesheetEntry, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
