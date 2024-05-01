from fastapi import FastAPI, APIRouter, HTTPException, Body, Path, Depends, Request, status, Response
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from bson.errors import InvalidId
from typing import List, Tuple

from schema.user import UserUpdate, UserInDB 
# from utils.jwt_validation import get_current_user
from utils.password import hash_password
# from utils.memberCheck import validate_project_members 
from uuid import uuid4
from datetime import datetime
from utils.create_jwt import JWT_SECRET, ALGORITHM
from jose import jwt, JWTError

from database import db, archive

users_collection = db.users

async def update_specific_field(user_id: str, field_name: str, value: any, current_user: dict):
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if str(current_user['_id']) != user_id and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to update this user's details")

    update_result = users_collection.update_one({"_id": oid}, {"$set": {field_name: value}})

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no update needed (value may be the same)")

    user_document = users_collection.find_one({"_id": oid})
    if not user_document:
        raise HTTPException(status_code=404, detail="User not found after update")

    user_document['id'] = str(user_document.pop('_id', None))
    return user_document
