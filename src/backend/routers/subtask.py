from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from database import db, archive 
from uuid import uuid4
from datetime import datetime
from bson import ObjectId

from utils.jwt_validation import get_current_user
from utils.dependency_injection.dependency import require_role
from utils.memberCheck import validate_project_members
from utils.idCollectionCheck import check_id_exists, check_epic_belongs_to_project, check_task_belongs_to_epic
from utils.subtask_util import *
from schema.subtask import SubTaskCreate, SubTaskUpdate, SubTaskInDB
from utils.jwt_validation import get_current_user


subtask = APIRouter(
    prefix="/subtask",
    tags=["subtasks"],
    dependencies=[Depends(require_role(["project_manager", "admin", "employee"]))] 
)

user_collection = db.users
projects_collection = db.projects
epics_collection = db.epics
tasks_collection = db.tasks
subtasks_collection = db.subtasks
subtask_archive = archive.subtasks

import logging

# Create a subtask
@subtask.post("/", response_model=SubTaskInDB)
async def create_subtask(subtask: SubTaskCreate, current_user: dict = Depends(require_role(["project_manager", "admin", "employee"]))):

    try:
        # Standard validations
        check_id_exists(subtask.project_id, projects_collection)
        check_id_exists(subtask.epic_id, epics_collection)
        check_id_exists(subtask.task_id, tasks_collection)

        check_epic_belongs_to_project(subtask.epic_id, subtask.project_id, epics_collection)

        check_task_belongs_to_epic(subtask.task_id, subtask.epic_id, tasks_collection)
        
        if not is_user_member_of_task(current_user["email"], subtask.task_id, tasks_collection):
            raise HTTPException(status_code=403, detail="Not part of the task.")
        for members in subtask.members:
                if not is_user_member_of_task(members, subtask.task_id, tasks_collection):
                    raise HTTPException(status_code=403, detail="Not part of the task.")

        # validate_subtask_members(subtask.task_id, subtask.members, tasks_collection, subtasks_collection)

        subtask_data = subtask.dict()
        subtask_data["subtask_created"] = datetime.utcnow()
        subtask_data["updated_at"] = None
        subtask_data["updated_by"] = None  # Explicitly setting 'updated_by' at creation
        subtask_data["created_by"] = current_user['email']

        result = subtasks_collection.insert_one(subtask_data)
        if result.inserted_id:
            subtask_data["id"] = str(result.inserted_id)
            logging.info(f"Subtask created with ID: {subtask_data['id']}")
            return SubTaskInDB(**subtask_data)
        else:
            raise HTTPException(status_code=500, detail="Failed to insert subtask in database")

    except Exception as e:
        logging.error(f"Failed to create subtask: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create Subtask: {str(e)}")


# Read a subtask
@subtask.get("/{subtask_id}", response_model=SubTaskInDB)
async def read_subtask(subtask_id: str = Path(...)):
    subtask_data = subtasks_collection.find_one({"_id": ObjectId(subtask_id)})
    if subtask_data:
        subtask_data["id"] = subtask_data.pop("_id")
        return SubTaskInDB(**subtask_data)
    raise HTTPException(status_code=404, detail="Subtask not found")

# update a subtask
@subtask.put("/{subtask_id}", response_model=SubTaskInDB)
async def update_subtask(subtask: SubTaskUpdate, subtask_id: str = Path(...), current_user: dict = Depends(require_role(["project_manager", "admin", "employee"]))):

    subtask_id_obj = ObjectId(subtask_id)

    check_id_exists(subtask.project_id, projects_collection)
    check_id_exists(subtask.epic_id, epics_collection)
    check_id_exists(subtask.task_id, tasks_collection)

    check_epic_belongs_to_project(subtask.epic_id, subtask.project_id, epics_collection)

    check_task_belongs_to_epic(subtask.task_id, subtask.epic_id, tasks_collection)

    if not is_user_member_of_task(current_user["email"], subtask.task_id, tasks_collection):
        raise HTTPException(status_code=403, detail="Not part of the task.")
    for members in subtask.members:
            if not is_user_member_of_task(members, subtask.task_id, tasks_collection):
                raise HTTPException(status_code=403, detail="Not part of the task.")

    existing_subtask = subtasks_collection.find_one({"_id": subtask_id_obj})
    if not existing_subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    update_data = subtask.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user["email"] 

    # Prevent updating non-editable fields
    non_editable_fields = {'subtask_created', 'updated_at', 'updated_by', 'created_by'}
    for field in non_editable_fields:
        update_data.pop(field, None) 

    result = subtasks_collection.update_one({"_id": subtask_id_obj}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="No changes were made to the subtask.")

    updated_subtask = subtasks_collection.find_one({"_id": subtask_id_obj})
    if not updated_subtask:
        raise HTTPException(status_code=404, detail="Failed to retrieve updated subtask.")

    updated_subtask["id"] = str(updated_subtask.pop("_id"))
    return SubTaskInDB(**updated_subtask)

# delete a subtask
@subtask.delete("/{subtask_id}", status_code=status.HTTP_200_OK)
async def delete_subtask(subtask_id: str = Path(...), current_user: dict = Depends(require_role(["project_manager", "admin", "employee"]))):
    subtask_id_obj = ObjectId(subtask_id)  # Convert subtask_id to ObjectId

    existing_subtask = subtasks_collection.find_one({"_id": subtask_id_obj})
    if not existing_subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    
    if not is_user_member_of_task(current_user["email"], existing_subtask["task_id"], tasks_collection):
        raise HTTPException(status_code=403, detail="Not part of the task.")

    existing_subtask['deleted_at'] = datetime.utcnow()
    existing_subtask['deleted_by'] = current_user['email']  # Assuming 'email' is part of current_user

    archive_result = subtask_archive.insert_one(existing_subtask)
    if not archive_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to archive subtask before deletion")

    delete_result = subtasks_collection.delete_one({"_id": subtask_id_obj})
    if delete_result.deleted_count == 0:
        subtask_archive.delete_one({"_id": subtask_id_obj})
        raise HTTPException(status_code=500, detail="Failed to delete subtask from the main collection")

    # Respond with a success message
    return {"message": f"Subtask {subtask_id} successfully deleted and archived"}