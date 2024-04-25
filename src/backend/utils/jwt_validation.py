from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
from model.model import User  # Ensure you import your User model correctly
from utils.util import ALGORITHM, JWT_SECRET
from database import get_db 

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )

    try:
        token = token.split(" ")[1] if token.startswith('Bearer ') else token
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

    return user.email


