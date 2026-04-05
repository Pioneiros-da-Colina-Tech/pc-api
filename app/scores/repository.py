from datetime import UTC, date, datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.entities import UsersEntity
from app.meetings.entities import MeetingsEntity
from app.units.entities import UnitEntity, UnitMemberEntity

from .entities import BonusScoreEntity, MeetingScoreEntity
from .schemas import (
    BonusScoreCreateSchema,
    BonusScoreSchema,
    MeetingScoreSchema,
    RankingResponseSchema,
    ScoreItemSchema,
    UnitRankingEntrySchema,
    UserRankingEntrySchema,
)


class ScoreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Meeting scores
    # ------------------------------------------------------------------

    async def upsert_meeting_score(
        self, meeting_id: UUID, item: ScoreItemSchema
    ) -> MeetingScoreSchema:
        """Create or replace the score for a user in a meeting."""
        existing_stmt = sa.select(MeetingScoreEntity).where(
            MeetingScoreEntity.meeting_id == meeting_id,
            MeetingScoreEntity.user_id == item.user_id,
        )
        result = await self.session.execute(existing_stmt)
        existing = result.scalars().first()

        if existing is not None:
            update_stmt = (
                sa.update(MeetingScoreEntity)
                .where(
                    MeetingScoreEntity.meeting_id == meeting_id,
                    MeetingScoreEntity.user_id == item.user_id,
                )
                .values(
                    presenca=item.presenca,
                    pontualidade=item.pontualidade,
                    uniforme=item.uniforme,
                    modestia=item.modestia,
                    updated_at=datetime.now(UTC),
                )
                .returning(MeetingScoreEntity)
            )
            upd_result = await self.session.execute(update_stmt)
            entity = upd_result.scalars().one()
        else:
            entity = MeetingScoreEntity(
                id_=uuid4(),
                meeting_id=meeting_id,
                user_id=item.user_id,
                presenca=item.presenca,
                pontualidade=item.pontualidade,
                uniforme=item.uniforme,
                modestia=item.modestia,
                created_at=datetime.now(UTC),
                updated_at=None,
                deleted_at=None,
            )
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)

        return self._score_to_schema(entity, meeting_id)

    async def get_meeting_scores(self, meeting_id: UUID) -> list[MeetingScoreSchema]:
        stmt = sa.select(MeetingScoreEntity).where(
            MeetingScoreEntity.meeting_id == meeting_id
        )
        result = await self.session.execute(stmt)
        return [
            self._score_to_schema(e, meeting_id) for e in result.scalars().all()
        ]

    @staticmethod
    def _score_to_schema(
        entity: MeetingScoreEntity, meeting_id: UUID
    ) -> MeetingScoreSchema:
        return MeetingScoreSchema(
            id_=entity.id_,
            meeting_id=meeting_id,
            user_id=entity.user_id,
            presenca=entity.presenca,
            pontualidade=entity.pontualidade,
            uniforme=entity.uniforme,
            modestia=entity.modestia,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    # ------------------------------------------------------------------
    # Bonus scores
    # ------------------------------------------------------------------

    async def create_bonus(self, data: BonusScoreCreateSchema) -> BonusScoreSchema:
        entity = BonusScoreEntity(
            id_=uuid4(),
            user_id=data.user_id,
            unit_id=data.unit_id,
            points=data.points,
            description=data.description,
            year=data.year,
            semester=data.semester,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return self._bonus_to_schema(entity)

    async def list_bonuses(
        self, year: str, semester: int
    ) -> list[BonusScoreSchema]:
        stmt = sa.select(BonusScoreEntity).where(
            BonusScoreEntity.year == year,
            BonusScoreEntity.semester == semester,
        )
        result = await self.session.execute(stmt)
        return [self._bonus_to_schema(e) for e in result.scalars().all()]

    @staticmethod
    def _bonus_to_schema(entity: BonusScoreEntity) -> BonusScoreSchema:
        return BonusScoreSchema(
            id_=entity.id_,
            user_id=entity.user_id,
            unit_id=entity.unit_id,
            points=entity.points,
            description=entity.description,
            year=entity.year,
            semester=entity.semester,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    # ------------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------------

    async def get_ranking(
        self, year: str, semester: int
    ) -> RankingResponseSchema:
        year_int = int(year)
        if semester == 1:
            start = date(year_int, 1, 1)
            end = date(year_int, 6, 30)
        else:
            start = date(year_int, 7, 1)
            end = date(year_int, 12, 31)

        # 1 – meetings in the date range
        meetings_stmt = sa.select(MeetingsEntity.id_).where(
            sa.func.date(MeetingsEntity.date) >= start,
            sa.func.date(MeetingsEntity.date) <= end,
        )
        meeting_ids: list[UUID] = list(
            (await self.session.execute(meetings_stmt)).scalars().all()
        )

        # 2 – aggregate meeting scores per user
        user_scores: dict[UUID, dict] = {}
        if meeting_ids:
            agg_stmt = (
                sa.select(
                    MeetingScoreEntity.user_id,
                    sa.func.sum(MeetingScoreEntity.presenca).label("presenca"),
                    sa.func.sum(MeetingScoreEntity.pontualidade).label("pontualidade"),
                    sa.func.sum(MeetingScoreEntity.uniforme).label("uniforme"),
                    sa.func.sum(MeetingScoreEntity.modestia).label("modestia"),
                )
                .where(MeetingScoreEntity.meeting_id.in_(meeting_ids))
                .group_by(MeetingScoreEntity.user_id)
            )
            for row in (await self.session.execute(agg_stmt)).all():
                user_scores[row.user_id] = {
                    "presenca": int(row.presenca or 0),
                    "pontualidade": int(row.pontualidade or 0),
                    "uniforme": int(row.uniforme or 0),
                    "modestia": int(row.modestia or 0),
                }

        # 3 – user bonus totals for this period
        user_bonus: dict[UUID, int] = {}
        bonus_stmt = sa.select(BonusScoreEntity).where(
            BonusScoreEntity.year == year,
            BonusScoreEntity.semester == semester,
            BonusScoreEntity.user_id.isnot(None),
        )
        for row in (await self.session.execute(bonus_stmt)).scalars():
            user_bonus[row.user_id] = user_bonus.get(row.user_id, 0) + row.points

        # 4 – unit bonus totals for this period
        unit_bonus: dict[UUID, int] = {}
        unit_bonus_stmt = sa.select(BonusScoreEntity).where(
            BonusScoreEntity.year == year,
            BonusScoreEntity.semester == semester,
            BonusScoreEntity.unit_id.isnot(None),
        )
        for row in (await self.session.execute(unit_bonus_stmt)).scalars():
            unit_bonus[row.unit_id] = unit_bonus.get(row.unit_id, 0) + row.points

        # 5 – unit membership for this year (use year as club_year_id)
        user_unit: dict[UUID, tuple[UUID, str, str]] = {}  # user_id → (unit_id, unit_name, unit_role)
        membership_stmt = (
            sa.select(
                UnitMemberEntity.user_id,
                UnitMemberEntity.unit_id,
                UnitMemberEntity.role.label("unit_role"),
                UnitEntity.name.label("unit_name"),
            )
            .join(UnitEntity, UnitEntity.id_ == UnitMemberEntity.unit_id)
            .where(UnitMemberEntity.club_year_id == year)
        )
        for row in (await self.session.execute(membership_stmt)).all():
            user_unit[row.user_id] = (row.unit_id, row.unit_name, row.unit_role)

        # 6 – user details for all users that appear in scores or bonuses
        all_user_ids = set(user_scores) | set(user_bonus)
        user_info: dict[UUID, tuple[str | None, str]] = {}  # user_id → (name, document)
        if all_user_ids:
            users_stmt = sa.select(
                UsersEntity.id_, UsersEntity.name, UsersEntity.document
            ).where(UsersEntity.id_.in_(all_user_ids))
            for row in (await self.session.execute(users_stmt)).all():
                user_info[row.id_] = (row.name, row.document)

        # 7 – build individual ranking
        individual: list[UserRankingEntrySchema] = []
        for uid in all_user_ids:
            scores = user_scores.get(uid, {"presenca": 0, "pontualidade": 0, "uniforme": 0, "modestia": 0})
            bonus = user_bonus.get(uid, 0)
            info = user_info.get(uid, (None, str(uid)))
            unit = user_unit.get(uid)
            meeting_total = scores["presenca"] + scores["pontualidade"] + scores["uniforme"] + scores["modestia"]
            individual.append(
                UserRankingEntrySchema(
                    user_id=uid,
                    name=info[0],
                    document=info[1],
                    unit_id=unit[0] if unit else None,
                    unit_name=unit[1] if unit else None,
                    unit_role=unit[2] if unit else None,
                    presenca=scores["presenca"],
                    pontualidade=scores["pontualidade"],
                    uniforme=scores["uniforme"],
                    modestia=scores["modestia"],
                    bonus=bonus,
                    total=meeting_total + bonus,
                )
            )
        individual.sort(key=lambda e: e.total, reverse=True)

        # 8 – build unit ranking
        units_data: dict[UUID, dict] = {}
        for entry in individual:
            if entry.unit_id is None:
                continue
            uid_unit = entry.unit_id
            if uid_unit not in units_data:
                units_data[uid_unit] = {
                    "unit_name": entry.unit_name,
                    "presenca": 0,
                    "pontualidade": 0,
                    "uniforme": 0,
                    "modestia": 0,
                    "member_bonus": 0,
                }
            units_data[uid_unit]["presenca"] += entry.presenca
            units_data[uid_unit]["pontualidade"] += entry.pontualidade
            units_data[uid_unit]["uniforme"] += entry.uniforme
            units_data[uid_unit]["modestia"] += entry.modestia
            units_data[uid_unit]["member_bonus"] += entry.bonus

        # include units that only have unit-level bonuses
        for u_id, pts in unit_bonus.items():
            if u_id not in units_data:
                unit_name_stmt = sa.select(UnitEntity.name).where(UnitEntity.id_ == u_id)
                name_row = (await self.session.execute(unit_name_stmt)).scalar_one_or_none()
                if name_row:
                    units_data[u_id] = {
                        "unit_name": name_row,
                        "presenca": 0,
                        "pontualidade": 0,
                        "uniforme": 0,
                        "modestia": 0,
                        "member_bonus": 0,
                    }

        units: list[UnitRankingEntrySchema] = []
        for u_id, data in units_data.items():
            ub = unit_bonus.get(u_id, 0)
            meeting_total = data["presenca"] + data["pontualidade"] + data["uniforme"] + data["modestia"]
            units.append(
                UnitRankingEntrySchema(
                    unit_id=u_id,
                    unit_name=data["unit_name"],
                    presenca=data["presenca"],
                    pontualidade=data["pontualidade"],
                    uniforme=data["uniforme"],
                    modestia=data["modestia"],
                    member_bonus=data["member_bonus"],
                    unit_bonus=ub,
                    total=meeting_total + data["member_bonus"] + ub,
                )
            )
        units.sort(key=lambda e: e.total, reverse=True)

        return RankingResponseSchema(individual=individual, units=units)
