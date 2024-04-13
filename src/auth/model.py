from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from uuid import uuid4
from datetime import datetime, timezone

from database import Base

# Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    employee_id = Column(String, primary_key=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    # phone_no = Column(Integer, unique=True, nullable=True)
    # profile_pic = Column(String, nullable=True)
    # role = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class TempUser(Base):
    __tablename__ = 'temporary_users'
    employee_id = Column(String, primary_key=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    totp_secret = Column(String, nullable=True)
    # created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
