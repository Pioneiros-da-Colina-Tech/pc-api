from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .concepts import RequestStatusConcept


class CreateItemSchema(BaseModel):
    name: str = Field(
        examples=["Barraca Iglú 4 Pessoas"], min_length=2, max_length=150
    )
    quantity: int = Field(examples=[5], ge=0)
    acquisition_date: date = Field(examples=[date(2023, 3, 15)])
    description: str | None = Field(default=None, examples=["Modelo Mor"])


class ItemSchema(CreateItemSchema):
    id_: UUID = Field(examples=[UUID("223e4567-e89b-12d3-a456-426614174001")])
    created_at: datetime = Field(examples=[datetime(2023, 1, 1)])
    updated_at: datetime | None = Field(examples=[None])
    deleted_at: datetime | None = Field(examples=[None])


class CreateRequestItemSchema(BaseModel):
    item_id: UUID = Field(
        examples=[UUID("223e4567-e89b-12d3-a456-426614174001")]
    )
    quantity: int = Field(examples=[2], gt=0)
    acquisition_date: date | None = Field(
        default=None, examples=[date(2023, 3, 15)]
    )


class RequestItemSchema(CreateRequestItemSchema):
    id_: UUID = Field(examples=[UUID("323e4567-e89b-12d3-a456-426614174002")])
    request_id: UUID = Field(
        examples=[UUID("423e4567-e89b-12d3-a456-426614174003")]
    )
    item_name: str | None = Field(
        default=None, examples=["Barraca Iglú 4 Pessoas"]
    )


class CreateRequestSchema(BaseModel):
    meeting_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    unit_id: UUID = Field(
        examples=[UUID("923e4567-e89b-12d3-a456-426614174009")]
    )
    items: list[CreateRequestItemSchema]


class UpdateItemSchema(BaseModel):
    name: str | None = Field(
        default=None, examples=["Barraca Iglú 4 Pessoas"], min_length=2, max_length=150
    )
    quantity: int | None = Field(default=None, examples=[5], ge=0)
    acquisition_date: date | None = Field(default=None, examples=[date(2023, 3, 15)])
    description: str | None = Field(default=None, examples=["Modelo Mor"])


class ItemSummarySchema(ItemSchema):
    committed_quantity: int = Field(
        examples=[2], description="Quantity committed in active requests"
    )
    available_quantity: int = Field(
        examples=[3], description="Total quantity minus committed"
    )


class ItemPageSchema(BaseModel):
    items: list[ItemSummarySchema]
    total: int
    page: int
    page_size: int


class UpdateRequestStatusSchema(BaseModel):
    status: RequestStatusConcept = Field(
        examples=[RequestStatusConcept.APPROVED]
    )
    rejection_reason: str | None = Field(
        default=None,
        examples=["Quantidade de barracas indisponível para a data."],
    )


class RequestSchema(BaseModel):
    id_: UUID = Field(examples=[UUID("423e4567-e89b-12d3-a456-426614174003")])
    meeting_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    unit_id: UUID = Field(
        examples=[UUID("923e4567-e89b-12d3-a456-426614174009")]
    )
    status: RequestStatusConcept = Field(
        examples=[RequestStatusConcept.PENDING]
    )
    rejection_reason: str | None = Field(default=None)
    items: list[RequestItemSchema]

    created_at: datetime = Field(examples=[datetime(2023, 1, 1)])
    updated_at: datetime | None = Field(examples=[None])
    deleted_at: datetime | None = Field(examples=[None])
