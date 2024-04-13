from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session
from database import engine, SessionLocal, get_db
from model import Base, TempUser, User
from schema import UserRegistration, TOTPValidation  # Assuming you've removed 'email' from this schema
from crud import create_temp_user, get_temp_user, create_user, delete_temp_user
import pyotp
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
import time
import base64
import json

app = FastAPI()

Base.metadata.create_all(bind=engine)

from fastapi.responses import JSONResponse


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

@app.post('/validate-totp')
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









# @app.post('/cookie/')
# async def cookie(response: Response):
#     # For the purpose of testing, we're setting a simple static cookie
#     response.set_cookie(key="test_cookie", value="test_value", httponly=True, samesite='Lax')
#     return {"message": "Check the cookie!"}
