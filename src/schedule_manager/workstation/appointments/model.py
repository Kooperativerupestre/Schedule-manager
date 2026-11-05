import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    func,
    text,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import (
    TSTZRANGE,
    UUID,
    ExcludeConstraint,
    Range,
)
from sqlalchemy.orm import Mapped, mapped_column

from schedule_manager.base_model import Base


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    SUCCESSFUL = "successful"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "NOT isempty(period) "
            "AND NOT lower_inf(period) "
            "AND NOT upper_inf(period) "
            "AND lower_inc(period) "
            "AND NOT upper_inc(period)",
            name="valid_period",
        ),
        ExcludeConstraint(
            ("workstation_id", "="),
            ("period", "&&"),
            where=text("status <> 'cancelled'"),
            name="no_overlapping_appointments",
        ),
        ForeignKeyConstraint(
            ["worker_id", "workstation_id"],
            ["workers.id", "workers.workstation_id"],
            ondelete="SET NULL (worker_id)",
            name="appointment_worker_workstation_fkey",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    made_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    maker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workstation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workstations.id", ondelete="CASCADE"),
        nullable=False,
    )
    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    period: Mapped[Range[datetime]] = mapped_column(
        TSTZRANGE,
        nullable=False,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        SqlEnum(
            AppointmentStatus,
            name="appointment_status",
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
        server_default=text("'pending'"),
    )
