from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegistrationSubmit(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    organization: Optional[str] = None

class RegistrationRequestResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    organization: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    organization: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
