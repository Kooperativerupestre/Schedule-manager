from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.appointments.model import (
    Appointment,
    AppointmentStatus,
)


class AppointmentRepository:
    @staticmethod
    async def get(
        session: AsyncSession,
        appointment_id: UUID,
    ) -> Appointment | None:
        return await session.scalar(
            select(Appointment).where(Appointment.id == appointment_id)
        )

    @staticmethod
    async def get_in_range(
        session: AsyncSession,
        workstation_id: UUID,
        period: Range[datetime],
    ) -> list[Appointment]:
        result = await session.scalars(
            select(Appointment)
            .where(
                Appointment.workstation_id == workstation_id,
                Appointment.period.op("&&")(period),
            )
            .order_by(Appointment.period)
        )
        return list(result)

    @staticmethod
    async def has_overlap(
        session: AsyncSession,
        workstation_id: UUID,
        period: Range[datetime],
    ) -> bool:
        statement = select(
            select(Appointment.id)
            .where(
                Appointment.workstation_id == workstation_id,
                Appointment.period.op("&&")(period),
                Appointment.status != AppointmentStatus.CANCELLED,
            )
            .exists()
        )
        return bool(await session.scalar(statement))

    @staticmethod
    async def create(
        session: AsyncSession,
        appointment: Appointment,
    ) -> bool:
        try:
            async with session.begin_nested():
                session.add(appointment)
                await session.flush()
        except IntegrityError as error:
            diagnostic = getattr(error.orig, "diag", None)
            if (
                getattr(diagnostic, "constraint_name", None)
                == "no_overlapping_appointments"
            ):
                return False
            raise
        return True

    @staticmethod
    async def delete(
        session: AsyncSession,
        appointment_id: UUID,
    ) -> bool:
        statement = (
            delete(Appointment)
            .where(Appointment.id == appointment_id)
            .returning(Appointment.id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def set_status_if_pending(
        session: AsyncSession,
        appointment_id: UUID,
        status: AppointmentStatus,
    ) -> bool:
        statement = (
            update(Appointment)
            .where(
                Appointment.id == appointment_id,
                Appointment.status == AppointmentStatus.PENDING,
            )
            .values(status=status)
            .returning(Appointment.id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
