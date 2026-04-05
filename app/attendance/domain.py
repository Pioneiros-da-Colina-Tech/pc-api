from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import already_exists, does_not_exist
from app.api.schemas import BaseResponseSchema
from app.auth.repository import UserRepository
from app.meetings.repository import MeetingsRepository

from .repository import AttendanceRepository
from .schemas import RecordAttendanceSchema, UpdateAttendanceSchema


@dataclass
class RecordAttendanceUseCase(ApiDomain):
    meeting_id: UUID
    payload: RecordAttendanceSchema
    session: AsyncSession

    @cached_property
    def meeting_repository(self) -> MeetingsRepository:
        return MeetingsRepository(self.session)

    @cached_property
    def user_repository(self) -> UserRepository:
        return UserRepository(self.session)

    @cached_property
    def repository(self) -> AttendanceRepository:
        return AttendanceRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.meeting_repository.exists(id_=self.meeting_id):
            raise does_not_exist("Meeting")
        if not await self.user_repository.exists(id_=self.payload.user_id):
            raise does_not_exist("User")
        if await self.repository.exists(
            meeting_id=self.meeting_id, user_id=self.payload.user_id
        ):
            raise already_exists("Attendance")
        result = await self.repository.record_attendance(
            self.meeting_id, self.payload
        )
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Attendance recorded successfully",
            data=result,
        )


@dataclass
class ListAttendanceUseCase(ApiDomain):
    meeting_id: UUID
    session: AsyncSession

    @cached_property
    def meeting_repository(self) -> MeetingsRepository:
        return MeetingsRepository(self.session)

    @cached_property
    def repository(self) -> AttendanceRepository:
        return AttendanceRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.meeting_repository.exists(id_=self.meeting_id):
            raise does_not_exist("Meeting")
        result = await self.repository.list_by_meeting(self.meeting_id)
        return BaseResponseSchema(
            message="Attendance retrieved successfully",
            data=result,
        )


@dataclass
class UpdateAttendanceUseCase(ApiDomain):
    meeting_id: UUID
    user_id: UUID
    payload: UpdateAttendanceSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> AttendanceRepository:
        return AttendanceRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.update_attendance(
            self.meeting_id, self.user_id, self.payload
        )
        return BaseResponseSchema(
            message="Attendance updated successfully",
            data=result,
        )
