from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.user import UserRegistrationSubmit, RegistrationRequestResponse, UserResponse, Token, LoginRequest
from app.models.domain import RegistrationRequest, RequestStatus, User, RoleEnum
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=RegistrationRequestResponse)
def submit_registration(request: UserRegistrationSubmit, db: Session = Depends(deps.get_db)):
    # Check if email is already used in active users or pending requests
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    existing_req = db.query(RegistrationRequest).filter(
        RegistrationRequest.email == request.email, 
        RegistrationRequest.status == RequestStatus.PENDING.value
    ).first()
    if existing_req:
        raise HTTPException(status_code=400, detail="Registration request already pending")

    new_request = RegistrationRequest(
        name=request.name,
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=request.role,
        organization=request.organization,
        status=RequestStatus.PENDING.value
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("/registration-requests", response_model=List[RegistrationRequestResponse])
def get_registration_requests(
    db: Session = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    return db.query(RegistrationRequest).filter(RegistrationRequest.status == RequestStatus.PENDING.value).all()

@router.post("/registration-requests/{request_id}/approve", response_model=UserResponse)
def approve_registration(
    request_id: int, 
    db: Session = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    req = db.query(RegistrationRequest).filter(RegistrationRequest.id == request_id).first()
    if not req or req.status != RequestStatus.PENDING.value:
        raise HTTPException(status_code=404, detail="Pending request not found")
        
    # Approve and create user
    req.status = RequestStatus.APPROVED.value
    
    new_user = User(
        email=req.email,
        hashed_password=req.password_hash,
        full_name=req.name,
        role=req.role,
        organization=req.organization,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/registration-requests/{request_id}/reject")
def reject_registration(
    request_id: int, 
    db: Session = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    req = db.query(RegistrationRequest).filter(RegistrationRequest.id == request_id).first()
    if not req or req.status != RequestStatus.PENDING.value:
        raise HTTPException(status_code=404, detail="Pending request not found")
        
    req.status = RequestStatus.REJECTED.value
    db.commit()
    return {"message": "Request rejected"}

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(deps.get_current_user)):
    return current_user
