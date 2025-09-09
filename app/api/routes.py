from fastapi import APIRouter

from app.auth.routes import router as auth_router
from app.meetings.routes import router as meetings_router

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
