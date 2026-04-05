from datetime import UTC, datetime
from typing import override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.heritage.concepts import RequestStatusConcept
from app.heritage.entities import (
    HeritageItemEntity,
    HeritageRequestEntity,
    HeritageRequestItemEntity,
)
from app.heritage.schemas import (
    CreateItemSchema,
    CreateRequestSchema,
    HeritageItemSchema,
    HeritageRequestItemSchema,
    HeritageRequestSchema,
    ItemPageSchema,
    ItemSummarySchema,
    UpdateItemSchema,
    UpdateRequestStatusSchema,
)
from app.infra.database.repository import Repository


class ItemRepository(Repository[HeritageItemEntity, HeritageItemSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=HeritageItemEntity)

    @override
    def to_schema(self, entity: HeritageItemEntity) -> HeritageItemSchema:
        return HeritageItemSchema(
            id_=entity.id_,
            name=entity.name,
            quantity=entity.quantity,
            acquisition_date=entity.acquisition_date,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    @override
    def to_entity(self, schema: HeritageItemSchema) -> HeritageItemEntity:
        return HeritageItemEntity(
            id_=schema.id_,
            name=schema.name,
            quantity=schema.quantity,
            acquisition_date=schema.acquisition_date,
            description=schema.description,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    async def create_item(self, data: CreateItemSchema) -> HeritageItemSchema:
        entity = HeritageItemEntity(
            id_=uuid4(),
            name=data.name,
            quantity=data.quantity,
            acquisition_date=data.acquisition_date,
            description=data.description,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        self.context.add(entity)
        await self.context.flush()
        await self.context.refresh(entity)
        return self.to_schema(entity)

    async def list_items_paginated(
        self,
        name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ItemPageSchema:
        # Subquery: committed quantities from active requests
        active_statuses = [
            RequestStatusConcept.PENDING,
            RequestStatusConcept.APPROVED,
            RequestStatusConcept.DELIVERED,
        ]
        committed_sq = (
            sa.select(
                HeritageRequestItemEntity.item_id,
                sa.func.coalesce(
                    sa.func.sum(HeritageRequestItemEntity.quantity), 0
                ).label("committed"),
            )
            .join(
                HeritageRequestEntity,
                HeritageRequestItemEntity.request_id
                == HeritageRequestEntity.id_,
            )
            .where(
                HeritageRequestEntity.status.in_(active_statuses),
                HeritageRequestItemEntity.deleted_at.is_(None),
                HeritageRequestEntity.deleted_at.is_(None),
            )
            .group_by(HeritageRequestItemEntity.item_id)
            .subquery()
        )

        base_where = [HeritageItemEntity.deleted_at.is_(None)]
        if name:
            base_where.append(HeritageItemEntity.name.ilike(f"%{name}%"))

        count_stmt = (
            sa.select(sa.func.count())
            .select_from(HeritageItemEntity)
            .where(*base_where)
        )
        total = (await self.context.execute(count_stmt)).scalar_one()

        offset = (page - 1) * page_size
        stmt = (
            sa.select(
                HeritageItemEntity,
                sa.func.coalesce(committed_sq.c.committed, 0).label(
                    "committed"
                ),
            )
            .outerjoin(
                committed_sq, HeritageItemEntity.id_ == committed_sq.c.item_id
            )
            .where(*base_where)
            .order_by(HeritageItemEntity.name)
            .offset(offset)
            .limit(page_size)
        )
        rows = (await self.context.execute(stmt)).all()
        items = [
            ItemSummarySchema(
                **self.to_schema(row[0]).model_dump(),
                committed_quantity=row[1],
                available_quantity=max(0, row[0].quantity - row[1]),
            )
            for row in rows
        ]
        return ItemPageSchema(
            items=items, total=total, page=page, page_size=page_size
        )

    async def update_item(
        self, item_id: UUID, data: UpdateItemSchema
    ) -> HeritageItemSchema:
        updates: dict = data.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.now(UTC)
        stmt = (
            sa.update(HeritageItemEntity)
            .where(
                HeritageItemEntity.id_ == item_id,
                HeritageItemEntity.deleted_at.is_(None),
            )
            .values(**updates)
            .returning(HeritageItemEntity)
        )
        result = await self.context.execute(stmt)
        updated = result.scalars().first()
        if updated is None:
            from app.api.exc import does_not_exist

            raise does_not_exist("Item")
        return self.to_schema(updated)


class RequestRepository:
    def __init__(self, session: AsyncSession):
        self.context = session

    def _to_schema(
        self, entity: HeritageRequestEntity
    ) -> HeritageRequestSchema:
        return HeritageRequestSchema(
            id_=entity.id_,
            meeting_id=entity.meeting_id,
            unit_id=entity.unit_id,
            status=entity.status,
            rejection_reason=entity.rejection_reason,
            items=[
                HeritageRequestItemSchema(
                    id_=ri.id_,
                    request_id=ri.request_id,
                    item_id=ri.item_id,
                    quantity=ri.quantity,
                    acquisition_date=ri.acquisition_date,
                    item_name=ri.item.name if ri.item else None,
                )
                for ri in (entity.requested_items or [])
                if ri.deleted_at is None
            ],
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_request(
        self, data: CreateRequestSchema
    ) -> HeritageRequestSchema:
        request = HeritageRequestEntity(
            id_=uuid4(),
            meeting_id=data.meeting_id,
            unit_id=data.unit_id,
            status=RequestStatusConcept.PENDING,
            rejection_reason=None,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        self.context.add(request)
        await self.context.flush()

        for item_data in data.items:
            request_item = HeritageRequestItemEntity(
                id_=uuid4(),
                request_id=request.id_,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                acquisition_date=item_data.acquisition_date,
                created_at=datetime.now(UTC),
                updated_at=None,
                deleted_at=None,
            )
            self.context.add(request_item)

        await self.context.flush()

        stmt = (
            sa.select(HeritageRequestEntity)
            .options(
                selectinload(
                    HeritageRequestEntity.requested_items
                ).selectinload(HeritageRequestItemEntity.item)
            )
            .where(HeritageRequestEntity.id_ == request.id_)
        )
        result = await self.context.execute(stmt)
        full = result.scalar_one()
        return self._to_schema(full)

    async def list_requests(
        self, unit_id: UUID | None = None
    ) -> list[HeritageRequestSchema]:
        stmt = (
            sa.select(HeritageRequestEntity)
            .options(
                selectinload(
                    HeritageRequestEntity.requested_items
                ).selectinload(HeritageRequestItemEntity.item)
            )
            .where(HeritageRequestEntity.deleted_at.is_(None))
        )
        if unit_id is not None:
            stmt = stmt.where(HeritageRequestEntity.unit_id == unit_id)
        result = await self.context.execute(stmt)
        return [self._to_schema(e) for e in result.scalars().all()]

    async def get_request(
        self, request_id: UUID
    ) -> HeritageRequestSchema | None:
        stmt = (
            sa.select(HeritageRequestEntity)
            .options(
                selectinload(
                    HeritageRequestEntity.requested_items
                ).selectinload(HeritageRequestItemEntity.item)
            )
            .where(
                HeritageRequestEntity.id_ == request_id,
                HeritageRequestEntity.deleted_at.is_(None),
            )
        )
        result = await self.context.execute(stmt)
        entity = result.scalar_one_or_none()
        return self._to_schema(entity) if entity else None

    async def update_status(
        self, request_id: UUID, data: UpdateRequestStatusSchema
    ) -> HeritageRequestSchema | None:
        stmt = (
            sa.update(HeritageRequestEntity)
            .where(
                HeritageRequestEntity.id_ == request_id,
                HeritageRequestEntity.deleted_at.is_(None),
            )
            .values(
                status=data.status,
                rejection_reason=data.rejection_reason,
                updated_at=datetime.now(UTC),
            )
        )
        _ = await self.context.execute(stmt)
        return await self.get_request(request_id)
