from fastapi import APIRouter, HTTPException, Path, Body, Depends, Request, status
from sqlalchemy.orm import Session

from schema.epic import *
# from utils.jwt_validation import get_current_user, get_current_admin_or_pm
from utils.memberCheck import validate_project_members, validate_epic_members
from utils.dependency_injection.dependency import require_role
from utils.idCollectionCheck import check_id_exists
from utils.epic_util import update_epic_field, update_validate_epic_members, is_user_member_of_project

from database import db, archive

from uuid import uuid4
from datetime import datetime
from typing import List

from bson import ObjectId

epic_prime = APIRouter(
    prefix="/epic",
    tags=["epics"],
    dependencies=[Depends(require_role(["project_manager", "admin"]))] 
)

epic = APIRouter(
    prefix="/epic",
    tags=["epics"],
    dependencies=[Depends(require_role(["project_manager", "admin", "employee"]))] 
)

users_collection = db.users
projects_collection = db.projects
epics_collection = db.epics
epic_archive = archive.epics

# @epic.post("/test/")
# async def test():


# create an epic
@epic_prime.post("/", response_model=EpicInDB)
async def create_epic(epic_data: EpicCreate, current_user: dict = Depends(require_role(["project_manager", "admin"]))):

    check_id_exists(epic_data.project_id, projects_collection)

    # if not is_user_member_of_project(current_user["email"], epic_data.project_id, projects_collection):
    #     raise HTTPException(status_code=403, detail="Not part of the task.")
    # for members in epic.members:
    #         if not is_user_member_of_project(members, epic_data.project_id, projects_collection):
    #             raise HTTPException(status_code=403, detail="Not part of the task.")

    validate_epic_members(epic_data.project_id, epic_data.members, projects_collection)

    epic_insert_data = epic_data.dict()
    epic_insert_data["epic_created"] = datetime.utcnow()
    epic_insert_data["updated_at"] = None
    epic_insert_data["updated_by"] = None
    epic_insert_data["created_by"] = current_user['email'] 

    try:
        result = epics_collection.insert_one(epic_insert_data)
        if result.inserted_id:
            epic_insert_data["id"] = str(epic_insert_data.pop("_id"))
            return EpicInDB(**epic_insert_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Epic: {str(e)}")

    raise HTTPException(status_code=500, detail="Epic could not be created")

# get an epic
@epic.get("/{epic_id}", response_model=EpicInDB)
async def read_epic(epic_id: str = Path(...)):
    epic_data = epics_collection.find_one({"_id": ObjectId(epic_id)})
    if epic_data:
        epic_data["id"] = epic_data.pop("_id")
        return EpicInDB(**epic_data)
    raise HTTPException(status_code=404, detail="Epic not found")

# Update epic name
@epic_prime.patch("/{epic_id}/update-name")
async def update_epic_name(epic_id: str, name_update: NameUpdate, current_user: dict = Depends(require_role(["project_manager", "admin"]))):
    return await update_epic_field(epic_id, "name", name_update.new_name, current_user)

# Update epic description
@epic_prime.patch("/{epic_id}/update-description")
async def update_epic_description(epic_id: str, description_update: DescriptionUpdate, current_user: dict = Depends(require_role(["project_manager", "admin"]))):
    return await update_epic_field(epic_id, "description", description_update.new_description, current_user)

# Update epic start date
@epic_prime.patch("/{epic_id}/update-start-date")
async def update_epic_start_date(epic_id: str, date_update: StartDateUpdate, current_user: dict = Depends(require_role(["project_manager", "admin"]))):
    return await update_epic_field(epic_id, "start_date", date_update.new_start_date, current_user)

# Update epic end date
@epic_prime.patch("/{epic_id}/update-end-date")
async def update_epic_end_date(epic_id: str, date_update: EndDateUpdate, current_user: dict = Depends(require_role(["project_manager", "admin"]))):
    return await update_epic_field(epic_id, "end_date", date_update.new_end_date, current_user)

# Update epic members
@epic_prime.patch("/{epic_id}/update-members")
async def update_epic_members(epic_id: str, members_update: MembersUpdate, current_user: dict = Depends(require_role(["project_manager", "admin"]))):
    update_validate_epic_members(epic_id, members_update.new_members, projects_collection, epics_collection)

    epic_data = epics_collection.find_one({"_id": ObjectId(epic_id)}, {"members": 1})
    print(epic_data)

    # if not is_user_member_of_project(current_user["email"], epic_data["project_id"], projects_collection):
    #     raise HTTPException(status_code=403, detail="Not part of the project.")
    # for members in epic.members:
    #         if not is_user_member_of_project(members, epic_data["project_id"], projects_collection):
    #             raise HTTPException(status_code=403, detail="Not part of the project.") 
    
    return await update_epic_field(epic_id, "members", members_update.new_members, current_user)

# delete a project
@epic_prime.delete("/{epic_id}", status_code=status.HTTP_200_OK)
async def delete_epic(epic_id: str = Path(...), current_user: dict = Depends(require_role(["project_manager", "admin"]))):

    epic_id_obj = ObjectId(epic_id)
    existing_epic = epics_collection.find_one({"_id": epic_id_obj})
    if not existing_epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    existing_epic['deleted_at'] = datetime.utcnow()
    existing_epic['deleted_by'] = current_user['email']

    archive_result = epic_archive.insert_one(existing_epic)
    if not archive_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to archive epic before deletion")

    delete_result = epics_collection.delete_one({"_id": epic_id_obj})
    if delete_result.deleted_count == 0:
        # Attempt to clean up the archive if the main delete fails
        epic_archive.delete_one({"_id": epic_id_obj})
        raise HTTPException(status_code=500, detail="Failed to delete epic from the main collection")

    # Return a success message
    return {"message": f"Epic {epic_id} successfully deleted"}

