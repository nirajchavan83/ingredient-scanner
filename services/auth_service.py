# services/auth_service.py

import random
from sqlalchemy.orm import Session
from models.user import User
from utils.token import create_access_token

def generate_otp() -> str:
    # return str(random.randint(100000, 999999))  # 🔁 original dynamic OTP logic
    return "123456"  # 🔒 Fixed OTP for development/testing

def send_otp(mobile: str, db: Session):
    otp = generate_otp()
    user = db.query(User).filter(User.mobile == mobile).first()

    if not user:
        user = User(mobile=mobile, otp_code=otp)
        db.add(user)
    else:
        user.otp_code = otp

    db.commit()
    print(f"✅ OTP for {mobile}: {otp}")
    return otp

def verify_otp(mobile: str, otp: str, db: Session):
    user = db.query(User).filter(User.mobile == mobile, User.otp_code == otp).first()

    if not user:
        return None

    user.is_verified = True
    access_token = create_access_token({"user_id": user.id, "mobile": user.mobile})
    user.token = access_token
    db.commit()
    return access_token
