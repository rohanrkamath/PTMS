from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    email: EmailStr
    employee_id: str
    first_name: str
    last_name: str
    password: str

class TOTPValidation(BaseModel):
    email: EmailStr
    totp: int

# class TOTPValidation(BaseModel):
#     email: EmailStr
#     token: str

# class UserPublic(BaseModel):
#     user_id: str
#     employee_id: str
#     email: EmailStr
#     first_name: str
#     last_name: str

# class UserRegistrationinDB(UserRegistration):

