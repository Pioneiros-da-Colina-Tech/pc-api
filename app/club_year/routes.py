from fastapi import APIRouter, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    CreateClubYearUseCase,
    DeleteClubYearUseCase,
    GetClubYearUseCase,
    ListClubYearsUseCase,
)
from .schemas import CreateClubYearSchema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_club_year(
    payload: CreateClubYearSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Create a new club year."""
    return await CreateClubYearUseCase(payload, session).execute()


@router.get("")
async def list_club_years(
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """List all club years."""
    return await ListClubYearsUseCase(session).execute()


@router.get("/{id_}")
async def get_club_year(
    id_: str,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get a club year by ID."""
    return await GetClubYearUseCase(id_, session).execute()


@router.delete("/{id_}", status_code=status.HTTP_200_OK)
async def delete_club_year(
    id_: str,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Delete a club year."""
    return await DeleteClubYearUseCase(id_, session).execute()
