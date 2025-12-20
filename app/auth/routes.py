from fastapi import APIRouter

from app.api.schemas import BaseResponseSchema
from app.auth.handler import protected
from app.infra.database.adapter import SessionContext

from .domain import AuthLoginUseCase, AuthRegisterUseCase
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


@protected
@router.get("/me")
async def me() -> BaseResponseSchema:
    """Get current user information."""
    return BaseResponseSchema(
        data=None, message="User information retrieved successfully"
    )
