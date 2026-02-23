from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app

client = TestClient(app)

def test_status():
    mock_container = MagicMock()
    mock_container.status = "running"

    with patch("main.client.containers.get", return_value=mock_container):
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

def test_start():
    mock_container = MagicMock()

    with patch("main.client.containers.get", return_value=mock_container):
        response = client.post("/start")
        assert response.status_code == 200
        assert "message" in response.json()

def test_stop():
    mock_container = MagicMock()

    with patch("main.client.containers.get", return_value=mock_container):
        response = client.post("/stop")
        assert response.status_code == 200
        assert "message" in response.json()
