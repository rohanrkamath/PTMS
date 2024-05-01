from fastapi import HTTPException, status, Depends, Request, Security
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
from utils.create_jwt import ALGORITHM, JWT_SECRET
from database import db
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from jose import jwt

roles_collection = db.roles
users_collection = db.users

def require_role(router_name: str):
    async def role_checker(request: Request):
        token = request.cookies.get("access_token")
        if not token:
            print("No token found")
            raise HTTPException(status_code=403, detail="Not authenticated")

        try:
            token = token.split(" ")[1] if ' ' in token else token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        except JWTError as e:
            print(f"JWT decoding error: {str(e)}")
            raise HTTPException(status_code=403, detail="Invalid token or token expired")

        user_id = decoded['sub']
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            print("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        role_info = roles_collection.find_one({"role_name": user.get('role')})
        if not role_info or router_name not in role_info.get('accessible_routers', []):
            print(f"Role check failed. User role: {user.get('role')}, Required router: {router_name}")
            raise HTTPException(status_code=403, detail="Access denied for this user role")

        return user
    return role_checker


# def require_role(router_name: str):
#     async def role_checker(request: Request):
#         token = request.cookies.get("access_token")
#         if not token:
#             raise HTTPException(status_code=403, detail="Not authenticated")

#         try:
#             token = token.split(" ")[1] if ' ' in token else token
#             decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#         except JWTError as e:
#             raise HTTPException(status_code=403, detail="Invalid token or token expired")

#         user_id = decoded['sub']
#         try:
#             ObjectId(user_id) 
#         except:
#             raise HTTPException(status_code=400, detail="Invalid user ID format")

#         user = users_collection.find_one({"_id": ObjectId(user_id)})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         role_info = roles_collection.find_one({"role_name": user.get('role')})
        
#         if not role_info or router_name not in role_info.get('accessible_routers', []):
#             print(role_info)
#             print(router_name) 
#             print(role_info.get('accessible_routers', []))
#             raise HTTPException(status_code=403, detail="Access denied for this user role")

#         return user
#     return role_checker

