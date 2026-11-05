from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from schedule_manager.auth.dependencies import get_current_user
from schedule_manager.database.connection import get_session
from schedule_manager.main import app
from schedule_manager.workstation.appointments.schemas import (
    AppointmentActionResult,
    AppointmentAdd,
    AppointmentResponse,
    AppointmentStatus,
)
from schedule_manager.workstation.appointments.service import AppointmentService
from schedule_manager.workstation.service import WorkstationService

WORKSTATION_ID = UUID("00000000-0000-0000-0000-000000000001")
APPOINTMENT_ID = UUID("00000000-0000-0000-0000-000000000002")
USER_ID = UUID("00000000-0000-0000-0000-000000000003")
WORKER_ID = UUID("00000000-0000-0000-0000-000000000004")
BEGIN_AT = datetime(2030, 1, 1, 9, tzinfo=UTC)
END_AT = BEGIN_AT + timedelta(hours=1)


@pytest.fixture
def appointment_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient]:
    async def current_user() -> SimpleNamespace:
        return SimpleNamespace(id=USER_ID)

    async def session() -> None:
        return None

    async def workstation_access(*args: object) -> SimpleNamespace:
        return SimpleNamespace(id=WORKSTATION_ID)

    monkeypatch.setitem(app.dependency_overrides, get_current_user, current_user)
    monkeypatch.setitem(app.dependency_overrides, get_session, session)
    monkeypatch.setattr(
        WorkstationService,
        "get",
        staticmethod(workstation_access),
    )
    with TestClient(app) as client:
        yield client


def _response() -> AppointmentResponse:
    return AppointmentResponse(
        id=APPOINTMENT_ID,
        workstation_id=WORKSTATION_ID,
        worker_id=WORKER_ID,
        maker_id=USER_ID,
        made_at=BEGIN_AT,
        begin_at=BEGIN_AT,
        end_at=END_AT,
        status=AppointmentStatus.PENDING,
    )


def test_create_appointment_uses_authenticated_user_and_returns_conflict_result(
    appointment_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_appointments: list[AppointmentAdd] = []

    async def create(session: object, appointment: AppointmentAdd) -> bool:
        created_appointments.append(appointment)
        return len(created_appointments) == 1

    monkeypatch.setattr(AppointmentService, "create", staticmethod(create))
    url = f"/workstations/{WORKSTATION_ID}/appointments"
    payload = {
        "worker_id": str(WORKER_ID),
        "begin_at": BEGIN_AT.isoformat(),
        "end_at": END_AT.isoformat(),
    }

    created = appointment_client.post(url, json=payload)
    conflict = appointment_client.post(url, json=payload)

    assert created.status_code == 201
    assert created.json() == {"created": True}
    assert conflict.status_code == 200
    assert conflict.json() == {"created": False}
    assert len(created_appointments) == 2
    assert created_appointments[0].maker_id == USER_ID
    assert created_appointments[0].workstation_id == WORKSTATION_ID
    assert created_appointments[0].worker_id == WORKER_ID


def test_range_and_availability_routes_validate_and_return_results(
    appointment_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    queried_ranges: list[tuple[UUID, datetime, datetime]] = []
    can_schedule_ranges: list[tuple[UUID, datetime, datetime]] = []

    async def get_in_range(
        session: object,
        workstation_id: UUID,
        begin_at: datetime,
        end_at: datetime,
    ) -> list[AppointmentResponse]:
        queried_ranges.append((workstation_id, begin_at, end_at))
        return [_response()]

    async def can_schedule(
        session: object,
        workstation_id: UUID,
        begin_at: datetime,
        end_at: datetime,
    ) -> bool:
        can_schedule_ranges.append((workstation_id, begin_at, end_at))
        return False

    monkeypatch.setattr(
        AppointmentService,
        "get_in_range",
        staticmethod(get_in_range),
    )
    monkeypatch.setattr(
        WorkstationService,
        "can_schedule",
        staticmethod(can_schedule),
    )
    params = {
        "begin_at": BEGIN_AT.isoformat(),
        "end_at": END_AT.isoformat(),
    }
    url = f"/workstations/{WORKSTATION_ID}/appointments"

    appointments = appointment_client.get(url, params=params)
    availability = appointment_client.get(f"{url}/availability", params=params)
    invalid_range = appointment_client.get(
        url,
        params={
            "begin_at": END_AT.isoformat(),
            "end_at": BEGIN_AT.isoformat(),
        },
    )

    assert appointments.status_code == 200
    assert datetime.fromisoformat(appointments.json()[0]["begin_at"]) == BEGIN_AT
    assert availability.status_code == 200
    assert availability.json() == {"can_schedule": False}
    assert invalid_range.status_code == 422
    assert len(queried_ranges) == 1
    assert len(can_schedule_ranges) == 1


def test_get_and_delete_appointment_are_scoped_to_workstation(
    appointment_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def get(session: object, appointment_id: UUID) -> AppointmentResponse:
        return _response()

    deleted_ids: list[UUID] = []

    async def delete(session: object, appointment_id: UUID) -> bool:
        deleted_ids.append(appointment_id)
        return True

    monkeypatch.setattr(AppointmentService, "get", staticmethod(get))
    monkeypatch.setattr(AppointmentService, "delete", staticmethod(delete))
    base_url = f"/workstations/{WORKSTATION_ID}/appointments/{APPOINTMENT_ID}"

    retrieved = appointment_client.get(base_url)
    deleted = appointment_client.delete(base_url)
    wrong_workstation = appointment_client.get(
        f"/workstations/{UUID(int=4)}/appointments/{APPOINTMENT_ID}"
    )

    assert retrieved.status_code == 200
    assert retrieved.json()["id"] == str(APPOINTMENT_ID)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert wrong_workstation.status_code == 404
    assert deleted_ids == [APPOINTMENT_ID]


def test_cancel_and_complete_routes_return_service_action_results(
    appointment_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def get(session: object, appointment_id: UUID) -> AppointmentResponse:
        return _response()

    cancel_calls: list[tuple[UUID, UUID]] = []
    complete_calls: list[tuple[UUID, UUID]] = []

    async def cancel(
        session: object,
        appointment_id: UUID,
        requester_id: UUID,
    ) -> AppointmentActionResult:
        cancel_calls.append((appointment_id, requester_id))
        return AppointmentActionResult.CANCELLED

    async def complete(
        session: object,
        appointment_id: UUID,
        requester_id: UUID,
    ) -> AppointmentActionResult:
        complete_calls.append((appointment_id, requester_id))
        return AppointmentActionResult.COMPLETED

    async def membership_lookup(*args: object) -> None:
        raise AssertionError("Action endpoints must delegate authorization to service.")

    monkeypatch.setattr(AppointmentService, "get", staticmethod(get))
    monkeypatch.setattr(AppointmentService, "cancel", staticmethod(cancel))
    monkeypatch.setattr(AppointmentService, "complete", staticmethod(complete))
    monkeypatch.setattr(WorkstationService, "get", staticmethod(membership_lookup))
    url = f"/workstations/{WORKSTATION_ID}/appointments/{APPOINTMENT_ID}"

    cancelled = appointment_client.post(f"{url}/cancel")
    completed = appointment_client.post(f"{url}/complete")

    assert cancelled.status_code == 200
    assert cancelled.json() == {"result": AppointmentActionResult.CANCELLED.value}
    assert completed.status_code == 200
    assert completed.json() == {"result": AppointmentActionResult.COMPLETED.value}
    assert cancel_calls == [(APPOINTMENT_ID, USER_ID)]
    assert complete_calls == [(APPOINTMENT_ID, USER_ID)]
