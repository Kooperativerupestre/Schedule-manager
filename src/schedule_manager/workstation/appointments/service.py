from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.repository import UnitRepository
from schedule_manager.workstation.appointments.errors import (
    AppointmentWorkerNotFoundError,
)
from schedule_manager.workstation.appointments.model import AppointmentStatus
from schedule_manager.workstation.appointments.repository import (
    AppointmentRepository,
)
from schedule_manager.workstation.appointments.schema_translator import (
    AppointmentSchemaTranslator,
)
from schedule_manager.workstation.appointments.schemas import (
    AppointmentActionResult,
    AppointmentAdd,
    AppointmentResponse,
)
from schedule_manager.workstation.repository import WorkstationRepository
from schedule_manager.workstation.workers.repository import WorkerRepository


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
        worker = (
            await WorkerRepository.get(
                session,
                appointment.workstation_id,
                appointment.worker_id,
            )
            if appointment.worker_id is not None
            else None
        )
        if worker is None:
            raise AppointmentWorkerNotFoundError(
                "Worker does not belong to the appointment workstation."
            )
        model = AppointmentSchemaTranslator.to_model(appointment)
        return await AppointmentRepository.create(session, model)

    @staticmethod
    async def delete(
        session: AsyncSession,
        appointment_id: UUID,
    ) -> bool:
        return await AppointmentRepository.delete(session, appointment_id)

    @staticmethod
    async def cancel(
        session: AsyncSession,
        appointment_id: UUID,
        requester_id: UUID,
    ) -> AppointmentActionResult:
        appointment = await AppointmentRepository.get(session, appointment_id)
        if appointment is None:
            return AppointmentActionResult.NOT_FOUND
        worker = (
            await WorkerRepository.get(
                session,
                appointment.workstation_id,
                appointment.worker_id,
            )
            if appointment.worker_id is not None
            else None
        )
        is_maker = appointment.maker_id == requester_id
        is_assigned_worker = worker is not None and worker.user_id == requester_id
        workstation = await WorkstationRepository.get(
            session,
            appointment.workstation_id,
        )
        is_unit_owner = workstation is not None and await UnitRepository.is_owner(
            session,
            workstation.unit_id,
            requester_id,
        )
        if not (is_maker or is_assigned_worker or is_unit_owner):
            return AppointmentActionResult.FORBIDDEN
        return await AppointmentService._transition(
            session,
            appointment_id,
            AppointmentStatus.CANCELLED,
            AppointmentActionResult.CANCELLED,
        )

    @staticmethod
    async def complete(
        session: AsyncSession,
        appointment_id: UUID,
        worker_user_id: UUID,
    ) -> AppointmentActionResult:
        appointment = await AppointmentRepository.get(session, appointment_id)
        if appointment is None:
            return AppointmentActionResult.NOT_FOUND
        if appointment.worker_id is None:
            return AppointmentActionResult.FORBIDDEN
        worker = await WorkerRepository.get(
            session,
            appointment.workstation_id,
            appointment.worker_id,
        )
        if worker is None or worker.user_id != worker_user_id:
            return AppointmentActionResult.FORBIDDEN
        return await AppointmentService._transition(
            session,
            appointment_id,
            AppointmentStatus.SUCCESSFUL,
            AppointmentActionResult.COMPLETED,
        )

    @staticmethod
    async def _transition(
        session: AsyncSession,
        appointment_id: UUID,
        status: AppointmentStatus,
        success_result: AppointmentActionResult,
    ) -> AppointmentActionResult:
        if await AppointmentRepository.set_status_if_pending(
            session,
            appointment_id,
            status,
        ):
            return success_result
        appointment = await AppointmentRepository.get(session, appointment_id)
        if appointment is None:
            return AppointmentActionResult.NOT_FOUND
        if appointment.status == AppointmentStatus.CANCELLED:
            return AppointmentActionResult.ALREADY_CANCELLED
        if appointment.status == AppointmentStatus.SUCCESSFUL:
            return AppointmentActionResult.ALREADY_COMPLETED
        raise RuntimeError("Appointment status transition failed unexpectedly.")
