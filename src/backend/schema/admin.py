from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from pymongo import MongoClient, errors as pymongo_errors
from bson import ObjectId

# Define the Pydantic model for the request body
class RoleCreation(BaseModel):
    role_name: str
    accessible_routers: List[str] = Field(default=[])

class RouterUpdate(BaseModel):
    add_routers: Optional[List[str]] = Field(default=[])
    remove_routers: Optional[List[str]] = Field(default=[])

class UserRoleUpdate(BaseModel):
    role_name: str