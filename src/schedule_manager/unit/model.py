import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from schedule_manager.base_model import Base


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )


class UnitOwner(Base):
    __tablename__ = "unit_owners"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="CASCADE"),
        primary_key=True,
    )
    begin_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "unit_id"],
            ["unit_members.user_id", "unit_members.unit_id"],
            ondelete="CASCADE",
        ),
    )
