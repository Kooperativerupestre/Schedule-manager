from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import Range

from schedule_manager.workstation.appointments.model import Appointment
from schedule_manager.workstation.appointments.schemas import (
    AppointmentAdd,
    AppointmentResponse,
    AppointmentTimeRange,
)


class AppointmentSchemaTranslator:
    @staticmethod
    def to_model(appointment: AppointmentAdd) -> Appointment:
        return Appointment(
            workstation_id=appointment.workstation_id,
            maker_id=appointment.maker_id,
            period=Range(
                appointment.begin_at,
                appointment.end_at,
                bounds="[)",
            ),
        )

    @staticmethod
    def to_range(
        begin_at: datetime,
        end_at: datetime,
    ) -> Range[datetime]:
        period = AppointmentTimeRange(
            begin_at=begin_at,
            end_at=end_at,
        )
        return Range(period.begin_at, period.end_at, bounds="[)")

    @staticmethod
    def to_response(appointment: Appointment) -> AppointmentResponse:
        begin_at = appointment.period.lower
        end_at = appointment.period.upper
        if begin_at is None or end_at is None:
            raise ValueError("Persisted appointment periods must be finite.")
        return AppointmentResponse(
            id=appointment.id,
            workstation_id=appointment.workstation_id,
            maker_id=appointment.maker_id,
            made_at=appointment.made_at.astimezone(UTC),
            begin_at=begin_at,
            end_at=end_at,
            status=appointment.status,
        )
