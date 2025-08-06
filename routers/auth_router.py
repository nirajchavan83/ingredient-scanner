# routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import SendOTPRequest, VerifyOTPRequest, TokenResponse
from services.auth_service import send_otp, verify_otp
from database import get_db

router = APIRouter( tags=["Authentication"])

@router.post("/send-otp")
def send_otp_endpoint(payload: SendOTPRequest, db: Session = Depends(get_db)):
    otp = send_otp(payload.mobile, db)
    return {"message": f"OTP sent to {payload.mobile}"}

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_endpoint(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    token = verify_otp(payload.mobile, payload.otp, db)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    return {"access_token": token, "token_type": "bearer"}
