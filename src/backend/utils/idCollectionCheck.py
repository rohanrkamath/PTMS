from fastapi import HTTPException
from pymongo.collection import Collection
from database import db

# class Epic:
#     collection = db.epics
#     @staticmethod 
#     def check_id_exists(project_id: str):
#         project = find_one({"_id": project_id})
#         if project is None:
#             raise HTTPException(status_code=404, detail="ID does not exist for either your project, epic or task")
        
# # abstract class


def check_id_exists(project_id: str, db: Collection):

    project = db.find_one({"_id": project_id})
    if project is None:
        raise HTTPException(status_code=404, detail="ID does not exist for either your project, epic or task")
    
def check_epic_belongs_to_project(epic_id: str, project_id: str, db: Collection):
    
    epic = db.find_one({"_id": epic_id, "project_id": project_id})
    if not epic:
        raise HTTPException(status_code=404, detail="Epic does not belong to the given project")
    
def check_task_belongs_to_epic(task_id: str, epic_id: str, db: Collection):
    
    task = db.find_one({"_id": task_id, "epic_id": epic_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task does not belong to the given epic")



