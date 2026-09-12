from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.domain import Case, User, RoleEnum
from pydantic import BaseModel
import datetime

router = APIRouter()

class CaseResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    victim_id: int
    assigned_to: int | None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CaseResponse])
def get_cases(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Only Admin, NGO can see all cases. Responders and Therapists see only assigned ones.
    if current_user.role in [RoleEnum.ADMIN.value, RoleEnum.NGO.value]:
        return db.query(Case).all()
    else:
        return db.query(Case).filter(Case.assigned_to == current_user.id).all()

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if current_user.role not in [RoleEnum.ADMIN.value, RoleEnum.NGO.value] and case.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this case")
        
    return case
