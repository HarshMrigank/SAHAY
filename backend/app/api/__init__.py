from fastapi import APIRouter
from app.api.endpoints import auth, cases, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
