from fastapi import APIRouter, status

from app.api.schemas import BaseResponseSchema
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import CreateMeetingUseCase
from .schemas import CreateMeetingSchema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: CreateMeetingSchema,
    session: SessionContext,
    _: AuthDependency,
):
    """Create a new meeting (protected route)."""
    return await CreateMeetingUseCase(payload, session).execute()


@router.get("")
async def get_meetings(_: AuthDependency) -> BaseResponseSchema:
    """Get all meetings for the authenticated user."""
    return BaseResponseSchema(
        message="Meetings retrieved successfully",
        data={"meetings": []},
    )


@router.get("/my-meetings")
async def get_my_meetings(_: AuthDependency) -> BaseResponseSchema:
    """Get meetings created by the current user."""
    return BaseResponseSchema(
        message='Meetings for user "" retrieved successfully',
        data={"meetings": []},
    )
