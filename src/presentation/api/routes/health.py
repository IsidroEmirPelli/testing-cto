from fastapi import APIRouter

from src.infrastructure.config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }
