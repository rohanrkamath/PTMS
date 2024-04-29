from fastapi import FastAPI, APIRouter, HTTPException, Body, Path, Depends, Request, status, Response
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from bson.errors import InvalidId
from typing import List, Tuple

from schema.user import UserUpdate, UserInDB, Role, FirstNameUpdate, LastNameUpdate, PasswordUpdate, ProfilePicUpdate, PasswordUpdateResponse
# from utils.jwt_validation import get_current_user
from utils.dependency_injection.dependency import require_role
from utils.password import hash_password
from utils.user_crud import update_specific_field
# from utils.memberCheck import validate_project_members 
from uuid import uuid4
from datetime import datetime
from utils.create_jwt import JWT_SECRET, ALGORITHM
from jose import jwt, JWTError

from database import db, archive

user = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(require_role(["project_manager", "admin", "unassigned", "hr", "employee"]))]
)

users_collection = db.users
users_archive = archive.users

# get user details
@user.get('/{user_id}', response_model=UserInDB)
async def read_user(user_id: str, current_user: dict = Depends(require_role(["project_manager", "admin", "unassigned", "hr", "employee"]))):
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # # Check if the current user has the permission to access this user's details
    # if current_user['_id'] != oid and current_user.get('role') != Role.admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user's details")
    
    user_document = users_collection.find_one({"_id": oid})
    if not user_document:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_document

# # update user details
# @user.put('/{user_id}', response_model=UserInDB)
# async def update_user(user_id: str, update_data: UserUpdate, response: Response, current_user: dict = Depends(get_current_user)):
#     try:
#         oid = ObjectId(user_id)
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")

#     # Fetch the current user details from the database
#     existing_user = users_collection.find_one({"_id": oid})
#     if not existing_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     update_data_dict = update_data.dict(exclude_unset=True)
#     user_self_update = str(current_user['_id']) == user_id

#     # Prevent updating non-editable fields
#     non_editable_fields = {'creation_time', 'updated_at', 'updated_by', 'last_login'}
#     for field in non_editable_fields:
#         update_data_dict.pop(field, None)  # Remove the field if it exists in the update dictionary

#     # Check sensitive fields that require special handling or permissions
#     if 'role' in update_data_dict and update_data_dict['role'] != existing_user.get('role') and current_user.get('role') != 'admin':
#         raise HTTPException(status_code=403, detail="Only admins can update user roles")

#     if 'email' in update_data_dict and update_data_dict['email'] != existing_user['email']:
#         raise HTTPException(status_code=403, detail="You cannot update the email after registration, contact admin")
    
#     if 'password' in update_data_dict:
#         new_password = update_data_dict.pop('password')
#         hashed_password = hash_password(new_password)
#         update_data_dict['password'] = hashed_password
#         # Invalidate the token or session if the user is updating their own password
#         response.delete_cookie(key="access_token", path="/", httponly=True, secure=True)
#         # Use JSONResponse to send back a simple message
#         return JSONResponse(content={"message": "Password updated successfully. Please re-login to continue."}, status_code=200)

        
#     if str(current_user['_id']) != user_id and current_user.get('role') != 'admin':
#         raise HTTPException(status_code=403, detail="Not authorized to update this user's details")

#     update_fields = update_data_dict
#     update_fields['updated_at'] = datetime.utcnow()
#     update_fields['updated_by'] = str(current_user['email'])

#     update_result = users_collection.update_one(
#         {"_id": oid},
#         {"$set": update_fields}
#     )

#     if update_result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="User not found")

#     user_document = users_collection.find_one({"_id": oid})
#     user_document['id'] = str(user_document.pop('_id', None))
#     return user_document

@user.patch("/{user_id}/update-first-name", response_model=UserInDB)
async def update_first_name(user_id: str, update_data: FirstNameUpdate, current_user: dict = Depends(require_role(["project_manager", "admin", "unassigned", "hr", "employee"]))):
    return await update_specific_field(user_id, "first_name", update_data.first_name, current_user)

@user.patch("/{user_id}/update-last-name", response_model=UserInDB)
async def update_last_name(user_id: str, update_data: LastNameUpdate, current_user: dict = Depends(require_role(["project_manager", "admin", "unassigned", "hr", "employee"]))):
    return await update_specific_field(user_id, "last_name", update_data.last_name, current_user)

@user.patch("/{user_id}/update-password", response_model=PasswordUpdateResponse)
async def update_password(user_id: str, update_data: PasswordUpdate, response: Response, current_user: dict = Depends(require_role(["project_manager", "admin", "unassigned", "hr", "employee"]))):
    hashed_password = hash_password(update_data.new_password)
    await update_specific_field(user_id, "password", hashed_password, current_user)
    
    response.delete_cookie(key="access_token", path="/", httponly=True, secure=True)
    return {"message": "Password updated successfully. Please re-login to continue."}

@user.patch("/{user_id}/update-profile-pic", response_model=UserInDB)
async def update_profile_pic(user_id: str, update_data:ProfilePicUpdate, current_user: dict = Depends(require_role(["project_manager", "admin", "unassigned", "hr", "employee"]))):
    return await update_specific_field(user_id, "profile_pic", update_data.profile_pic, current_user)

# @user.delete('/{user_id}', status_code=204)
# async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
#     try:
#         oid = ObjectId(user_id)
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")

#     if str(current_user['_id']) != user_id and current_user.get('role') != 'admin':
#         raise HTTPException(status_code=403, detail="Not authorized to delete this user")

#     # Retrieve the user document to be deleted
#     user_document = users_collection.find_one({"_id": oid})
#     if not user_document:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Prepare the document for the archive
#     user_document['deleted_at'] = datetime.utcnow()
#     user_document['deleted_by'] = str(current_user['email'])

#     # Insert the modified user document into the archive collection
#     users_archive.insert_one(user_document)

#     # Delete the user from the primary users collection
#     delete_result = users_collection.delete_one({"_id": oid})
#     if delete_result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="User not found despite earlier finding")

#     return Response(status_code=status.HTTP_204_NO_CONTENT)






