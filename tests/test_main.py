from fastapi.testclient import TestClient

from schedule_manager.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Schedule Manager API is running"}


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_business_routes_are_registered():
    paths = app.openapi()["paths"]
    assert "/businesses" in paths
    assert "/businesses/{business_id}/owners" in paths
