import uuid
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Boolean

from sql_app.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer(), primary_key=True)
    phone_number = Column(String(length=11), nullable=True)
    email = Column(String(length=50), nullable=True)
    email_verified_at = Column(DateTime(), nullable=True)
    phone_verified_at = Column(DateTime(), nullable=True)
    is_active = Column(Boolean(), nullable=False, default=False)
    password = Column(String(length=255), nullable=False)
    date_created = Column(DateTime)
    date_updated = Column(DateTime)
    last_login = Column(DateTime)

    def __init__(self, password, email=None, phone_number=None):
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.is_active = False
        self.date_created = datetime.utcnow()
        self.date_updated = datetime.utcnow()


class EmailActivationRequest(Base):
    __tablename__ = "email_activation_request"
    id = Column(Integer(), primary_key=True)
    token = Column(String(length=50), nullable=False)
    user = Column(Integer(), ForeignKey("user.id"), nullable=False)
    date_created = Column(DateTime(timezone=False))

    def __init__(self, user):
        self.user = user
        self.token = uuid.uuid4().hex
        self.date_created = datetime.utcnow()


class PhoneActivationRequest(Base):
    __tablename__ = "phone_activation_request"
    id = Column(Integer(), primary_key=True)
    otp = Column(Integer(), nullable=False)
    user = Column(Integer(), ForeignKey("user.id"), nullable=False)
    date_created = Column(DateTime(timezone=True))

    def __init__(self, user: int, otp: int):
        self.otp = otp
        self.user = user
        self.date_created = datetime.utcnow()