from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, status, Request, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import engine, SessionLocal, get_db
from model.model import Base, TempUser, User
from schema.schema import UserRegistration, TOTPValidation
from utils.crud import create_temp_user, get_temp_user, create_user 
from utils.util import JWT_SECRET, ALGORITHM, pwd_context, create_jwt

import pyotp
import qrcode
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets

from datetime import datetime, timedelta
from io import BytesIO
import os
import time
import base64
import json

# Basic authentication dependency
security = HTTPBasic()

router = APIRouter()

# # Middleware for error handling
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
 
 
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.detail},
#     )
 
 
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc: RequestValidationError):
#     result = list(
#         map(
#             lambda error: {"message": error["msg"], "field": error["loc"][1]},
#             exc.args[0],
#         )
#     )
#     return JSONResponse(status_code=422, content=result)
 
 
# @app.exception_handler(Exception)
# async def validation_exception_handler(request, exc):
#     print(exc)
#     return JSONResponse(status_code=500, content={"message": "Internal Server Error"})



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBasic()

Base.metadata.create_all(bind=engine)

# registration
@router.post('/register/')
async def register(user_data: UserRegistration, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    totp_secret = pyotp.random_base32()
    uri = pyotp.TOTP(totp_secret).provisioning_uri(name=user_data.email, issuer_name="YourAppName")
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    temp_user_details = user_data.dict()
    temp_user_details['totp_secret'] = totp_secret
    create_temp_user(db, temp_user_details)

    return StreamingResponse(buf, media_type="image/png")

# totp validation

@router.post('/validate-totp/')
async def validate_totp(totp_details: TOTPValidation, db: Session = Depends(get_db)):

    temp_user = db.query(TempUser).filter(TempUser.email == totp_details.email).first()

    if not temp_user:
        raise HTTPException(status_code=400, detail="Please re-register.")

    totp_secret = temp_user.totp_secret
    totp = pyotp.TOTP(totp_secret)

    if not totp.verify(totp_details.totp):
        raise HTTPException(status_code=403, detail="Wrong TOTP entered.")

    new_user = create_user(db, temp_user)
    return {"message": "Registration successful.", "user_id": new_user.employee_id}

# login

@router.post('/login')
async def login(response: Response, credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    username = credentials.username
    password = credentials.password

    user = db.query(User).filter(User.email == username).first()
    if user and pwd_context.verify(password, str(user.hashed_password)):
        token = create_jwt(username, JWT_SECRET, True)
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=False)

        return {"message": "Login successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
# not required; add middleware to routes that need access token
# JWT cookie validation route
@router.post("/validate")
async def validate(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authenticated"
        )

    try:
        token = token.split(" ")[1] if ' ' in token else token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    user = db.query(User).filter(User.email == decoded['sub']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.last_login = datetime.utcnow()
    db.commit()

    return f"{decoded['sub']} has successfully logged in!"

# curent_logged_in_users
@router.get('/get_current_user')
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return {'message': 'No user is logged in.'}
    
    try:
        token = token.split(" ")[1] if ' ' in token else token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    user = db.query(User).filter(User.email == decoded['sub']).first()
    if not user:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
 
    return f"User currently logged in: {decoded['sub']}"

# logout

@router.post('/logout')
async def logout(request: Request, response: Response):
    if "access_token" not in request.cookies:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session found"
        )

    response.delete_cookie(key="access_token", path="/", httponly=True, secure=False)
    # return Response(status_code=status.HTTP_204_NO_CONTENT, content="Logged out successfully")
    return {'message': 'Successfully logged out'}



