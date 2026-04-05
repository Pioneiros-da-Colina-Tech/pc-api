from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ScoreItemSchema(BaseModel):
    """Scores for a single user in a meeting."""

    user_id: UUID
    presenca: int = Field(ge=0, le=10)
    pontualidade: int = Field(ge=0, le=10)
    uniforme: int = Field(ge=0, le=10)
    modestia: int = Field(ge=0, le=10)


class SubmitMeetingScoresSchema(BaseModel):
    scores: list[ScoreItemSchema] = Field(min_length=1)


class MeetingScoreSchema(ScoreItemSchema):
    id_: UUID
    meeting_id: UUID
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None


class BonusScoreCreateSchema(BaseModel):
    user_id: UUID | None = None
    unit_id: UUID | None = None
    points: int = Field(examples=[10])
    description: str = Field(min_length=2, max_length=500)
    year: str = Field(examples=["2025"], min_length=4, max_length=4)
    semester: int = Field(ge=1, le=2)

    @model_validator(mode="after")
    def exactly_one_target(self) -> "BonusScoreCreateSchema":
        if (self.user_id is None) == (self.unit_id is None):
            raise ValueError("Provide exactly one of user_id or unit_id.")
        return self


class BonusScoreSchema(BonusScoreCreateSchema):
    id_: UUID
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None


# --- Ranking ---


class UserRankingEntrySchema(BaseModel):
    user_id: UUID
    name: str | None
    document: str
    unit_id: UUID | None
    unit_name: str | None
    unit_role: str | None
    presenca: int
    pontualidade: int
    uniforme: int
    modestia: int
    bonus: int
    total: int


class UnitRankingEntrySchema(BaseModel):
    unit_id: UUID
    unit_name: str
    presenca: int
    pontualidade: int
    uniforme: int
    modestia: int
    member_bonus: int
    unit_bonus: int
    total: int


class RankingResponseSchema(BaseModel):
    individual: list[UserRankingEntrySchema]
    units: list[UnitRankingEntrySchema]
