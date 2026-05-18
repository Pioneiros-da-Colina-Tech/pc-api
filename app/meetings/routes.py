from uuid import UUID

from fastapi import APIRouter, status

from app.api.schemas import BaseResponseSchema
from app.auth.handler import AuthDependency, CurrentUser
from app.infra.database.adapter import SessionContext

from .domain import (
    CreateMeetingUseCase,
    DeleteMeetingUseCase,
    GetMeetingUseCase,
    ListMeetingsUseCase,
    UpdateMeetingUseCase,
)
from .schemas import CreateMeetingSchema, UpdateMeetingSchema

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
async def get_meetings(
    session: SessionContext, _: AuthDependency
) -> BaseResponseSchema:
    """Get all meetings."""
    return await ListMeetingsUseCase(session).execute()


@router.get("/my-meetings")
async def get_my_meetings(
    session: SessionContext, current_user: CurrentUser
) -> BaseResponseSchema:
    """Get meetings for the authenticated user."""
    return await ListMeetingsUseCase(
        session=session, user_id=current_user.id_
    ).execute()


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get a meeting by ID. Meetings are club-wide resources visible to all authenticated members."""
    return await GetMeetingUseCase(meeting_id, session).execute()


@router.patch("/{meeting_id}")
async def update_meeting(
    meeting_id: UUID,
    payload: UpdateMeetingSchema,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Partially update a meeting (name and/or date)."""
    return await UpdateMeetingUseCase(meeting_id, payload, session).execute()


@router.delete("/{meeting_id}", status_code=status.HTTP_200_OK)
async def delete_meeting(
    meeting_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Delete a meeting."""
    return await DeleteMeetingUseCase(meeting_id, session).execute()
