from datetime import UTC, datetime
from typing import override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.heritage.concepts import RequestStatusConcept
from app.heritage.entities import ItemEntity, RequestEntity, RequestItemEntity
from app.heritage.schemas import (
    CreateItemSchema,
    CreateRequestSchema,
    ItemPageSchema,
    ItemSchema,
    ItemSummarySchema,
    RequestItemSchema,
    RequestSchema,
    UpdateItemSchema,
    UpdateRequestStatusSchema,
)
from app.infra.database.repository import Repository


class ItemRepository(Repository[ItemEntity, ItemSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=ItemEntity)

    @override
    def to_schema(self, entity: ItemEntity) -> ItemSchema:
        return ItemSchema(
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
    def to_entity(self, schema: ItemSchema) -> ItemEntity:
        return ItemEntity(
            id_=schema.id_,
            name=schema.name,
            quantity=schema.quantity,
            acquisition_date=schema.acquisition_date,
            description=schema.description,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    async def create_item(self, data: CreateItemSchema) -> ItemSchema:
        entity = ItemEntity(
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
                RequestItemEntity.item_id,
                sa.func.coalesce(
                    sa.func.sum(RequestItemEntity.quantity), 0
                ).label("committed"),
            )
            .join(
                RequestEntity, RequestItemEntity.request_id == RequestEntity.id_
            )
            .where(
                RequestEntity.status.in_(active_statuses),
                RequestItemEntity.deleted_at.is_(None),
                RequestEntity.deleted_at.is_(None),
            )
            .group_by(RequestItemEntity.item_id)
            .subquery()
        )

        base_where = [ItemEntity.deleted_at.is_(None)]
        if name:
            base_where.append(ItemEntity.name.ilike(f"%{name}%"))

        count_stmt = (
            sa.select(sa.func.count())
            .select_from(ItemEntity)
            .where(*base_where)
        )
        total = (await self.context.execute(count_stmt)).scalar_one()

        offset = (page - 1) * page_size
        stmt = (
            sa.select(
                ItemEntity,
                sa.func.coalesce(committed_sq.c.committed, 0).label(
                    "committed"
                ),
            )
            .outerjoin(committed_sq, ItemEntity.id_ == committed_sq.c.item_id)
            .where(*base_where)
            .order_by(ItemEntity.name)
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
    ) -> ItemSchema:
        updates: dict = data.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.now(UTC)
        stmt = (
            sa.update(ItemEntity)
            .where(ItemEntity.id_ == item_id, ItemEntity.deleted_at.is_(None))
            .values(**updates)
            .returning(ItemEntity)
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

    def _to_schema(self, entity: RequestEntity) -> RequestSchema:
        return RequestSchema(
            id_=entity.id_,
            meeting_id=entity.meeting_id,
            unit_id=entity.unit_id,
            status=entity.status,
            rejection_reason=entity.rejection_reason,
            items=[
                RequestItemSchema(
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

    async def create_request(self, data: CreateRequestSchema) -> RequestSchema:
        request = RequestEntity(
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
            request_item = RequestItemEntity(
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
            sa.select(RequestEntity)
            .options(
                selectinload(RequestEntity.requested_items).selectinload(
                    RequestItemEntity.item
                )
            )
            .where(RequestEntity.id_ == request.id_)
        )
        result = await self.context.execute(stmt)
        full = result.scalar_one()
        return self._to_schema(full)

    async def list_requests(
        self, unit_id: UUID | None = None
    ) -> list[RequestSchema]:
        stmt = (
            sa.select(RequestEntity)
            .options(
                selectinload(RequestEntity.requested_items).selectinload(
                    RequestItemEntity.item
                )
            )
            .where(RequestEntity.deleted_at.is_(None))
        )
        if unit_id is not None:
            stmt = stmt.where(RequestEntity.unit_id == unit_id)
        result = await self.context.execute(stmt)
        return [self._to_schema(e) for e in result.scalars().all()]

    async def get_request(self, request_id: UUID) -> RequestSchema | None:
        stmt = (
            sa.select(RequestEntity)
            .options(
                selectinload(RequestEntity.requested_items).selectinload(
                    RequestItemEntity.item
                )
            )
            .where(
                RequestEntity.id_ == request_id,
                RequestEntity.deleted_at.is_(None),
            )
        )
        result = await self.context.execute(stmt)
        entity = result.scalar_one_or_none()
        return self._to_schema(entity) if entity else None

    async def update_status(
        self, request_id: UUID, data: UpdateRequestStatusSchema
    ) -> RequestSchema | None:
        stmt = (
            sa.update(RequestEntity)
            .where(
                RequestEntity.id_ == request_id,
                RequestEntity.deleted_at.is_(None),
            )
            .values(
                status=data.status,
                rejection_reason=data.rejection_reason,
                updated_at=datetime.now(UTC),
            )
        )
        _ = await self.context.execute(stmt)
        return await self.get_request(request_id)
