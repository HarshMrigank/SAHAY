from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import datetime

router = APIRouter()

# Mock data
MOCK_CASES = [
    {
        "id": "CASE-1042",
        "victimId": "VIC-001",
        "district": "North District",
        "status": "Active",
        "risk": "HIGH",
        "trend": "Increasing",
        "lastCheckIn": "2026-09-07T10:00:00Z",
        "assignedOfficer": "Counsellor A",
        "distressScore": 74
    },
    {
        "id": "CASE-1078",
        "victimId": "VIC-002",
        "district": "South District",
        "status": "Active",
        "risk": "MODERATE",
        "trend": "Stable",
        "lastCheckIn": "2026-09-06T14:30:00Z",
        "assignedOfficer": "Counsellor B",
        "distressScore": 45
    }
]

@router.get("/")
def get_cases():
    return MOCK_CASES

@router.get("/{case_id}")
def get_case(case_id: str):
    for case in MOCK_CASES:
        if case["id"] == case_id:
            return case
    return {"error": "Case not found"}
