from fastapi import HTTPException
from bson import ObjectId
from typing import List
from pymongo.collection import Collection
from datetime import datetime

from database import db

tasks_collection = db.tasks

def is_user_member_of_epic(user_email: str, epic_id: str, epics_collection: Collection):
    try:
        epic = epics_collection.find_one({"_id": ObjectId(epic_id)}, {"members": 1})
        print("epic check", user_email,epic.get('members', []))
        if epic and user_email in epic.get('members', []):
            return True
        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking membership: {str(e)}")


async def validate_task_members(task_id: str, proposed_members: List[str], epics_collection: Collection, tasks_collection: Collection):
    # Retrieve the task to get the associated epic ID
    task = tasks_collection.find_one({"_id": ObjectId(task_id)}, {"epic_id": 1})
    if not task or 'epic_id' not in task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Fetch the epic to ensure it exists and retrieve its members
    epic = epics_collection.find_one({"_id": ObjectId(task['epic_id'])}, {"members": 1})
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    epic_members = set(epic.get('members', []))

    # Identify members who are not part of the epic
    non_epic_members = [member for member in proposed_members if member not in epic_members]
    if non_epic_members:
        raise HTTPException(status_code=400, detail=f"The following users are not members of the epic and cannot be added to the task: {', '.join(non_epic_members)}")
