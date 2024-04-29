from fastapi import APIRouter, HTTPException, Path, Body, Depends, status
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List
from bson import ObjectId


from schema.task import *
from utils.jwt_validation import get_current_user
from utils.memberCheck import validate_project_members
from utils.dependency_injection.dependency import require_role
from utils.idCollectionCheck import check_id_exists, check_epic_belongs_to_project
from utils.subtask_util import is_user_member_of_task
from utils.task_util import *
from database import db, archive

task = APIRouter(
    prefix="/task",
    tags=["tasks"],
    dependencies=[Depends(require_role(["project_manager", "admin", "employee"]))] 
)

users_collections = db.users
projects_collection = db.projects
epics_collection = db.epics
tasks_collection = db.tasks
task_archive = archive.tasks

# create a task
@task.post("/", response_model=TaskInDB)
async def create_task(task: TaskCreate, current_user: dict = Depends(require_role(["project_manager", "admin", "employee"]))):

    check_id_exists(task.project_id, projects_collection) 
    check_id_exists(task.epic_id, epics_collection)
    check_epic_belongs_to_project(task.epic_id, task.project_id, epics_collection)

    # check if current user has permission

    # check if added user in members field are part of epic

    if not is_user_member_of_epic(current_user["email"], task.epic_id, epics_collection):
        raise HTTPException(status_code=403, detail="Current user: Not part of the epic.")
    for members in task.members:
            if not is_user_member_of_epic(members, task.epic_id, epics_collection):
                raise HTTPException(status_code=403, detail="Not part of the epic.")

    validate_task_members(task.epic_id, task.members, epics_collection, tasks_collection)

    task_data = task.dict()
    task_data["task_created"] = datetime.now()
    task_data["updated_at"] = None
    task_data["updated_by"] = None
    task_data["created_by"] = current_user["email"]

    try:
        result = tasks_collection.insert_one(task_data)
        if result.inserted_id:
            task_data["id"] = task_data.pop("_id")
            return TaskInDB(**task_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Task: {str(e)}")

    raise HTTPException(status_code=500, detail="Task could not be created")

# read a task
@task.get("/{task_id}", response_model=TaskInDB)
async def read_task(task_id: str = Path(...)):
    task_data = tasks_collection.find_one({"_id": ObjectId(task_id)})
    if task_data:
        task_data["id"] = task_data.pop("_id")
        return TaskInDB(**task_data)
    raise HTTPException(status_code=404, detail="Task not found")



# update a task
@task.put("/{task_id}", response_model=TaskInDB)
async def update_task(task: TaskUpdate, task_id: str = Path(...), current_user: dict = Depends(require_role(["project_manager", "admin", "employee"]))):
    task_id_obj = ObjectId(task_id)  # Ensure the task_id is correctly converted to ObjectId

    check_id_exists(task.project_id, projects_collection) 
    check_id_exists(task.epic_id, epics_collection)
    check_epic_belongs_to_project(task.epic_id, task.project_id, epics_collection)

    if not is_user_member_of_epic(current_user["email"], task.epic_id, epics_collection):
        raise HTTPException(status_code=403, detail="Not part of the epic.")
    for members in task.members:
            if not is_user_member_of_epic(members, task.epic_id, epics_collection):
                raise HTTPException(status_code=403, detail="Not part of the epic.")
            
    # validate_task_members(task.epic_id, task.members, epics_collection, tasks_collection)

    existing_task = tasks_collection.find_one({"_id": task_id_obj})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user["email"]

    # Prevent updating non-editable fields
    non_editable_fields = {'task_created', 'updated_at', 'updated_by', 'created_by'}
    for field in non_editable_fields:
        update_data.pop(field, None) 

    result = tasks_collection.update_one({"_id": task_id_obj}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="No changes were made to the task.")

    updated_task = tasks_collection.find_one({"_id": task_id_obj})
    if not updated_task:
        raise HTTPException(status_code=404, detail="Failed to retrieve updated task.")

    updated_task["id"] = str(updated_task.pop("_id"))
    return TaskInDB(**updated_task)

@task.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: str = Path(...), current_user: dict = Depends(require_role(["project_manager", "admin", "employee"]))):
    task_id_obj = ObjectId(task_id)  # Convert task_id to ObjectId

    existing_task = tasks_collection.find_one({"_id": task_id_obj})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not is_user_member_of_epic(current_user["email"], existing_task["epic_id"], epics_collection):
        raise HTTPException(status_code=403, detail="Not part of the epic.")

    existing_task['deleted_at'] = datetime.utcnow()
    existing_task['deleted_by'] = current_user['email']  # Assuming 'email' is part of current_user

    archive_result = task_archive.insert_one(existing_task)
    if not archive_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to archive task before deletion")

    delete_result = tasks_collection.delete_one({"_id": task_id_obj})
    if delete_result.deleted_count == 0:
        task_archive.delete_one({"_id": task_id_obj})
        raise HTTPException(status_code=500, detail="Failed to delete task from the main collection")

    # Respond with a success message
    return {"message": f"Task {task_id} successfully deleted and archived"}


