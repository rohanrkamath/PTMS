from typing import List
from fastapi import HTTPException
from pymongo.collection import Collection
from bson import ObjectId

from database import db

def validate_project_members(members: List[str], users_collection=db.users):
    # Fetch users' email and role where emails are in the members list
    existing_members_cursor = users_collection.find(
        {"email": {"$in": members}},
        {"email": 1, "role": 1} 
    )

    existing_member_emails = set()
    unassigned_members = []

    for member in existing_members_cursor:
        if member.get('role') == 'unassigned':
            unassigned_members.append(member['email'])
        existing_member_emails.add(member['email'])

    # Identify non-existing members
    non_existing_members = [member for member in members if member not in existing_member_emails]

    # If there are non-existing members or unassigned role members, raise an exception
    if non_existing_members or unassigned_members:
        details = []
        if non_existing_members:
            details.append(f"The following users do not exist: {', '.join(non_existing_members)}")
        if unassigned_members:
            details.append(f"The following users have an unassigned role and cannot be added: {', '.join(unassigned_members)}")
        
        raise HTTPException(status_code=400, detail="; ".join(details))