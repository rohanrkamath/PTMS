from fastapi import HTTPException
from bson.objectid import ObjectId
from database import db, archive
from pymongo.collection import Collection

from typing import List

from datetime import datetime

from schema.epic import EpicInDB

projects_collection = db.projects
epics_collection = db.epics

def is_user_member_of_project(user_email: str, project_id: str, project_collection: Collection):
    try:
        # Ensure the task_id is a valid ObjectId
        project_obj_id = ObjectId(project_id)
        project = project_collection.find_one({"_id": project_obj_id}, {"members": 1})
        print(user_email, project["members"])
        if not project:
            # logging.warning(f"No task found with ID: {task_id}")
            raise HTTPException(status_code=404, detail="Porject not found")
        
        # print(user_email, task.get('members', []))

        # Check if the user's email is in the task's members list
        if user_email in project.get('members', []):
            # logging.info(f"User {user_email} is a member of task {task_id}")
            return True
        
        # logging.warning(f"User {user_email} is not a member of task {task_id}")
        return False
    
    except Exception as e:
        # logging.error(f"Error checking membership for user {user_email} in task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking membership: {str(e)}")

async def update_epic_field(epic_id: str, field_name: str, new_value, current_user: dict):
    epic_id_obj = ObjectId(epic_id)
    update_result = epics_collection.update_one(
        {"_id": epic_id_obj},
        {"$set": {field_name: new_value, "updated_at": datetime.utcnow(), "updated_by": current_user['email']}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Epic not found or no changes made")

    updated_epic = epics_collection.find_one({"_id": epic_id_obj})
    if not updated_epic:
        raise HTTPException(status_code=404, detail="Epic not found after update")
    
    updated_epic["id"] = str(updated_epic.pop("_id"))
    return updated_epic

async def update_validate_epic_members(epic_id: str, proposed_members: List[str], projects_collection: Collection, epics_collection: Collection):
    # Retrieve the epic to get the associated project ID
    epic = epics_collection.find_one({"_id": ObjectId(epic_id)}, {"project_id": 1})
    if not epic or 'project_id' not in epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    # Fetch the project to ensure it exists and retrieve its members
    project = projects_collection.find_one({"_id": ObjectId(epic['project_id'])}, {"members": 1})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_members = set(project.get('members', []))

    # Identify members who are not part of the project
    non_project_members = [member for member in proposed_members if member not in project_members]
    if non_project_members:
        raise HTTPException(status_code=400, detail=f"The following users are not members of the project and cannot be added to the epic: {', '.join(non_project_members)}")
    
