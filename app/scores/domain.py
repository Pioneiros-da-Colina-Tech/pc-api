from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import does_not_exist, validation_error
from app.api.schemas import BaseResponseSchema
from app.attendance.concepts import AttendanceStatus
from app.attendance.repository import AttendanceRepository
from app.attendance.schemas import RecordAttendanceSchema, UpdateAttendanceSchema
from app.auth.repository import UserRepository
from app.meetings.repository import MeetingsRepository

from .repository import ScoreRepository
from .schemas import BonusScoreCreateSchema, SubmitMeetingScoresSchema


def _presenca_to_status(presenca: int) -> AttendanceStatus:
    if presenca >= 10:
        return AttendanceStatus.PRESENTE
    if presenca >= 5:
        return AttendanceStatus.JUSTIFICADO
    return AttendanceStatus.AUSENTE


@dataclass
class SubmitMeetingScoresUseCase(ApiDomain):
    meeting_id: UUID
    payload: SubmitMeetingScoresSchema
    session: AsyncSession

    @cached_property
    def score_repo(self) -> ScoreRepository:
        return ScoreRepository(self.session)

    @cached_property
    def meeting_repo(self) -> MeetingsRepository:
        return MeetingsRepository(self.session)

    @cached_property
    def user_repo(self) -> UserRepository:
        return UserRepository(self.session)

    @cached_property
    def attendance_repo(self) -> AttendanceRepository:
        return AttendanceRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.meeting_repo.exists(id_=self.meeting_id):
            raise does_not_exist("Meeting")

        results = []
        for item in self.payload.scores:
            if not await self.user_repo.exists(id_=item.user_id):
                raise does_not_exist(f"User {item.user_id}")

            # Upsert score
            score = await self.score_repo.upsert_meeting_score(self.meeting_id, item)
            results.append(score)

            # Keep attendance table in sync
            att_status = _presenca_to_status(item.presenca)
            already_exists = await self.attendance_repo.exists(
                meeting_id=self.meeting_id, user_id=item.user_id
            )
            if already_exists:
                await self.attendance_repo.update_attendance(
                    self.meeting_id,
                    item.user_id,
                    UpdateAttendanceSchema(attendance_status=att_status),
                )
            else:
                await self.attendance_repo.record_attendance(
                    self.meeting_id,
                    RecordAttendanceSchema(
                        user_id=item.user_id, attendance_status=att_status
                    ),
                )

        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Scores submitted successfully",
            data=results,
        )


@dataclass
class GetMeetingScoresUseCase(ApiDomain):
    meeting_id: UUID
    session: AsyncSession

    @cached_property
    def score_repo(self) -> ScoreRepository:
        return ScoreRepository(self.session)

    @cached_property
    def meeting_repo(self) -> MeetingsRepository:
        return MeetingsRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.meeting_repo.exists(id_=self.meeting_id):
            raise does_not_exist("Meeting")
        result = await self.score_repo.get_meeting_scores(self.meeting_id)
        return BaseResponseSchema(
            message="Scores retrieved successfully",
            data=result,
        )


@dataclass
class GetRankingUseCase(ApiDomain):
    year: str
    semester: int
    session: AsyncSession

    @cached_property
    def score_repo(self) -> ScoreRepository:
        return ScoreRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.score_repo.get_ranking(self.year, self.semester)
        return BaseResponseSchema(
            message="Ranking retrieved successfully",
            data=result,
        )


@dataclass
class CreateBonusUseCase(ApiDomain):
    payload: BonusScoreCreateSchema
    session: AsyncSession

    @cached_property
    def score_repo(self) -> ScoreRepository:
        return ScoreRepository(self.session)

    @cached_property
    def user_repo(self) -> UserRepository:
        return UserRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if self.payload.user_id and not await self.user_repo.exists(
            id_=self.payload.user_id
        ):
            raise does_not_exist("User")

        if self.payload.unit_id:
            from app.units.repository import UnitRepository
            if not await UnitRepository(self.session).exists(id_=self.payload.unit_id):
                raise does_not_exist("Unit")

        result = await self.score_repo.create_bonus(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Bonus created successfully",
            data=result,
        )


@dataclass
class ListBonusesUseCase(ApiDomain):
    year: str
    semester: int
    session: AsyncSession

    @cached_property
    def score_repo(self) -> ScoreRepository:
        return ScoreRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.score_repo.list_bonuses(self.year, self.semester)
        return BaseResponseSchema(
            message="Bonuses retrieved successfully",
            data=result,
        )
