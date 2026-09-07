from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class LoginRequest(BaseModel):
    userId: str
    password: str
    role: str

class LoginResponse(BaseModel):
    token: str
    user: dict

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    # Mock authentication for prototype
    return {
        "token": "mock-jwt-token-12345",
        "user": {
            "id": request.userId,
            "role": request.role,
            "name": f"Demo {request.role.capitalize()}"
        }
    }
