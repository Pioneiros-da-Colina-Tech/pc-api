from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard
from app.auth.handler import AuthDependency, decode_token
from app.auth.schemas import UpdateUserSchema
from app.infra.database.adapter import SessionContext

from .domain import (
    AssignRoleUseCase,
    ListRolesUseCase,
    ListUsersUseCase,
    RevokeRoleUseCase,
    UpdateUserUseCase,
)
from .schemas import AssignRoleSchema, RevokeRoleSchema

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def list_roles(
    credentials: AuthDependency, session: SessionContext
) -> BaseResponseSchema:
    """List all available roles."""
    _ = await decode_token(credentials.credentials)
    return await ListRolesUseCase(session).execute()


@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_role(
    payload: AssignRoleSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Assign a role to a user. Only Diretor, Secretaria and Tesouraria can do this."""
    return await AssignRoleUseCase(payload, session).execute()


@router.delete("/revoke", status_code=status.HTTP_200_OK)
async def revoke_role(
    payload: RevokeRoleSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Revoke a role from a user. Only Diretor, Secretaria and Tesouraria can do this."""
    return await RevokeRoleUseCase(payload, session).execute()


@router.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    payload: UpdateUserSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Replace user editable fields (name, codigo_sgc). Only admin roles can do this."""
    return await UpdateUserUseCase(user_id, payload, session).execute()


@router.get("/users", status_code=status.HTTP_200_OK)
async def list_users(
    session: SessionContext,
    _: AdminGuard,
    search: str | None = Query(
        default=None, description="Partial CPF to search"
    ),
    page: int = Query(default=0, ge=0, description="Page index (0-based)"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Items per page"
    ),
) -> BaseResponseSchema:
    """
    List all users with optional search by document (CPF) and pagination.
    Only Diretor, Secretaria and Tesouraria can access this.
    """
    return await ListUsersUseCase(
        query=search, page=page, page_size=page_size, session=session
    ).execute()
