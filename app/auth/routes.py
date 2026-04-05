from fastapi import APIRouter

from app.api.schemas import BaseResponseSchema
from app.auth.handler import AuthDependency, decode_token
from app.infra.database.adapter import SessionContext
from app.roles.repository import RoleScreenRepository, UserRoleRepository

from .domain import AuthLoginUseCase, AuthRegisterUseCase
from .repository import UserRepository
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
async def me(
    credentials: AuthDependency, session: SessionContext
) -> BaseResponseSchema:
    """Get current user info with assigned roles and accessible screens."""
    token_data = await decode_token(credentials.credentials)

    user = await UserRepository(session).get(document=token_data.document)

    roles = await UserRoleRepository(session).get_roles_for_user(user.id_)
    screens = await RoleScreenRepository(session).get_screens_for_roles(roles)

    return BaseResponseSchema(
        data={"user": user, "roles": roles, "screens": screens},
        message="User information retrieved successfully",
    )
