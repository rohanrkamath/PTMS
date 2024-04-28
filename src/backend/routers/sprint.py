from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from bson import ObjectId
from pymongo.errors import PyMongoError

from database import db, archive
from schema.sprint import SprintCreate, SprintUpdate, SprintInDB
from utils.jwt_validation import get_current_user, get_current_admin_or_pm
from utils.idCollectionCheck import check_id_exists
# from utils.memberCheck import validate_project_members

from uuid import uuid4

sprint = APIRouter(
    prefix="/sprint",
    tags=["sprints"],
    dependencies=[Depends(get_current_admin_or_pm)]
)

user_collection = db.users
project_collection = db.projects
sprints_collection = db.sprints
sprint_archive = archive.sprints

# create a sprint
@sprint.post("/", response_model=SprintInDB)
async def create_sprint(sprint: SprintCreate, current_user: dict = Depends(get_current_admin_or_pm)):
    project = project_collection.find_one({"_id": ObjectId(sprint.project_id)}, {"members": 1})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Prepare sprint data with project members
    sprint_data = sprint.dict()
    sprint_data["members"] = project["members"]  # Include all project members in the sprint
    sprint_data["sprint_created"] = datetime.now()
    sprint_data["updated_at"] = None
    sprint_data["updated_by"] = None
    sprint_data["created_by"] = current_user["email"]

    try:
        result = sprints_collection.insert_one(sprint_data)
        if result.inserted_id:
            sprint_data["id"] = sprint_data.pop("_id")
            return SprintInDB(**sprint_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Sprint: {str(e)}")

    raise HTTPException(status_code=500, detail="Sprint could not be created")


# read sprint
@sprint.get("/{sprint_id}", response_model=SprintInDB)
async def read_sprint(sprint_id: str = Path(...)):
    sprint_data = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    if sprint_data:
        sprint_data["id"] = sprint_data.pop("_id")
        return SprintInDB(**sprint_data)
    raise HTTPException(status_code=404, detail="Sprint not found")

# update a sprint
@sprint.put("/{sprint_id}", response_model=SprintInDB)
async def update_sprint(sprint: SprintUpdate, sprint_id: str = Path(...), current_user: dict = Depends(get_current_admin_or_pm)):
    existing_sprint = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    if not existing_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    update_data = sprint.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user["email"]

    non_editable_fields = {'members', 'sprint_created', 'updated_at', 'updated_by', 'created_by'}
    for field in non_editable_fields:
        update_data.pop(field, None) 

    result = sprints_collection.update_one({"_id": ObjectId(sprint_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_sprint = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
        updated_sprint["id"] = str(updated_sprint.pop("_id"))
        return SprintInDB(**updated_sprint)
    elif result.modified_count == 0 and result.matched_count == 1:
        raise HTTPException(status_code=200, detail="No changes made to the sprint")
    else:
        raise HTTPException(status_code=500, detail="Failed to update sprint")

    raise HTTPException(status_code=500, detail="Sprint could not be updated")

# delete a sprint
@sprint.delete("/{sprint_id}", status_code=200)
async def delete_sprint(sprint_id: str = Path(...)):
    sprint_id_obj = ObjectId(sprint_id)  # Ensure sprint_id is a valid ObjectId
    existing_sprint = sprints_collection.find_one({"_id": sprint_id_obj})
    if not existing_sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Prepare to archive the sprint
    existing_sprint['deleted_at'] = datetime.utcnow()
    existing_sprint['deleted_by'] = "Current user email or identifier"  # Dynamically assigned

    try:
        # Insert the sprint into the archive
        archive_result = sprint_archive.insert_one(existing_sprint)
        if not archive_result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to archive sprint before deletion")

        # If archival is successful, delete the sprint from the main collection
        delete_result = sprints_collection.delete_one({"_id": sprint_id_obj})
        if delete_result.deleted_count == 0:
            # If no document was deleted, possibly roll back the archival if needed
            sprint_archive.delete_one({"_id": sprint_id_obj})
            raise HTTPException(status_code=500, detail="Failed to delete sprint from the main collection")
    
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # If everything went well, return a success message
    return {"message": f"Sprint {sprint_id} successfully deleted and archived"}
