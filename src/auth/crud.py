from sqlalchemy.orm import Session
from model import User, TempUser
from password import hash_password
from datetime import datetime, timezone
from fastapi import HTTPException

def create_temp_user(db: Session, user_details: dict):

    # temp_user_details = {k: user_details[k] for k in ('email', 'totp_secret') if k in user_details}
    hashed_password = hash_password(user_details['password'])
    del user_details['password']
    db_user = TempUser(**user_details, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()

def create_user(db: Session, temp_user: TempUser):
    try:
        new_user = User(
            employee_id=temp_user.employee_id,
            email=temp_user.email,
            hashed_password=temp_user.hashed_password,
            first_name=temp_user.first_name,
            last_name=temp_user.last_name,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_user)
        # db.delete(temp_user)  # cron job
        db.commit()
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to complete registration: {str(e)}")


def get_temp_user(db: Session, email: str):
    return db.query(TempUser).filter(TempUser.email == email).first()

# def delete_temp_user(db: Session, email: str):
#     temp_user = get_temp_user(db, email)
#     if temp_user:
#         db.delete(temp_user)
#         db.commit()
