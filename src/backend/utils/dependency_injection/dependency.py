from fastapi import HTTPException, status, Depends, Request, Security
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
from utils.create_jwt import ALGORITHM, JWT_SECRET
from database import db
from bson import ObjectId
from bson.errors import InvalidId
from schema.user import Role
from typing import List

from jose import jwt

users_collection = db.users

def require_role(allowed_roles: List[str]):
    async def role_checker(request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=403, detail="Not authenticated")

        try:
            token = token.split(" ")[1] if ' ' in token else token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        except JWTError as e:
            raise HTTPException(status_code=403, detail="Invalid token or token expired")

        user_id = decoded['sub']
        try:
            ObjectId(user_id) 
        except:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied for this user role")

        return user 
    return role_checker

