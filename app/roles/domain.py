from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import already_exists, does_not_exist
from app.api.schemas import BaseResponseSchema
from app.auth.repository import UserRepository

from .repository import RoleRepository, RoleScreenRepository, UserRoleRepository
from .schemas import AssignRoleSchema, RevokeRoleSchema, UserPermissionsSchema


@dataclass
class ListRolesUseCase(ApiDomain):
    session: AsyncSession

    @cached_property
    def repository(self) -> RoleRepository:
        return RoleRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        roles = await self.repository.fetch_all()
        return BaseResponseSchema(
            status=status.HTTP_200_OK,
            message="Roles retrieved successfully",
            data=roles,
        )


@dataclass
class AssignRoleUseCase(ApiDomain):
    payload: AssignRoleSchema
    session: AsyncSession

    @cached_property
    def role_repo(self) -> RoleRepository:
        return RoleRepository(self.session)

    @cached_property
    def user_role_repo(self) -> UserRoleRepository:
        return UserRoleRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        role_exists = await self.role_repo.exists(id_=self.payload.role_id)
        if not role_exists:
            raise does_not_exist("Role")

        already_assigned = await self.user_role_repo.exists(
            user_id=self.payload.user_id, role_id=self.payload.role_id
        )
        if already_assigned:
            raise already_exists("UserRole")

        result = await self.user_role_repo.assign(
            user_id=self.payload.user_id, role_id=self.payload.role_id
        )
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Role assigned successfully",
            data=result,
        )


@dataclass
class RevokeRoleUseCase(ApiDomain):
    payload: RevokeRoleSchema
    session: AsyncSession

    @cached_property
    def user_role_repo(self) -> UserRoleRepository:
        return UserRoleRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        assigned = await self.user_role_repo.exists(
            user_id=self.payload.user_id, role_id=self.payload.role_id
        )
        if not assigned:
            raise does_not_exist("UserRole")

        await self.user_role_repo.revoke(
            user_id=self.payload.user_id, role_id=self.payload.role_id
        )
        return BaseResponseSchema(
            status=status.HTTP_200_OK,
            message="Role revoked successfully",
            data=None,
        )


@dataclass
class ListUsersUseCase(ApiDomain):
    query: str | None
    page: int
    page_size: int
    session: AsyncSession

    @cached_property
    def user_repo(self) -> UserRepository:
        return UserRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        items, total = await self.user_repo.search(
            query=self.query,
            page=self.page,
            page_size=self.page_size,
        )
        return BaseResponseSchema(
            status=status.HTTP_200_OK,
            message="Users retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": self.page,
                "page_size": self.page_size,
            },
        )


@dataclass
class GetUserPermissionsUseCase(ApiDomain):
    user_id: UUID
    session: AsyncSession

    @cached_property
    def user_role_repo(self) -> UserRoleRepository:
        return UserRoleRepository(self.session)

    @cached_property
    def role_screen_repo(self) -> RoleScreenRepository:
        return RoleScreenRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        roles = await self.user_role_repo.get_roles_for_user(self.user_id)
        screens = await self.role_screen_repo.get_screens_for_roles(roles)
        permissions = UserPermissionsSchema(roles=roles, screens=screens)
        return BaseResponseSchema(
            status=status.HTTP_200_OK,
            message="Permissions retrieved successfully",
            data=permissions,
        )
