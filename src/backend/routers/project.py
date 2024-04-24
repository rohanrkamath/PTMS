from fastapi import FastAPI, APIRouter, HTTPException, Body, Path, Depends, Request
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from sqlalchemy.orm import Session
from database import engine, SessionLocal, get_db
from typing import List, Tuple

from schema.project import ProjectBase, ProjectCreate, ProjectUpdate, ProjectInDB
from utils.jwt_validation import get_current_user
from utils.memberCheck import validate_project_members 
from uuid import uuid4
from datetime import datetime
from utils.util import JWT_SECRET, ALGORITHM
from jose import jwt, JWTError
from model.model import User


from database import db

project = APIRouter(
    # prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)]  # Ensure every route in this router requires authentication
)

projects_collection = db.projects

# def validate_project_members(members: List[str], db_session):
#     existing_members = db_session.query(User).filter(User.email.in_(members)).all()
#     existing_member_emails = {member.email for member in existing_members}
#     non_existing_members = [member for member in members if member not in existing_member_emails]
#     if non_existing_members:
#         raise HTTPException(status_code=400, detail=f"The following users do not exist: {', '.join(non_existing_members)}")

# create a project
@project.post("/projects/", response_model=ProjectInDB)
async def create_project(project: ProjectCreate, created_by: str = Depends(get_current_user), db: Session = Depends(get_db)):

    validate_project_members(project.members, db)

    project_data = project.dict()
    project_data["_id"] = uuid4().hex
    project_data["project_created"] = datetime.now()
    project_data["updated_at"] = None
    project_data["created_by"] = created_by  
    
    try:
        result = projects_collection.insert_one(project_data)
        if result.inserted_id:
            project_data["id"] = project_data.pop("_id")
            return ProjectInDB(**project_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

    raise HTTPException(status_code=500, detail="Project could not be created")

# get a project
@project.get("/projects/{project_id}", response_model=ProjectInDB)
async def read_project(project_id: str = Path(..., description="The ID of the project to retrieve")):
    project_data = projects_collection.find_one({"_id": project_id})
    if project_data:
        project_data["id"] = project_data.pop("_id")
        return ProjectInDB(**project_data)
    raise HTTPException(status_code=404, detail="Project not found")

#update a project
@project.put("/projects/{project_id}", response_model=ProjectInDB)
async def update_project(project: ProjectUpdate, project_id: str = Path(...), db: Session = Depends(get_db)):

    validate_project_members(project.members, db)

    existing_project = projects_collection.find_one({"_id": project_id})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    
    try:
        result = projects_collection.update_one({"_id": project_id}, {"$set": update_data})
        if result.modified_count == 1:
            updated_project = {**existing_project, **update_data}
            updated_project["id"] = updated_project.pop("_id")
            return ProjectInDB(**updated_project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

    raise HTTPException(status_code=500, detail="Project could not be updated")

# delete a project
@project.delete("/projects/{project_id}", response_model=ProjectInDB)
async def delete_project(project_id: str = Path(...), db: Session = Depends(get_db)):

    existing_project = projects_collection.find_one({"_id": project_id})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = projects_collection.delete_one({"_id": project_id})
        if result.deleted_count == 1:
            existing_project["id"] = existing_project.pop("_id")
            return ProjectInDB(**existing_project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

    raise HTTPException(status_code=500, detail="Project could not be deleted")

