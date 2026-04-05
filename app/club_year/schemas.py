from datetime import datetime

from pydantic import BaseModel, Field


class CreateClubYearSchema(BaseModel):
    id_: str = Field(examples=["2024"], min_length=1, max_length=20)


class ClubYearSchema(CreateClubYearSchema):
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
