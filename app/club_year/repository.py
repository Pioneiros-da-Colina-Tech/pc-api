from datetime import UTC, datetime
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.repository import Repository

from .entities import ClubYearEntity
from .schemas import ClubYearSchema, CreateClubYearSchema


class ClubYearRepository(Repository[ClubYearEntity, ClubYearSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=ClubYearEntity)

    @override
    def to_entity(self, schema: ClubYearSchema) -> ClubYearEntity:
        return ClubYearEntity(
            id_=schema.id_,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: ClubYearEntity) -> ClubYearSchema:
        return ClubYearSchema(
            id_=entity.id_,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_club_year(
        self, data: CreateClubYearSchema
    ) -> ClubYearSchema:
        club_year = ClubYearSchema(
            id_=data.id_,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(club_year)
