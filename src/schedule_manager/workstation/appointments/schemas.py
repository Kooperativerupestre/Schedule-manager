from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from schedule_manager.workstation.appointments.model import AppointmentStatus


class AppointmentTimeRange(BaseModel):
    begin_at: datetime
    end_at: datetime

    @field_validator("begin_at", "end_at")
    @classmethod
    def convert_to_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime values must include a UTC timezone.")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_period(self) -> AppointmentTimeRange:
        if self.end_at <= self.begin_at:
            raise ValueError("Appointment end must be after its start.")
        return self


class AppointmentAdd(AppointmentTimeRange):
    workstation_id: UUID
    maker_id: UUID


class AppointmentCreateResponse(BaseModel):
    created: bool


class AppointmentAvailabilityResponse(BaseModel):
    can_schedule: bool


class AppointmentResponse(AppointmentTimeRange):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workstation_id: UUID
    maker_id: UUID
    made_at: datetime
    status: AppointmentStatus

    @field_validator("made_at")
    @classmethod
    def convert_made_at_to_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime values must include a UTC timezone.")
        return value.astimezone(UTC)
