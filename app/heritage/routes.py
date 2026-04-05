from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.schemas import BaseResponseSchema
from app.auth.guards import AdminGuard
from app.auth.handler import AuthDependency
from app.infra.database.adapter import SessionContext

from .domain import (
    CreateItemUseCase,
    CreateRequestUseCase,
    DeleteItemUseCase,
    ListItemsUseCase,
    ListRequestsUseCase,
    UpdateItemUseCase,
    UpdateRequestStatusUseCase,
)
from .schemas import (
    CreateItemSchema,
    CreateRequestSchema,
    UpdateItemSchema,
    UpdateRequestStatusSchema,
)

router = APIRouter()


# --- Items ---


@router.get("/items")
async def list_items(
    session: SessionContext,
    _: AuthDependency,
    name: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> BaseResponseSchema:
    """List heritage items with optional search and pagination."""
    return await ListItemsUseCase(
        session, name=name, page=page, page_size=page_size
    ).execute()


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: CreateItemSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Add a new item to the heritage. Admin only."""
    return await CreateItemUseCase(payload, session).execute()


@router.put("/items/{item_id}")
async def update_item(
    item_id: UUID,
    payload: UpdateItemSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Update a heritage item. Admin only."""
    return await UpdateItemUseCase(item_id, payload, session).execute()


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: UUID,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Delete a heritage item. Admin only."""
    return await DeleteItemUseCase(item_id, session).execute()


# --- Requests ---


@router.post("/requests", status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: CreateRequestSchema,
    session: SessionContext,
    _: AuthDependency,
) -> BaseResponseSchema:
    """Submit a material request for a meeting."""
    return await CreateRequestUseCase(payload, session).execute()


@router.get("/requests")
async def list_requests(
    session: SessionContext,
    _: AuthDependency,
    unit_id: UUID | None = Query(default=None),
) -> BaseResponseSchema:
    """List material requests, optionally filtered by unit."""
    return await ListRequestsUseCase(unit_id, session).execute()


@router.patch("/requests/{request_id}/status")
async def update_request_status(
    request_id: UUID,
    payload: UpdateRequestStatusSchema,
    session: SessionContext,
    _: AdminGuard,
) -> BaseResponseSchema:
    """Update the status of a material request. Admin only."""
    return await UpdateRequestStatusUseCase(
        request_id, payload, session
    ).execute()
