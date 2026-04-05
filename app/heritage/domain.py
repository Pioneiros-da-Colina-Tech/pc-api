from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import does_not_exist
from app.api.schemas import BaseResponseSchema
from app.heritage.repository import ItemRepository, RequestRepository
from app.heritage.schemas import (
    CreateItemSchema,
    CreateRequestSchema,
    UpdateItemSchema,
    UpdateRequestStatusSchema,
)


@dataclass
class ListItemsUseCase(ApiDomain):
    session: AsyncSession
    name: str | None = None
    page: int = 1
    page_size: int = 20

    @cached_property
    def repo(self) -> ItemRepository:
        return ItemRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        page = await self.repo.list_items_paginated(
            name=self.name, page=self.page, page_size=self.page_size
        )
        return BaseResponseSchema(
            message="Items retrieved successfully", data=page
        )


@dataclass
class CreateItemUseCase(ApiDomain):
    payload: CreateItemSchema
    session: AsyncSession

    @cached_property
    def repo(self) -> ItemRepository:
        return ItemRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        item = await self.repo.create_item(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Item created successfully",
            data=item,
        )


@dataclass
class UpdateItemUseCase(ApiDomain):
    item_id: UUID
    payload: UpdateItemSchema
    session: AsyncSession

    @cached_property
    def repo(self) -> ItemRepository:
        return ItemRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        item = await self.repo.update_item(self.item_id, self.payload)
        return BaseResponseSchema(message="Item updated successfully", data=item)


@dataclass
class DeleteItemUseCase(ApiDomain):
    item_id: UUID
    session: AsyncSession

    @cached_property
    def repo(self) -> ItemRepository:
        return ItemRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        await self.repo.delete(id_=self.item_id)
        return BaseResponseSchema(
            message="Item deleted successfully", data=None
        )


@dataclass
class CreateRequestUseCase(ApiDomain):
    payload: CreateRequestSchema
    session: AsyncSession

    @cached_property
    def item_repo(self) -> ItemRepository:
        return ItemRepository(self.session)

    @cached_property
    def request_repo(self) -> RequestRepository:
        return RequestRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        for item_data in self.payload.items:
            if not await self.item_repo.exists(id_=item_data.item_id):
                raise does_not_exist(f"Item '{item_data.item_id}'")

        result = await self.request_repo.create_request(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Request created successfully",
            data=result,
        )


@dataclass
class ListRequestsUseCase(ApiDomain):
    unit_id: UUID | None
    session: AsyncSession

    @cached_property
    def repo(self) -> RequestRepository:
        return RequestRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        requests = await self.repo.list_requests(unit_id=self.unit_id)
        return BaseResponseSchema(
            message="Requests retrieved successfully", data=requests
        )


@dataclass
class UpdateRequestStatusUseCase(ApiDomain):
    request_id: UUID
    payload: UpdateRequestStatusSchema
    session: AsyncSession

    @cached_property
    def repo(self) -> RequestRepository:
        return RequestRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repo.update_status(self.request_id, self.payload)
        if result is None:
            raise does_not_exist("Request")
        return BaseResponseSchema(
            message="Request status updated successfully", data=result
        )
