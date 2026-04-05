from uuid import UUID

from fastapi import APIRouter, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    CreateClassesRequirementUseCase,
    CreateClassesUseCase,
    DeleteClassesRequirementUseCase,
    DeleteClassesUseCase,
    GetClassesUseCase,
    ListClassesRequirementsUseCase,
    ListClassesUseCase,
    UpdateClassesRequirementUseCase,
    UpdateClassesUseCase,
)
from .schemas import (
    CreateClassesRequirementSchema,
    CreateClassesSchema,
    UpdateClassesRequirementSchema,
    UpdateClassesSchema,
)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_class(
    payload: CreateClassesSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Create a new class."""
    return await CreateClassesUseCase(payload, session).execute()


@router.get("")
async def list_classes(
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """List all classes."""
    return await ListClassesUseCase(session).execute()


@router.get("/{class_id}")
async def get_class(
    class_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Get a class by ID."""
    return await GetClassesUseCase(class_id, session).execute()


@router.put("/{class_id}")
async def update_class(
    class_id: UUID,
    payload: UpdateClassesSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Update a class."""
    return await UpdateClassesUseCase(class_id, payload, session).execute()


@router.delete("/{class_id}")
async def delete_class(
    class_id: UUID,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Delete a class."""
    return await DeleteClassesUseCase(class_id, session).execute()


@router.post("/{class_id}/requirements", status_code=status.HTTP_201_CREATED)
async def create_requirement(
    class_id: UUID,
    payload: CreateClassesRequirementSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Add a requirement to a class."""
    return await CreateClassesRequirementUseCase(
        class_id, payload, session
    ).execute()


@router.get("/{class_id}/requirements")
async def list_requirements(
    class_id: UUID,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """List all requirements for a class."""
    return await ListClassesRequirementsUseCase(class_id, session).execute()


@router.put("/{class_id}/requirements/{requirement_id}")
async def update_requirement(
    class_id: UUID,
    requirement_id: UUID,
    payload: UpdateClassesRequirementSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Update a requirement."""
    return await UpdateClassesRequirementUseCase(
        class_id, requirement_id, payload, session
    ).execute()


@router.delete("/{class_id}/requirements/{requirement_id}")
async def delete_requirement(
    class_id: UUID,
    requirement_id: UUID,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Delete a requirement from a class."""
    return await DeleteClassesRequirementUseCase(
        class_id, requirement_id, session
    ).execute()
