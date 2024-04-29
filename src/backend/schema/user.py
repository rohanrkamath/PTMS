from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional 
from datetime import datetime
from uuid import uuid4
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    hr = "hr"
    project_manager = "project manager"
    employee = "employee"

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    profile_pic: Optional[str]

class UserUpdate(UserBase):
    pass

class UserInDB(UserBase):
    role: Optional[str] = "unassigned"
    creation_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    last_login: Optional[datetime] = None

class TOTPValidation(BaseModel):
    email: EmailStr
    totp: int

# -----------------

class FirstNameUpdate(BaseModel):
    first_name: str

class LastNameUpdate(BaseModel):
    last_name: str

class PasswordUpdate(BaseModel):
    new_password: str

class PasswordUpdateResponse(BaseModel):
    message: str

class ProfilePicUpdate(BaseModel):
    profile_pic: str



