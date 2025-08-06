# schemas/user.py

from pydantic import BaseModel

class SendOTPRequest(BaseModel):
    mobile: str

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
