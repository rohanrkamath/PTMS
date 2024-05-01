from fastapi import HTTPException, status, Depends, Request, Security
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
from utils.create_jwt import ALGORITHM, JWT_SECRET
from database import db
from bson import ObjectId
from bson.errors import InvalidId
# from schema.user import Role

from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

users_collection = db.users

# # user injection
# def get_current_user(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

#     try:
#         token = token.split(" ")[1] if ' ' in token else token
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#     except JWTError as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e)
#         )

#     user_id = decoded['sub']  # Ensure this is a valid MongoDB ObjectId as a string
#     try:
#         ObjectId(user_id)  # This is to check if user_id is a valid ObjectId
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
    
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     print(user['email'])
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )

#     return user

# # admin injection
# def get_current_admin(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

#     try:
#         token = token.split(" ")[1] if ' ' in token else token
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#     except JWTError as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e)
#         )

#     user_id = decoded['sub']
#     try:
#         ObjectId(user_id)  # Validate user_id is a valid ObjectId
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
    
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )

#     if user.get('role') != 'admin':
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Insufficient permissions"
#         )

#     return user

# # admin and pm injection for project/epic routes
# def get_current_admin_or_pm(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

#     try:
#         token = token.split(" ")[1] if ' ' in token else token
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#     except JWTError as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e)
#         )

#     user_id = decoded['sub']
#     try:
#         ObjectId(user_id) 
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
    
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )

#     if user.get('role') not in [Role.admin.value, Role.project_manager.value]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Insufficient permissions"
#         )

#     return user

# # admin and hr injection for timesheet
# def get_current_admin_or_hr(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

#     try:
#         token = token.split(" ")[1] if ' ' in token else token
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#     except JWTError as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e)
#         )

#     user_id = decoded['sub']
#     try:
#         ObjectId(user_id)  
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
    
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )

#     if user.get('role') not in [Role.admin.value, Role.hr.value]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Insufficient permissions"
#         )

#     return user

# imoprting to other files
def decode_jwt(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return decoded
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
# # def get_current_user(request: Request, token: HTTPAuthorizationCredentials = Depends(security)) -> dict:
# #     try:
# #         decoded = jwt.decode(token.credentials, JWT_SECRET, algorithms=[ALGORITHM])
# #         user_id = decoded['sub']
# #     except JWTError as e:
# #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

# #     user = users_collection.find_one({"_id": ObjectId(user_id)})
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")
    
# #     return user

# # def get_current_user(request: Request):
# #     token = request.cookies.get("access_token")
# #     if not token:
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN,
# #             detail="Not authenticated"
# #         )

# #     try:
# #         token = token.split(" ")[1] if token.startswith('Bearer ') else token
# #         decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
# #     except JWTError as e:
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN,
# #             detail=str(e)
# #         )
    
# #     user = users_collection.find_one({"email": decoded['sub']})
# #     if not user:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="User not found"
# #         )

# #     return user['email']


