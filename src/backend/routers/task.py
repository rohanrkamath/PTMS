from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List

from schema.task import TaskCreate, TaskUpdate, TaskInDB  
from utils.jwt_validation import get_current_user
from utils.memberCheck import validate_project_members
from utils.idCollectionCheck import check_id_exists, check_epic_belongs_to_project
from database import db, get_db

task = APIRouter(
    # prefix="/project/epic",
    tags=["tasks"],
    dependencies=[Depends(get_current_user)]
)

projects_collection = db.projects
epics_collection = db.epics
tasks_collection = db.tasks

# create a task
@task.post("/task/", response_model=TaskInDB)
async def create_task(task: TaskCreate, created_by: str = Depends(get_current_user), db: Session = Depends(get_db)):

    check_id_exists(task.project_id, projects_collection) 
    check_id_exists(task.epic_id, epics_collection)
    check_epic_belongs_to_project(task.epic_id, task.project_id, epics_collection)
    validate_project_members(task.members, db)

    task_data = task.dict()
    task_data["_id"] = uuid4().hex
    task_data["task_created"] = datetime.now()
    task_data["updated_at"] = None
    task_data["created_by"] = created_by

    try:
        result = tasks_collection.insert_one(task_data)
        if result.inserted_id:
            task_data["id"] = task_data.pop("_id")
            return TaskInDB(**task_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Task: {str(e)}")

    raise HTTPException(status_code=500, detail="Task could not be created")

# read a task
@task.get("/task/{task_id}", response_model=TaskInDB)
async def read_task(task_id: str = Path(...)):
    task_data = tasks_collection.find_one({"_id": task_id})
    if task_data:
        task_data["id"] = task_data.pop("_id")
        return TaskInDB(**task_data)
    raise HTTPException(status_code=404, detail="Task not found")

# update a task
@task.put("/task/{task_id}", response_model=TaskInDB)
async def update_task(task: TaskUpdate, task_id: str = Path(...), db: Session = Depends(get_db)):

    check_id_exists(task.project_id, projects_collection) 
    check_id_exists(task.epic_id, epics_collection)
    check_epic_belongs_to_project(task.epic_id, task.project_id, epics_collection)
    validate_project_members(task.members, db)

    existing_task = tasks_collection.find_one({"_id": task_id})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()

    try:
        result = tasks_collection.update_one({"_id": task_id}, {"$set": update_data})
        if result.modified_count == 1:
            updated_task = {**existing_task, **update_data}
            updated_task["id"] = updated_task.pop("_id")
            return TaskInDB(**updated_task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update Task: {str(e)}")

    raise HTTPException(status_code=500, detail="Task could not be updated")

# delete a task
@task.delete("/task/{task_id}", response_model=TaskInDB)
async def delete_task(task_id: str = Path(...), db: Session = Depends(get_db)):

    existing_task = tasks_collection.find_one({"_id": task_id})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        result = tasks_collection.delete_one({"_id": task_id})
        if result.deleted_count == 1:
            existing_task["id"] = existing_task.pop("_id")
            return TaskInDB(**existing_task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete Task: {str(e)}")

    raise HTTPException(status_code=500, detail="Task could not be deleted")


