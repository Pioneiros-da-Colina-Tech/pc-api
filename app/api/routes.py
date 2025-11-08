from fastapi import APIRouter, status

from app.meetings.routes import router as meetings_router

from .schemas import BaseResponseSchema

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> BaseResponseSchema[None]:
    """Health check endpoint."""
    return BaseResponseSchema[None](message="healthy", data=None)


router.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
