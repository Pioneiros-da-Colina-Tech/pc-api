from fastapi import APIRouter, status

from .schemas import BaseResponseSchema

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> BaseResponseSchema[None]:
    """Health check endpoint."""
    return BaseResponseSchema[None](message="healthy", data=None)
