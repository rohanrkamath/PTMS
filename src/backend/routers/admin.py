from fastapi import FastAPI, APIRouter, HTTPException, Body, Path, Depends, Request, status, Response
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from bson.errors import InvalidId
from typing import List, Tuple

from utils.jwt_validation import get_current_admin
from utils.password import hash_password
from utils.admin_util import generate_random_password
# from schema.admin import PasswordUpdateRequest

from uuid import uuid4
from datetime import datetime
from utils.create_jwt import JWT_SECRET, ALGORITHM

from database import db, archive

admin = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)] 
)

users_collection = db.users
users_archive = archive.users_archive

# when user is logged out and doesnt remember password, can contact admin. will gen random password, and then can send to user
@admin.patch('/update-password/{user_id}', response_model=dict)
async def update_user_password(user_id: str, current_user: dict = Depends(get_current_admin)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can update passwords")

    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Generate a random password
    new_password = generate_random_password()

    # Hash the generated password
    hashed_password = hash_password(new_password)

    update_result = users_collection.update_one(
        {"_id": oid},
        {"$set": {"password": hashed_password}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the plaintext new password so it can be communicated to the user
    return {"message": "Password updated successfully.", "new_password": new_password}

# user deletion

@admin.delete('/delete-user/{user_id}', response_model=dict)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if str(current_user.get('_id')) != user_id and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    user_document = users_collection.find_one({"_id": oid})
    if not user_document:
        raise HTTPException(status_code=404, detail="User not found")

    user_document['deleted_at'] = datetime.utcnow()
    user_document['deleted_by'] = str(current_user['email'])

    users_archive.insert_one(user_document)

    delete_result = users_collection.delete_one({"_id": oid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found despite earlier finding")

    return JSONResponse(content={"message": f"{user_document['email']} deleted successfully"}, status_code=200)





