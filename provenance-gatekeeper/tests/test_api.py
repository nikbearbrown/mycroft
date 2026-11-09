from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_check():
    """Ensure the API boots up without crashing."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_failed_authentication():
    """Ensure the JWT gate is actually locked."""
    response = client.post(
        "/token",
        data={"username": "hacker", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_successful_authentication():
    """Ensure valid admins can get a token."""
    response = client.post(
        "/token",
        data={"username": "admin", "password": "secret_password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()