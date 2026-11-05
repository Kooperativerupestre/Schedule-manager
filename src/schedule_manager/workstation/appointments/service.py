from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.appointments.repository import (
    AppointmentRepository,
)
from schedule_manager.workstation.appointments.schema_translator import (
    AppointmentSchemaTranslator,
)
from schedule_manager.workstation.appointments.schemas import (
    AppointmentAdd,
    AppointmentResponse,
)


class AppointmentService:
    @staticmethod
    async def get(
        session: AsyncSession,
        appointment_id: UUID,
    ) -> AppointmentResponse | None:
        appointment = await AppointmentRepository.get(session, appointment_id)
        if appointment is None:
            return None
        return AppointmentSchemaTranslator.to_response(appointment)

    @staticmethod
    async def get_in_range(
        session: AsyncSession,
        workstation_id: UUID,
        begin_at: datetime,
        end_at: datetime,
    ) -> list[AppointmentResponse]:
        period = AppointmentSchemaTranslator.to_range(begin_at, end_at)
        appointments = await AppointmentRepository.get_in_range(
            session,
            workstation_id,
            period,
        )
        return [
            AppointmentSchemaTranslator.to_response(appointment)
            for appointment in appointments
        ]

    @staticmethod
    async def can_schedule(
        session: AsyncSession,
        workstation_id: UUID,
        begin_at: datetime,
        end_at: datetime,
    ) -> bool:
        period = AppointmentSchemaTranslator.to_range(begin_at, end_at)
        return not await AppointmentRepository.has_overlap(
            session,
            workstation_id,
            period,
        )

    @staticmethod
    async def create(
        session: AsyncSession,
        appointment: AppointmentAdd,
    ) -> bool:
        model = AppointmentSchemaTranslator.to_model(appointment)
        return await AppointmentRepository.create(session, model)

    @staticmethod
    async def delete(
        session: AsyncSession,
        appointment_id: UUID,
    ) -> bool:
        return await AppointmentRepository.delete(session, appointment_id)
