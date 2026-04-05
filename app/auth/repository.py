from datetime import UTC, datetime
from typing import override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.entities import UsersEntity
from app.auth.schemas import (
    CreateUserSchema,
    UpdateUserSchema,
    UserSchema,
    UserWithUnitSchema,
)
from app.infra.database.repository import Repository
from app.units.entities import UnitEntity, UnitMemberEntity


class UserRepository(Repository[UsersEntity, UserSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=UsersEntity)

    @override
    def to_entity(self, schema: UserSchema) -> UsersEntity:
        return UsersEntity(
            id_=schema.id_,
            document=schema.document,
            birth_date=schema.birth_date,
            name=schema.name,
            codigo_sgc=schema.codigo_sgc,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: UsersEntity) -> UserSchema:
        return UserSchema(
            id_=entity.id_,
            document=entity.document,
            birth_date=entity.birth_date,
            name=entity.name,
            codigo_sgc=entity.codigo_sgc,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def update_user(
        self, user_id: UUID, payload: UpdateUserSchema
    ) -> UserSchema:
        stmt = (
            sa.update(UsersEntity)
            .where(UsersEntity.id_ == user_id, UsersEntity.deleted_at.is_(None))
            .values(
                name=payload.name,
                codigo_sgc=payload.codigo_sgc,
                updated_at=datetime.now(UTC),
            )
            .returning(UsersEntity)
        )
        result = await self.context.execute(stmt)
        entity = result.scalars().first()
        if entity is None:
            from app.api.exc import does_not_exist

            raise does_not_exist("User")
        return self.to_schema(entity)

    async def create_user(self, data: CreateUserSchema) -> UserSchema:
        user_data = UserSchema(
            id_=uuid4(),
            document=data.document,
            birth_date=data.birth_date,
            name=data.name,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(user_data)

    async def search(
        self,
        query: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> tuple[list[UserSchema], int]:
        """Search active users by partial document or name match."""
        base = sa.select(UsersEntity).where(UsersEntity.deleted_at.is_(None))

        if query:
            base = base.where(
                sa.or_(
                    UsersEntity.document.ilike(f"%{query}%"),
                    UsersEntity.name.ilike(f"%{query}%"),
                )
            )

        count_stmt = sa.select(sa.func.count()).select_from(base.subquery())
        count_result = await self.context.execute(count_stmt)
        total = count_result.scalar_one()

        items_stmt = base.offset(page * page_size).limit(page_size)
        items_result = await self.context.execute(items_stmt)
        items = [self.to_schema(e) for e in items_result.scalars().all()]

        return items, total

    async def search_with_unit(
        self,
        query: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> tuple[list[UserWithUnitSchema], int]:
        """
        Search active users (with name/CPF filter) and enrich each result
        with their most-recent unit assignment (nullable).
        """
        items, total = await self.search(
            query=query, page=page, page_size=page_size
        )
        if not items:
            return [], total

        user_ids: list[UUID] = [item.id_ for item in items]

        # For each user get the unit from their most-recent club year.
        latest_year_sq = (
            sa.select(
                UnitMemberEntity.user_id,
                sa.func.max(UnitMemberEntity.club_year_id).label("max_year"),
            )
            .where(UnitMemberEntity.user_id.in_(user_ids))
            .group_by(UnitMemberEntity.user_id)
            .subquery()
        )

        unit_stmt = (
            sa.select(
                UnitMemberEntity.user_id,
                UnitMemberEntity.unit_id,
                UnitEntity.name.label("unit_name"),
                UnitMemberEntity.role.label("unit_role"),
            )
            .join(
                latest_year_sq,
                sa.and_(
                    UnitMemberEntity.user_id == latest_year_sq.c.user_id,
                    UnitMemberEntity.club_year_id == latest_year_sq.c.max_year,
                ),
            )
            .join(UnitEntity, UnitEntity.id_ == UnitMemberEntity.unit_id)
        )

        unit_result = await self.context.execute(unit_stmt)
        unit_map: dict[UUID, tuple[UUID, str, str]] = {
            row.user_id: (row.unit_id, row.unit_name, row.unit_role)
            for row in unit_result
        }

        enriched: list[UserWithUnitSchema] = []
        for item in items:
            unit_info = unit_map.get(item.id_)
            enriched.append(
                UserWithUnitSchema(
                    **item.model_dump(),
                    unit_id=unit_info[0] if unit_info else None,
                    unit_name=unit_info[1] if unit_info else None,
                    unit_role=unit_info[2] if unit_info else None,
                )
            )

        return enriched, total
