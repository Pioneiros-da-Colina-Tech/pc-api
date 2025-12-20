from fastapi import APIRouter

from app.api.schemas import BaseResponseSchema
from app.infra.database.adapter import SessionContext

from .domain import AuthLoginUseCase, AuthRegisterUseCase
from .handler import CurrentUser
from .schemas import BaseUserSchema, CreateUserSchema

router = APIRouter()


@router.post("/login")
async def login(
    payload: BaseUserSchema, session: SessionContext
) -> BaseResponseSchema:
    """Login endpoint using document and birth date."""
    return await AuthLoginUseCase(payload, session).execute()


@router.post("/register")
async def register(
    payload: CreateUserSchema, session: SessionContext
) -> BaseResponseSchema:
    """Register endpoint using document and birth date."""
    return await AuthRegisterUseCase(payload, session).execute()


@router.get("/me")
async def me(current_user: CurrentUser) -> BaseResponseSchema:
    """Get current user information from JWT token."""
    return BaseResponseSchema(
        data=current_user, message="User information retrieved successfully"
    )
