from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard, AttendanceGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    CreateBonusUseCase,
    GetMeetingScoresUseCase,
    GetRankingUseCase,
    ListBonusesUseCase,
    SubmitMeetingScoresUseCase,
)
from .schemas import BonusScoreCreateSchema, SubmitMeetingScoresSchema

router = APIRouter()


@router.post(
    "/meetings/{meeting_id}",
    status_code=status.HTTP_201_CREATED,
    tags=["Scores"],
)
async def submit_meeting_scores(
    meeting_id: UUID,
    payload: SubmitMeetingScoresSchema,
    session: SessionContext,
    _: AttendanceGuard,
) -> BaseResponseSchema:
    """Batch-submit per-user scores for a meeting (also syncs attendance status)."""
    return await SubmitMeetingScoresUseCase(meeting_id, payload, session).execute()


@router.get("/meetings/{meeting_id}", tags=["Scores"])
async def get_meeting_scores(
    meeting_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get all scores for a meeting."""
    return await GetMeetingScoresUseCase(meeting_id, session).execute()


@router.get("/ranking", tags=["Scores"])
async def get_ranking(
    session: SessionContext,
    _: AuthDependency,
    year: str = Query(examples=["2025"]),
    semester: int = Query(ge=1, le=2, examples=[1]),
) -> BaseResponseSchema:
    """Get individual and unit ranking for a given year/semester."""
    return await GetRankingUseCase(year, semester, session).execute()


@router.post("/bonus", status_code=status.HTTP_201_CREATED, tags=["Scores"])
async def create_bonus(
    payload: BonusScoreCreateSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Add a bonus score to a user or a unit."""
    return await CreateBonusUseCase(payload, session).execute()


@router.get("/bonus", tags=["Scores"])
async def list_bonuses(
    session: SessionContext,
    _: AuthDependency,
    year: str = Query(examples=["2025"]),
    semester: int = Query(ge=1, le=2, examples=[1]),
) -> BaseResponseSchema:
    """List all bonuses for a given year/semester."""
    return await ListBonusesUseCase(year, semester, session).execute()
