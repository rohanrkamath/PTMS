# from fastapi import APIRouter, HTTPException, Path, Depends
# from sqlalchemy.orm import Session
# from database import db, get_db
# from uuid import uuid4
# from datetime import datetime

# from utils.jwt_validation import get_current_user
# from utils.memberCheck import validate_project_members
# from utils.idCollectionCheck import check_id_exists, check_epic_belongs_to_project, check_task_belongs_to_epic
# from schema.subtask import SubTaskCreate, SubTaskUpdate, SubTaskInDB
# from utils.jwt_validation import get_current_user


# subtask = APIRouter(
#     # prefix="/project/epic/task/subtask",
#     tags=["subtasks"],
#     dependencies=[Depends(get_current_user)]
# )

# projects_collection = db.projects
# epics_collection = db.epics
# tasks_collection = db.tasks
# subtasks_collection = db.subtasks

# # Create a subtask
# @subtask.post("/subtask", response_model=SubTaskInDB)
# async def create_subtask(subtask: SubTaskCreate, created_by: str = Depends(get_current_user), db: Session = Depends(get_db)):

#     check_id_exists(subtask.project_id, projects_collection)
#     check_id_exists(subtask.epic_id, epics_collection)
#     check_id_exists(subtask.task_id, tasks_collection)
#     check_epic_belongs_to_project(subtask.epic_id, subtask.project_id, epics_collection)
#     check_task_belongs_to_epic (subtask.task_id, subtask.epic_id, tasks_collection)
#     validate_project_members(subtask.members, db)

#     subtask_data = subtask.dict()
#     subtask_data["_id"] = uuid4().hex
#     subtask_data["subtask_created"] = datetime.now()
#     subtask_data["updated_at"] = None
#     subtask_data["created_by"] = created_by

#     try:
#         result = subtasks_collection.insert_one(subtask_data)
#         if result.inserted_id:
#             subtask_data["id"] = subtask_data.pop("_id")
#             return SubTaskInDB(**subtask_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create Subtask: {str(e)}")

#     raise HTTPException(status_code=500, detail="Subtask could not be created")

# # Read a subtask
# @subtask.get("/subtask/{subtask_id}", response_model=SubTaskInDB)
# async def read_subtask(subtask_id: str = Path(...)):
#     subtask_data = subtasks_collection.find_one({"_id": subtask_id})
#     if subtask_data:
#         subtask_data["id"] = subtask_data.pop("_id")
#         return SubTaskInDB(**subtask_data)
#     raise HTTPException(status_code=404, detail="Subtask not found")

# # update a subtask
# @subtask.put("/subtask/{subtask_id}", response_model=SubTaskInDB)
# async def update_subtask(subtask: SubTaskUpdate, subtask_id: str = Path(...), db: Session = Depends(get_db)):

#     check_id_exists(subtask.project_id, projects_collection)
#     check_id_exists(subtask.epic_id, epics_collection)
#     check_id_exists(subtask.task_id, tasks_collection)
#     check_epic_belongs_to_project(subtask.epic_id, subtask.project_id, epics_collection)
#     check_task_belongs_to_epic (subtask.task_id, subtask.epic_id, tasks_collection)
#     validate_project_members(subtask.members, db)

#     existing_subtask = subtasks_collection.find_one({"_id": subtask_id})
#     if not existing_subtask:
#         raise HTTPException(status_code=404, detail="Subtask not found")

#     update_data = subtask.dict(exclude_unset=True)
#     update_data["updated_at"] = datetime.now()

#     try:
#         result = subtasks_collection.update_one({"_id": subtask_id}, {"$set": update_data})
#         if result.modified_count == 1:
#             updated_subtask = {**existing_subtask, **update_data}
#             updated_subtask["id"] = updated_subtask.pop("_id")
#             return SubTaskInDB(**updated_subtask)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update subtask: {str(e)}")

#     raise HTTPException(status_code=500, detail="Subtask could not be updated")

# # delete a subtask
# @subtask.delete("/subtask/{subtask_id}", response_model=SubTaskInDB)
# async def delete_subtask(subtask_id: str = Path(...), db: Session = Depends(get_db)):

#     existing_subtask = subtasks_collection.find_one({"_id": subtask_id})
#     if not existing_subtask:
#         raise HTTPException(status_code=404, detail="Subtask not found")

#     try:
#         result = subtasks_collection.delete_one({"_id": subtask_id})
#         if result.deleted_count == 1:
#             existing_subtask["id"] = existing_subtask.pop("_id")
#             return SubTaskInDB(**existing_subtask)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete subtask: {str(e)}")

#     raise HTTPException(status_code=500, detail="Subtask could not be deleted")