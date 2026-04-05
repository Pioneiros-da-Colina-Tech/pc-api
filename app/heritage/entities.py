from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin
from app.meetings.entities import MeetingsEntity
from app.units.entities import UnitEntity

from .concepts import RequestStatusConcept


class ItemEntity(Entity, TimestampMixin, UUIDMixin):
    __tablename__ = "heritage_item"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    acquisition_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)


class RequestEntity(Entity, TimestampMixin, UUIDMixin):
    __tablename__ = "heritage_request"

    meeting_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("meetings.id"), nullable=False
    )
    unit_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("unit.id"), nullable=False
    )

    status: Mapped[RequestStatusConcept] = mapped_column(
        sa.Enum(RequestStatusConcept, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RequestStatusConcept.PENDING,
    )
    rejection_reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    meeting: Mapped[MeetingsEntity] = relationship()
    unit: Mapped[UnitEntity] = relationship()
    requested_items: Mapped[list["RequestItemEntity"]] = relationship(
        back_populates="request"
    )


class RequestItemEntity(Entity, TimestampMixin, UUIDMixin):
    __tablename__ = "heritage_request_item"

    request_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("heritage_request.id"), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("heritage_item.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    acquisition_date: Mapped[date | None] = mapped_column(
        sa.Date, nullable=True
    )
    request: Mapped[RequestEntity] = relationship(
        back_populates="requested_items"
    )
    item: Mapped[ItemEntity] = relationship()
