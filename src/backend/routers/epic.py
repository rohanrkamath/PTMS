from fastapi import APIRouter, HTTPException, Path, Body, Depends, Request
from sqlalchemy.orm import Session

from schema.epic import EpicCreate, EpicUpdate, EpicInDB
from utils.jwt_validation import get_current_user
from utils.memberCheck import validate_project_members
from utils.idCollectionCheck import check_id_exists
from database import db, get_db

from uuid import uuid4
from datetime import datetime
from typing import List
import logging

epic = APIRouter(
    prefix="/project",
    tags=["epics"],
    dependencies=[Depends(get_current_user)]
)

projects_collection = db.projects
epics_collection = db.epics

# @epic.post("/test/")
# async def test():


# create an epic
@epic.post("/epic/", response_model=EpicInDB)
async def create_epic(epic: EpicCreate, created_by: str = Depends(get_current_user), db: Session = Depends(get_db)):

    check_id_exists(epic.project_id, projects_collection)
    validate_project_members(epic.members, db)

    epic_data = epic.dict()
    epic_data["_id"] = uuid4().hex
    epic_data["epic_created"] = datetime.now()
    epic_data["updated_at"] = None
    epic_data["created_by"] = created_by

    try:
        result = epics_collection.insert_one(epic_data)
        if result.inserted_id:
            epic_data["id"] = epic_data.pop("_id")
            return EpicInDB(**epic_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Epic: {str(e)}")

    raise HTTPException(status_code=500, detail="Epic could not be created")

# get an epic
@epic.get("/epic/{epic_id}", response_model=EpicInDB)
async def read_epic(epic_id: str = Path(...)):
    epic_data = epics_collection.find_one({"_id": epic_id})
    if epic_data:
        epic_data["id"] = epic_data.pop("_id")
        return EpicInDB(**epic_data)
    raise HTTPException(status_code=404, detail="Epic not found")

# update an epic
@epic.put("/epic/{epic_id}", response_model=EpicInDB)
async def update_epic(epic: EpicUpdate, epic_id: str = Path(...), db: Session = Depends(get_db)):

    check_id_exists(epic.project_id, projects_collection)
    validate_project_members(epic.members, db)  

    existing_epic = epics_collection.find_one({"_id": epic_id})
    if not existing_epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    update_data = epic.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    
    try:
        result = epics_collection.update_one({"_id": epic_id}, {"$set": update_data})
        if result.modified_count == 1:
            updated_epic = {**existing_epic, **update_data}
            updated_epic["id"] = updated_epic.pop("_id")
            return EpicInDB(**updated_epic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update epic: {str(e)}")

    raise HTTPException(status_code=500, detail="Epic could not be updated")

# delete an epic
@epic.delete("/epic/{epic_id}", response_model=EpicInDB)
async def delete_epic(epic_id: str = Path(..., description="The ID of the epic to delete"), db: Session = Depends(get_db)):

    existing_epic = epics_collection.find_one({"_id": epic_id})
    if not existing_epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    try:
        result = epics_collection.delete_one({"_id": epic_id})
        if result.deleted_count == 1:
            existing_epic["id"] = existing_epic.pop("_id")
            return EpicInDB(**existing_epic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete epic: {str(e)}")

    raise HTTPException(status_code=500, detail="Epic could not be deleted")