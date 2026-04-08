from fastapi import APIRouter

from app.api.v1.generations import router as generations_router
from app.api.v1.profiles import router as profiles_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(generations_router, tags=["generations"])
api_router.include_router(profiles_router, tags=["profiles"])
