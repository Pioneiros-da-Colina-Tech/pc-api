from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typeid import TypeID

from .entities import UsersEntity
from .schemas import User, UserSchema


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def to_schema(self, entity: UsersEntity) -> User:
        return User(
            id_=entity.id_,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name or "",
            disabled=entity.disabled,
            sgc_code=entity.sgc_code,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, schema: User) -> UsersEntity:
        return UsersEntity(
            id_=schema.id_,
            username=schema.username,
            email=schema.email,
            hashed_password=schema.hashed_password,
            full_name=schema.full_name,
            disabled=schema.disabled,
            sgc_code=schema.sgc_code,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
        )

    async def create_user(
        self,
        user_data: UserSchema,
        hashed_password: str,
        phone_number: str | None = None,
    ) -> User:
        """Create a new user in the database."""
        user_entity = UsersEntity(
            id_=TypeID(),
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.name,
            phone_number=phone_number,
            disabled=user_data.disabled,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.session.add(user_entity)
        await self.session.flush()
        await self.session.refresh(user_entity)

        return self.to_schema(user_entity)

    async def get_user_by_id(self, user_id: TypeID) -> User | None:
        """Get a user by their ID."""
        stmt = select(UsersEntity).where(
            UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        user_entity = result.scalar_one_or_none()

        return self.to_schema(user_entity) if user_entity else None

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by their username."""
        stmt = select(UsersEntity).where(
            UsersEntity.username == username, UsersEntity.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        user_entity = result.scalar_one_or_none()

        return self.to_schema(user_entity) if user_entity else None

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by their email."""
        stmt = select(UsersEntity).where(
            UsersEntity.email == email, UsersEntity.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        user_entity = result.scalar_one_or_none()

        return self.to_schema(user_entity) if user_entity else None

    async def update_user(self, user_id: TypeID, **updates: Any) -> User | None:
        """Update a user's information."""
        updates["updated_at"] = datetime.now(UTC)

        stmt = (
            update(UsersEntity)
            .where(UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None))
            .values(**updates)
            .returning(UsersEntity)
        )

        result = await self.session.execute(stmt)
        updated_entity = result.scalar_one_or_none()

        return self.to_schema(updated_entity) if updated_entity else None

    async def update_password(
        self, user_id: TypeID, hashed_password: str
    ) -> bool:
        """Update a user's password."""
        stmt = (
            update(UsersEntity)
            .where(UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None))
            .values(
                hashed_password=hashed_password, updated_at=datetime.now(UTC)
            )
        )

        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def disable_user(self, user_id: TypeID) -> bool:
        """Disable a user account."""
        stmt = (
            update(UsersEntity)
            .where(UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None))
            .values(disabled=True, updated_at=datetime.now(UTC))
        )

        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def enable_user(self, user_id: TypeID) -> bool:
        """Enable a user account."""
        stmt = (
            update(UsersEntity)
            .where(UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None))
            .values(disabled=False, updated_at=datetime.now(UTC))
        )

        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def soft_delete_user(self, user_id: TypeID) -> bool:
        """Soft delete a user by setting deleted_at timestamp."""
        stmt = (
            update(UsersEntity)
            .where(UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None))
            .values(deleted_at=datetime.now(UTC), updated_at=datetime.now(UTC))
        )

        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def hard_delete_user(self, user_id: TypeID) -> bool:
        """Permanently delete a user from the database."""
        stmt = delete(UsersEntity).where(UsersEntity.id_ == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def list_users(
        self, limit: int = 100, offset: int = 0, include_disabled: bool = False
    ) -> Sequence[User]:
        """List users with pagination."""
        stmt = select(UsersEntity).where(UsersEntity.deleted_at.is_(None))

        if not include_disabled:
            stmt = stmt.where(UsersEntity.disabled == False)

        stmt = (
            stmt.offset(offset)
            .limit(limit)
            .order_by(UsersEntity.created_at.desc())
        )

        result = await self.session.execute(stmt)
        entities = result.scalars().all()

        return [self.to_schema(entity) for entity in entities]

    async def count_users(self, include_disabled: bool = False) -> int:
        """Count total number of users."""
        from sqlalchemy import func

        stmt = select(func.count(UsersEntity.id_)).where(
            UsersEntity.deleted_at.is_(None)
        )

        if not include_disabled:
            stmt = stmt.where(UsersEntity.disabled == False)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def user_exists(
        self, username: str | None = None, email: str | None = None
    ) -> bool:
        """Check if a user exists by username or email."""
        if not username and not email:
            return False

        stmt = select(UsersEntity.id_).where(UsersEntity.deleted_at.is_(None))

        if username and email:
            stmt = stmt.where(
                (UsersEntity.username == username)
                | (UsersEntity.email == email)
            )
        elif username:
            stmt = stmt.where(UsersEntity.username == username)
        elif email:
            stmt = stmt.where(UsersEntity.email == email)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def search_users(self, query: str, limit: int = 50) -> Sequence[User]:
        """Search users by username, email, or full name."""
        search_pattern = f"%{query}%"

        stmt = (
            select(UsersEntity)
            .where(
                UsersEntity.deleted_at.is_(None),
                UsersEntity.disabled == False,
                (
                    UsersEntity.username.ilike(search_pattern)
                    | UsersEntity.email.ilike(search_pattern)
                    | UsersEntity.full_name.ilike(search_pattern)
                    | UsersEntity.phone_number.ilike(search_pattern)
                ),
            )
            .limit(limit)
            .order_by(UsersEntity.username)
        )

        result = await self.session.execute(stmt)
        entities = result.scalars().all()

        return [self.to_schema(entity) for entity in entities]
