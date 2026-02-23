from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app

client = TestClient(app)

def test_status():
    with patch("main.client") as mock_client:
        mock_client.containers.get.return_value.status = "running"
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

def test_start():
    with patch("main.client") as mock_client:
        mock_client.containers.get.return_value = MagicMock()
        response = client.post("/start")
        assert response.status_code == 200
        assert "message" in response.json()

def test_stop():
    with patch("main.client") as mock_client:
        mock_client.containers.get.return_value = MagicMock()
        response = client.post("/stop")
        assert response.status_code == 200
        assert "message" in response.json()
