from fastapi import HTTPException
from pymongo.collection import Collection
from database import db
from bson import ObjectId

# class Epic:
#     collection = db.epics
#     @staticmethod 
#     def check_id_exists(project_id: str):
#         project = find_one({"_id": project_id})
#         if project is None:
#             raise HTTPException(status_code=404, detail="ID does not exist for either your project, epic or task")
        
# # abstract class


def check_id_exists(project_id: str, db: Collection):

    project = db.find_one({"_id": ObjectId(project_id)})
    if project is None:
        raise HTTPException(status_code=404, detail="ID does not exist for either your project, epic or task")

def check_epic_belongs_to_project(epic_id: str, project_id: str, db: Collection):
    try:
        obj_epic_id = ObjectId(epic_id)
        # obj_project_id = ObjectId(project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")

    # print(f"Checking epic {obj_epic_id} belongs to project {obj_project_id}")

    epic = db.find_one({"_id": obj_epic_id, "project_id": project_id})
    if not epic:
        # print(f"No epic found linking epic ID {obj_epic_id} to project ID {obj_project_id}")
        raise HTTPException(status_code=404, detail="Epic does not belong to the given project")

import logging

def check_task_belongs_to_epic(task_id: str, epic_id: str, db: Collection):
    try:
        obj_task_id = ObjectId(task_id)
        # obj_epic_id = ObjectId(epic_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")

    task = db.find_one({"_id": obj_task_id, "epic_id": epic_id})
    logging.debug(f"Checking task {obj_task_id} for epic {epic_id}, found: {task}")
    if not task:
        raise HTTPException(status_code=404, detail="Task does not belong to the given epic")

# def check_task_belongs_to_epic(task_id: str, epic_id: str, db: Collection):
#     try:
#         obj_task_id = ObjectId(task_id)
#         obj_epic_id = ObjectId(epic_id)  # Ensuring the ID is a valid ObjectId
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")

#     task = db.find_one({"_id": obj_task_id, "epic_id": obj_epic_id})
#     if not task:
#         raise HTTPException(status_code=404, detail="Task does not belong to the given epic")




