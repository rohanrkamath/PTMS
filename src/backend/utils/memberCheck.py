from typing import List
from model.model import User
from fastapi import HTTPException

def validate_project_members(members: List[str], db_session):
    existing_members = db_session.query(User).filter(User.email.in_(members)).all()
    existing_member_emails = {member.email for member in existing_members}
    non_existing_members = [member for member in members if member not in existing_member_emails]
    if non_existing_members:
        raise HTTPException(status_code=400, detail=f"The following users do not exist: {', '.join(non_existing_members)}")