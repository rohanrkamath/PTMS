from fastapi import FastAPI, APIRouter, HTTPException, Body, Path, Depends, Request, status
from bson.objectid import ObjectId
from bson.errors import InvalidId

from typing import List, Tuple

from schema.project import *
# from utils.jwt_validation import get_current_admin_or_pm, get_current_user
# from utils.memberCheck import validate_project_members 
from utils.project.projectUpdateField import update_project_field
from utils.project.projectMemberUpdate import update_project_members_field
from utils.project.projectValidateMembers import validate_project_members
from utils.dependency_injection.dependency import require_role

from uuid import uuid4
from datetime import datetime
from utils.create_jwt import JWT_SECRET, ALGORITHM
from jose import jwt, JWTError


from database import db, archive

project_prime = APIRouter(
    prefix="/project",
    tags=["projects"],
    dependencies=[Depends(require_role("project_prime_router"))] 
)

project = APIRouter(
    prefix="/project",
    tags=["projects"],
    dependencies=[Depends(require_role("project_router"))]  
)

users_collection = db.users
projects_collection = db.projects
project_archive = archive.projects

# create a project
@project_prime.post("/", response_model=ProjectInDB)
async def create_project(project: ProjectCreate, current_user: dict = Depends(require_role("project_prime_router"))):
    validate_project_members(project.members, users_collection)
    
    project_data = project.dict()
    project_data["project_created"] = datetime.now()
    project_data["updated_at"] = None
    project_data["updated_by"] = None
    project_data["created_by"] = current_user["email"]  
    
    try:
        result = projects_collection.insert_one(project_data)
        if result.inserted_id:
            project_data["id"] = str(result.inserted_id)
            return ProjectInDB(**project_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

    raise HTTPException(status_code=500, detail="Project could not be created")

# get a project
@project.get("/{project_id}", response_model=ProjectInDB)
async def read_project(project_id: str = Path(...)):
    project_data = projects_collection.find_one({"_id": ObjectId(project_id)})
    if project_data:
        project_data["id"] = project_data.pop("_id")
        return ProjectInDB(**project_data)
    raise HTTPException(status_code=404, detail="Project not found")


# -------- update project --------------

# Update project name
@project_prime.patch("/{project_id}/update-name")
async def update_project_name(project_id: str, name_update: NameUpdate, current_user: dict = Depends(require_role("project_prime_router"))):
    return await update_project_field(project_id, "name", name_update.new_name, current_user)

# Update project description
@project_prime.patch("/{project_id}/update-description")
async def update_project_description(project_id: str, description_update: DescriptionUpdate, current_user: dict = Depends(require_role("project_prime_router"))):
    return await update_project_field(project_id, "description", description_update.new_description, current_user)

# Update project start date
@project_prime.patch("/{project_id}/update-start-date")
async def update_project_start_date(project_id: str, date_update: StartDateUpdate, current_user: dict = Depends(require_role("project_prime_router"))):
    return await update_project_field(project_id, "start_date", date_update.new_start_date, current_user)

# Update project end date
@project_prime.patch("/{project_id}/update-end-date")
async def update_project_end_date(project_id: str, date_update: EndDateUpdate, current_user: dict = Depends(require_role("project_prime_router"))):
    return await update_project_field(project_id, "end_date", date_update.new_end_date, current_user)

# Update project members
@project_prime.patch("/{project_id}/update-members")
async def update_project_members(project_id: str, members_update: MembersUpdate, current_user: dict = Depends(require_role("project_prime_router"))):
    # Validate new members to be added
    if members_update.add_members:
        validate_project_members(members_update.add_members, users_collection)
    
    return await update_project_members_field(project_id, members_update, current_user)

# Update project status
@project_prime.patch("/{project_id}/update-status")
async def update_project_status(project_id: str, status_update: StatusUpdate, current_user: dict = Depends(require_role("project_prime_router"))):
    return await update_project_field(project_id, "active", status_update.new_status, current_user)

# ----------- delete project -----------

# delete a project
@project_prime.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(project_id: str = Path(...), current_user: dict = Depends(require_role("project_prime_router"))):
    project_id_obj = ObjectId(project_id)
    existing_project = projects_collection.find_one({"_id": project_id_obj})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing_project['deleted_at'] = datetime.utcnow()
    existing_project['deleted_by'] = current_user['email']

    # Insert into archive before deletion
    archive_result = project_archive.insert_one(existing_project)
    if not archive_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to archive project before deletion")

    # Delete the project from the main collection
    delete_result = projects_collection.delete_one({"_id": project_id_obj})
    if delete_result.deleted_count == 0:
        # Attempt to clean up the archive if the main delete fails
        project_archive.delete_one({"_id": project_id_obj})
        raise HTTPException(status_code=500, detail="Failed to delete project from the main collection")

    # Return a success message
    return {"message": f"Project {project_id} successfully deleted"}


