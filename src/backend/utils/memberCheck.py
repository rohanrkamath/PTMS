from typing import List
from fastapi import HTTPException
from pymongo.collection import Collection
from bson import ObjectId

from database import db

def validate_project_members(members: List[str], users_collection=db.users):
    existing_members_cursor = users_collection.find({"email": {"$in": members}}, {"email": 1})
    existing_member_emails = {member['email'] for member in existing_members_cursor}

    non_existing_members = [member for member in members if member not in existing_member_emails]

    if non_existing_members:
        raise HTTPException(status_code=400, detail=f"The following users do not exist: {', '.join(non_existing_members)}")

def validate_epic_members(project_id: str, proposed_members: List[str], projects_collection: Collection):
    # Fetch the project to ensure it exists and retrieve its members
    project = projects_collection.find_one({"_id": ObjectId(project_id)}, {"members": 1})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_members = set(project['members'])

    non_project_members = [member for member in proposed_members if member not in project_members]
    if non_project_members:
        raise HTTPException(status_code=400, detail=f"The following users are not members of the project and cannot be added to the epic: {', '.join(non_project_members)}")

