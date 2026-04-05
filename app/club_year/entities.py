from app.infra.database.entities import Entity, TimestampMixin, VarCharMixin


class ClubYearEntity(Entity, TimestampMixin, VarCharMixin):
    """Represents a club year (e.g. '2024'). Uses a readable string as PK."""
