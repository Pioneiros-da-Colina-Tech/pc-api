from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    AssignSpecialtyToUserUseCase,
    CreateSpecialtyUseCase,
    DeleteSpecialtyUseCase,
    GetSpecialtyUseCase,
    ListSpecialtiesUseCase,
    ListUserSpecialtiesUseCase,
    RemoveSpecialtyFromUserUseCase,
    UpdateSpecialtyUseCase,
)
from .schemas import (
    CreateSpecialtySchema,
    CreateUserSpecialtySchema,
    UpdateSpecialtySchema,
)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_specialty(
    payload: CreateSpecialtySchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Create a new specialty."""
    return await CreateSpecialtyUseCase(payload, session).execute()


@router.get("")
async def list_specialties(
    session: SessionContext,
    _: AuthDependency,
    search: str | None = Query(
        default=None, description="Search by code or name"
    ),
    page: int = Query(default=0, ge=0, description="Page index (0-based)"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Items per page"
    ),
) -> BaseResponseSchema:
    """List all specialties with optional search and pagination."""
    return await ListSpecialtiesUseCase(
        query=search, page=page, page_size=page_size, session=session
    ).execute()


@router.get("/{specialty_id}")
async def get_specialty(
    specialty_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get a specialty by ID."""
    return await GetSpecialtyUseCase(specialty_id, session).execute()


@router.put("/{specialty_id}")
async def update_specialty(
    specialty_id: UUID,
    payload: UpdateSpecialtySchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Update a specialty."""
    return await UpdateSpecialtyUseCase(
        specialty_id, payload, session
    ).execute()


@router.delete("/{specialty_id}")
async def delete_specialty(
    specialty_id: UUID,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Delete a specialty."""
    return await DeleteSpecialtyUseCase(specialty_id, session).execute()


# --- User Specialties Routes ---


@router.post("/users/{user_id}", status_code=status.HTTP_201_CREATED)
async def assign_specialty_to_user(
    user_id: UUID,
    payload: CreateUserSpecialtySchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Assign a specialty to a user."""
    return await AssignSpecialtyToUserUseCase(
        user_id, payload, session
    ).execute()


@router.get("/users/{user_id}")
async def list_user_specialties(
    user_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """List all specialties for a user."""
    return await ListUserSpecialtiesUseCase(user_id, session).execute()


@router.delete("/users/{user_id}/{user_specialty_id}")
async def remove_specialty_from_user(
    user_id: UUID,
    user_specialty_id: UUID,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Remove a specialty from a user."""
    return await RemoveSpecialtyFromUserUseCase(
        user_id, user_specialty_id, session
    ).execute()
