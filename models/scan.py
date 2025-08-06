# models/scan.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ✅ Link to user

    image_path = Column(String, nullable=True)               # optional: if image was uploaded
    ingredients_text = Column(Text, nullable=True)           # raw or OCRed text
    result_json = Column(Text, nullable=True)                # classified ingredient list as JSON string
    recommendation = Column(String, nullable=True)           # e.g. "⚠ Consume in Moderation"
    health_score = Column(Integer, nullable=True)            # 0–10
    created_at = Column(DateTime(timezone=True), server_default=func.now())
