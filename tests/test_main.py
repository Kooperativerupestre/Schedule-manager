import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from schedule_manager.auth.errors import AuthenticationInvalidCredentialsError
from schedule_manager.business.memberships.errors import MembershipNotFoundError
from schedule_manager.core.exception_handlers import register_exception_handlers
from schedule_manager.main import app
from schedule_manager.unit.memberships.errors import (
    UnitMembershipNotFoundError,
)
from schedule_manager.user.errors import UserForbiddenError

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Schedule Manager API is running"}


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (AuthenticationInvalidCredentialsError("Email or password is invalid."), 401),
        (UserForbiddenError("Access denied."), 403),
        (MembershipNotFoundError("Membership not found."), 404),
        (UnitMembershipNotFoundError("Unit membership not found."), 404),
    ],
)
def test_domain_errors_use_global_exception_handlers(
    error: Exception,
    expected_status: int,
) -> None:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/")
    async def raise_error() -> None:
        raise error

    response = TestClient(test_app).get("/")

    assert response.status_code == expected_status
    assert response.json() == {"detail": str(error)}
