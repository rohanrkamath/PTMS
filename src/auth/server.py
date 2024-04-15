from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, status, Request
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse

from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import engine, SessionLocal, get_db
from model import Base, TempUser, User
from schema import UserRegistration, TOTPValidation
from crud import create_temp_user, get_temp_user, create_user 

import pyotp
import qrcode
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets

from datetime import datetime, timezone
from io import BytesIO
import os
import time
import base64
import json



# JWT config

JWT_SECRET = "your_jwt_secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from datetime import datetime, timedelta
from jose import jwt

def create_jwt(username: str, secret: str, is_secure: bool):
    # Define token expiration time
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour

    # Create token payload
    payload = {
        "sub": username,  # Subject, usually the username or user id
        "iat": datetime.utcnow(),  # Issued at time
        "exp": expiration,  # Expiration time
    }

    # Encode the payload
    token = jwt.encode(payload, secret, algorithm=ALGORITHM)

    return token


# Basic authentication dependency
security = HTTPBasic()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBasic()

Base.metadata.create_all(bind=engine)

# registration

@app.post('/register/')
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

    response.set_cookie(key="user_email", value=user_data.email, httponly=True, max_age=3600, secure=True, samesite='Lax')
    return StreamingResponse(buf, media_type="image/png")

# totp validation

@app.post('/validate-totp/')
async def validate_totp(totp_details: TOTPValidation, db: Session = Depends(get_db)):

    temp_user = db.query(TempUser).filter(TempUser.email == totp_details.email).first()

    # temp_user = db.query(TempUser).filter(TempUser.email == totp_details.email).order_by(desc(TempUser.created_at)).first()
    if not temp_user:
        raise HTTPException(status_code=400, detail="Please re-register.")

    totp_secret = temp_user.totp_secret
    totp = pyotp.TOTP(totp_secret)

    if not totp.verify(totp_details.totp):
        raise HTTPException(status_code=403, detail="Wrong TOTP entered.")

    new_user = create_user(db, temp_user)
    return {"message": "Registration successful.", "user_id": new_user.employee_id}

# login

@app.post('/login')
async def login(response: Response, credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    username = credentials.username
    password = credentials.password

    user = db.query(User).filter(User.email == username).first()
    if user and pwd_context.verify(password, str(user.hashed_password)):
        # Generate a JWT token
        token = create_jwt(username, JWT_SECRET, True)
        # token = create_jwt(username, JWT_SECRET, True)

        # Set the JWT token as a secure cookie in the response
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, secure=False)

        return {"message": "Login successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.post("/validate")
async def validate(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )

    try:
        # Here you strip the "Bearer " prefix to get the actual token
        token = token.split(" ")[1] if ' ' in token else token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    # Retrieve the user from the database
    user = db.query(User).filter(User.email == decoded['sub']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update the last login time
    user.last_login = datetime.utcnow()
    db.commit()

    return f"{decoded['sub']} has successfully logged in!"




# curent_loggedin_users

# logout

# @app.post('/cookie/')
# async def cookie(response: Response):
#     # For the purpose of testing, we're setting a simple static cookie
#     response.set_cookie(key="test_cookie", value="test_value", httponly=True, samesite='Lax')
#     return {"message": "Check the cookie!"}
