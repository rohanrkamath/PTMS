from fastapi import FastAPI, APIRouter, HTTPException, Body, Path, Depends, Request, status, Response
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from bson.errors import InvalidId
from typing import List, Tuple
from pymongo.errors import PyMongoError
from schema.admin import RoleCreation, RouterUpdate, UserRoleUpdate

# from utils.jwt_validation import get_current_admin, get_current_user
from utils.dependency_injection.dependency import require_role
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
    dependencies=[Depends(require_role("admin_router"))]
)

roles_collection = db.roles
users_collection = db.users
users_archive = archive.users_archive

def is_admin(user_id: str):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return user and user['role'] == 'admin'

# admin can add role to user
@admin.patch("/user/{user_id}/role", response_model=dict)
async def assign_role_to_user(user_id: str, role_data: UserRoleUpdate, current_user: dict = Depends(require_role("admin_router"))):
    if not is_admin(current_user['_id']):
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not roles_collection.find_one({"role_name": role_data.role_name}):
        raise HTTPException(status_code=404, detail="Role does not exist")

    try:
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": role_data.role_name}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or role already set to this value")
        return {"message": f"Role '{role_data.role_name}' assigned to user successfully."}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# admin can add roles
@admin.post("/roles/add", response_model=dict)
async def add_role(role_data: RoleCreation, current_user: dict = Depends(require_role("admin_router"))):
    if not is_admin(current_user['_id']):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if roles_collection.find_one({"role_name": role_data.role_name}):
        raise HTTPException(status_code=400, detail="Role already exists")
    
    try:
        result = roles_collection.insert_one({
            "role_name": role_data.role_name,
            "accessible_routers": role_data.accessible_routers
        })
        if result.inserted_id:
            return {"message": f"Role {role_data.role_name} added successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to add role, no ID returned")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# admin can delete roles
@admin.delete("/roles/{role_name}", response_model=dict)
async def delete_role(role_name: str, current_user: dict = Depends(require_role("admin_router"))):
    if not is_admin(current_user['_id']):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    result = roles_collection.delete_one({"role_name": role_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {"message": f"Role {role_name} successfully deleted."}

# add or remove routers from roles
@admin.patch("/roles/{role_name}/routers", response_model=dict)
async def update_role_routers(role_name: str, router_update: RouterUpdate, current_user: dict = Depends(require_role("admin_router"))):
    if not is_admin(current_user['_id']):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    role_doc = roles_collection.find_one({"role_name": role_name})
    if not role_doc:
        raise HTTPException(status_code=404, detail="Role not found")

    updated_routers = set(role_doc.get("accessible_routers", []))
    updated_routers.update(router_update.add_routers)
    updated_routers.difference_update(router_update.remove_routers)
    
    result = roles_collection.update_one(
        {"role_name": role_name},
        {"$set": {"accessible_routers": list(updated_routers)}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="No update performed")
    
    return {"message": f"Accessible routers for role {role_name} updated successfully."}

# when user is logged out and doesnt remember password, can contact admin. will gen random password, and then can send to user
@admin.patch('/update-password/{user_id}', response_model=dict)
async def update_user_password(user_id: str, current_user: dict = Depends(require_role("admin_router"))):
    if not is_admin(current_user['_id']):
        raise HTTPException(status_code=403, detail="Unauthorized")

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
async def delete_user(user_id: str, current_user: dict = Depends(require_role("admin_router"))):
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if str(current_user.get('_id')) != user_id and not is_admin(current_user['_id']):
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





