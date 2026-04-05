from uuid import UUID

from fastapi import APIRouter, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AttendanceGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    ListAttendanceUseCase,
    RecordAttendanceUseCase,
    UpdateAttendanceUseCase,
)
from .schemas import RecordAttendanceSchema, UpdateAttendanceSchema

router = APIRouter()


@router.post("/{meeting_id}/attendance", status_code=status.HTTP_201_CREATED)
async def record_attendance(
    meeting_id: UUID,
    payload: RecordAttendanceSchema,
    session: SessionContext,
    _: AttendanceGuard,
) -> BaseResponseSchema:
    """Record attendance for a user in a meeting."""
    return await RecordAttendanceUseCase(meeting_id, payload, session).execute()


@router.get("/{meeting_id}/attendance")
async def list_attendance(
    meeting_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get all attendance records for a meeting."""
    return await ListAttendanceUseCase(meeting_id, session).execute()


@router.patch("/{meeting_id}/attendance/{user_id}")
async def update_attendance(
    meeting_id: UUID,
    user_id: UUID,
    payload: UpdateAttendanceSchema,
    session: SessionContext,
    _: AttendanceGuard,
) -> BaseResponseSchema:
    """Update attendance status for a user in a meeting."""
    return await UpdateAttendanceUseCase(
        meeting_id, user_id, payload, session
    ).execute()
