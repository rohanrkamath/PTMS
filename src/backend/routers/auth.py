from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, status, Request, APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials

from database import db
from schema.user import UserBase, UserInDB, TOTPValidation
from utils.crud.auth_crud import check_user_exists, create_temp_user, get_temp_user_by_email, create_user, delete_temp_user
from utils.create_jwt import create_jwt, JWT_SECRET, ALGORITHM
from utils.password import hash_password, verify_password
from utils.jwt_validation import decode_jwt

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING
from pymongo.errors import DuplicateKeyError
import pyotp
import qrcode
from jose import jwt, JWTError
from passlib.context import CryptContext

from datetime import datetime, timedelta
from io import BytesIO

# Basic authentication dependency
security = HTTPBasic()

auth = APIRouter(
    tags = ["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBasic()

temp_users_collection = db.temp_users
users_collection = db.users

# registration
@auth.post('/register')
async def register(user_data: UserBase):
    if check_user_exists(users_collection, user_data.email) or check_user_exists(temp_users_collection, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered or pending registration.")
    
    hashed_password = hash_password(user_data.password)
    user_data.password = hashed_password 

    totp_secret = pyotp.random_base32()
    uri = pyotp.TOTP(totp_secret).provisioning_uri(name=user_data.email, issuer_name="YourAppName")
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    temp_user_details = user_data.dict()
    temp_user_details['totp_secret'] = totp_secret
    temp_user_details['role'] = "unassigned"

    create_temp_user(temp_users_collection, temp_user_details)

    return StreamingResponse(buf, media_type="image/png")

# topt validation

@auth.post('/validate-totp/')
async def validate_totp(totp_details: TOTPValidation):
    temp_user = get_temp_user_by_email(temp_users_collection, totp_details.email)
    if not temp_user:
        raise HTTPException(status_code=400, detail="Please re-register, your 5 minutes to register has expired.")

    totp_secret = temp_user['totp_secret']
    totp = pyotp.TOTP(totp_secret)
    if totp.verify(totp_details.totp):
        try:
            user_data = UserInDB(**temp_user, creation_time=datetime.now(), updated_at=None, last_login=None)
            create_user(users_collection, user_data.dict(exclude_unset=True))
            delete_temp_user(temp_users_collection, totp_details.email)
            return {"message": "Registration successful.", "user_email": user_data.email}
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="Email already exists in the system.")
    else:
        raise HTTPException(status_code=403, detail="Wrong TOTP entered.")

# login

@auth.post('/login')
async def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password

    user = users_collection.find_one({"email": username})
    if user and verify_password(password, user['password']):
        role = user.get('role', 'unassigned')  
        token = create_jwt(str(user['_id']), JWT_SECRET, role, True)
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=False)

        users_collection.update_one(
            {"_id": user['_id']},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return {"message": "Login successful", "user_email": user['email'], "role": role}
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

# @auth.post('/login')
# async def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     password = credentials.password

#     user = users_collection.find_one({"email": username})
#     if user and verify_password(password, user['password']):
#         # Create JWT token with the user's role
#         token = create_jwt(str(user['_id']), JWT_SECRET, user.get('role', 'user'), True)
#         response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=False)

#         users_collection.update_one(
#             {"_id": user['_id']},
#             {"$set": {"last_login": datetime.utcnow()}}
#         )
        
#         return {"message": "Login successful", "user_email": user['email']}
#     else:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )
    
# get current logged in user
@auth.get('/get_current_user')
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return {'message': 'No user is logged in.'}

    token = token.split(" ")[1] if 'Bearer ' in token else token

    try:
        decoded = decode_jwt(token)
    except HTTPException as e:
        return {"message": str(e.detail)}

    try:
        user_id = ObjectId(decoded['sub'])  # Convert the sub to ObjectId
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User currently logged in: {user['email']}"}

# logout

@auth.post('/logout')
async def logout(request: Request, response: Response):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session found"
        )

    token = token.split(" ")[1] if 'Bearer ' in token else token

    try:
        decoded = decode_jwt(token)
        user_id = ObjectId(decoded['sub'])
    except (HTTPException, InvalidId):
        response.delete_cookie(key="access_token", path="/", httponly=True, secure=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token - Logging out anyway"
        )

    # Fetch the user from the database to retrieve the email
    user = users_collection.find_one({"_id": user_id})
    if not user:
        response.delete_cookie(key="access_token", path="/", httponly=True, secure=True)
        raise HTTPException(status_code=404, detail="User not found - Logging out anyway")

    user_email = user['email']
    response.delete_cookie(key="access_token", path="/", httponly=True, secure=True)
    return {'message': f'Successfully logged out: {user_email}'}

# check cookie
# task collection


