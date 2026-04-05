from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    AddUnitMemberUseCase,
    CreateUnitUseCase,
    DeleteUnitUseCase,
    GetUnitUseCase,
    ListUnitMembersUseCase,
    ListUnitsUseCase,
    RemoveUnitMemberUseCase,
    UpdateUnitUseCase,
)
from .schemas import AddUnitMemberSchema, CreateUnitSchema, UpdateUnitSchema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_unit(
    payload: CreateUnitSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Create a new unit."""
    return await CreateUnitUseCase(payload, session).execute()


@router.get("")
async def list_units(
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """List all units."""
    return await ListUnitsUseCase(session).execute()


@router.get("/{unit_id}")
async def get_unit(
    unit_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get a unit by ID."""
    return await GetUnitUseCase(unit_id, session).execute()


@router.put("/{unit_id}")
async def update_unit(
    unit_id: UUID,
    payload: UpdateUnitSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Update a unit."""
    return await UpdateUnitUseCase(unit_id, payload, session).execute()


@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: UUID,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Delete a unit."""
    return await DeleteUnitUseCase(unit_id, session).execute()


@router.post("/{unit_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    unit_id: UUID,
    payload: AddUnitMemberSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Add a member to a unit for a given club year."""
    return await AddUnitMemberUseCase(unit_id, payload, session).execute()


@router.get("/{unit_id}/members")
async def list_members(
    unit_id: UUID,
    session: SessionContext,
    _: AuthDependency,
    club_year_id: str | None = Query(default=None, examples=["2024"]),
) -> BaseResponseSchema:
    """List members of a unit, optionally filtered by club year."""
    return await ListUnitMembersUseCase(
        unit_id, club_year_id, session
    ).execute()


@router.delete("/{unit_id}/members/{user_id}/{club_year_id}")
async def remove_member(
    unit_id: UUID,
    user_id: UUID,
    club_year_id: str,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Remove a member from a unit for a given club year."""
    return await RemoveUnitMemberUseCase(
        unit_id, user_id, club_year_id, session
    ).execute()
