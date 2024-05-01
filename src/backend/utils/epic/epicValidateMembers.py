from fastapi import HTTPException
from typing import List
from bson import ObjectId
from database import db

users_collection = db.users
projects_collection = db.projects

def validate_epic_members(epic_id: str, members: List[str], users_collection=db.users, epics_collection=db.epics):
    # First, verify each member exists in the users collection
    existing_users_cursor = users_collection.find(
        {"email": {"$in": members}},
        {"email": 1}
    )
    existing_user_emails = {user['email'] for user in existing_users_cursor}
    
    # Check for non-existent users
    non_existent_members = [member for member in members if member not in existing_user_emails]
    if non_existent_members:
        raise HTTPException(status_code=400, detail=f"The following users do not exist: {', '.join(non_existent_members)}")

    # Check if the epic exists and fetch its associated project ID
    epic = epics_collection.find_one({"_id": ObjectId(epic_id)}, {"project_id": 1})
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    # Fetch the project to check if the members are part of the project
    project_id = epic['project_id']
    project_members_cursor = projects_collection.find_one({"_id": ObjectId(project_id)}, {"members": 1})
    if not project_members_cursor:
        raise HTTPException(status_code=404, detail="Associated project not found")

    # Validate members are part of the project
    valid_members = set(project_members_cursor.get('members', []))
    invalid_members = [member for member in members if member not in valid_members]
    if invalid_members:
        raise HTTPException(status_code=400, detail=f"The following users are not members of the project and cannot be added to the epic: {', '.join(invalid_members)}")


# def validate_epic_members(epic_id: str, members: List[str], users_collection=db.users, epics_collection=db.epics):
#     epic = epics_collection.find_one({"_id": ObjectId(epic_id)}, {"project_id": 1})
#     if not epic:
#         raise HTTPException(status_code=404, detail="Epic not found")

#     # Fetch the project to check if the members are part of the project
#     project_id = epic['project_id']
#     project_members_cursor = projects_collection.find_one({"_id": ObjectId(project_id)}, {"members": 1})
#     if not project_members_cursor:
#         raise HTTPException(status_code=404, detail="Associated project not found")

#     valid_members = set(project_members_cursor.get('members', []))
#     invalid_members = [member for member in members if member not in valid_members]
#     if invalid_members:
#         raise HTTPException(status_code=400, detail=f"The following users are not members of the project and cannot be added to the epic: {', '.join(invalid_members)}")
