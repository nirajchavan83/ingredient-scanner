# models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, nullable=False)
    otp_code = Column(String, nullable=True)
    token = Column(String, nullable=True)  # ✅ NEW: store latest access token
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
