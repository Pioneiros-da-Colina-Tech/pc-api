from datetime import UTC, datetime
from typing import Any, override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exc import does_not_exist
from app.infra.database.repository import Repository

from .entities import SpecialtiesEntity, UserSpecialtiesEntity
from .schemas import (
    CreateSpecialtySchema,
    CreateUserSpecialtySchema,
    SpecialtySchema,
    UpdateSpecialtySchema,
    UserSpecialtySchema,
)


class SpecialtiesRepository(Repository[SpecialtiesEntity, SpecialtySchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=SpecialtiesEntity)

    @override
    def to_entity(self, schema: SpecialtySchema) -> SpecialtiesEntity:
        return SpecialtiesEntity(
            id_=schema.id_,
            code=schema.code,
            name=schema.name,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: SpecialtiesEntity) -> SpecialtySchema:
        return SpecialtySchema(
            id_=entity.id_,
            code=entity.code,
            name=entity.name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_specialty(
        self, data: CreateSpecialtySchema
    ) -> SpecialtySchema:
        specialty = SpecialtySchema(
            id_=uuid4(),
            code=data.code,
            name=data.name,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(specialty)

    async def update_specialty(
        self, data: UpdateSpecialtySchema, **filters: Any
    ) -> SpecialtySchema:
        statement = (
            sa.update(SpecialtiesEntity)
            .filter_by(**filters)
            .values(
                **data.model_dump(exclude_unset=True, exclude_none=True),
                updated_at=datetime.now(UTC),
            )
            .returning(SpecialtiesEntity)
        )
        result = await self.context.execute(statement)
        updated = result.scalars().first()
        if updated is None:
            raise does_not_exist("Specialty")
        return self.to_schema(updated)

    async def search(
        self,
        query: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> tuple[list[SpecialtySchema], int]:
        """
        Search specialties by partial code or name match with pagination.
        Returns (items, total_count).
        """
        base = sa.select(SpecialtiesEntity).where(
            SpecialtiesEntity.deleted_at.is_(None)
        )

        if query:
            base = base.where(
                sa.or_(
                    SpecialtiesEntity.code.ilike(f"%{query}%"),
                    SpecialtiesEntity.name.ilike(f"%{query}%"),
                )
            )

        count_stmt = sa.select(sa.func.count()).select_from(base.subquery())
        count_result = await self.context.execute(count_stmt)
        total = count_result.scalar_one()

        items_stmt = (
            base.order_by(SpecialtiesEntity.code)
            .offset(page * page_size)
            .limit(page_size)
        )
        items_result = await self.context.execute(items_stmt)
        items = [self.to_schema(e) for e in items_result.scalars().all()]

        return items, total


class UserSpecialtiesRepository(
    Repository[UserSpecialtiesEntity, UserSpecialtySchema]
):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=UserSpecialtiesEntity)

    @override
    def to_entity(self, schema: UserSpecialtySchema) -> UserSpecialtiesEntity:
        return UserSpecialtiesEntity(
            id_=schema.id_,
            user_id=schema.user_id,
            specialty_id=schema.specialty_id,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: UserSpecialtiesEntity) -> UserSpecialtySchema:
        return UserSpecialtySchema(
            id_=entity.id_,
            user_id=entity.user_id,
            specialty_id=entity.specialty_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_user_specialty(
        self, user_id: UUID, data: CreateUserSpecialtySchema
    ) -> UserSpecialtySchema:
        user_specialty = UserSpecialtySchema(
            id_=uuid4(),
            user_id=user_id,
            specialty_id=data.specialty_id,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(user_specialty)

    async def get_by_user_and_specialty(
        self, user_id: UUID, specialty_id: UUID
    ) -> UserSpecialtySchema | None:
        statement = (
            sa.select(UserSpecialtiesEntity)
            .where(
                UserSpecialtiesEntity.user_id == user_id,
                UserSpecialtiesEntity.specialty_id == specialty_id,
            )
            .limit(1)
        )
        result = await self.context.execute(statement)
        entity = result.scalars().first()
        return self.to_schema(entity) if entity is not None else None

    async def fetch_user_specialties(
        self, user_id: UUID
    ) -> list[UserSpecialtySchema]:
        """Fetch all specialties for a specific user."""
        return await self.fetch(user_id=user_id)
