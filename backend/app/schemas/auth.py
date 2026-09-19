from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    email: str
    password: str

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)
