import pytest
from fastapi.testclient import TestClient

TOKEN = "test-token"


@pytest.fixture
def backup_dir(tmp_path, monkeypatch):
    d = tmp_path / "backups"
    d.mkdir()
    monkeypatch.setenv("BACKUP_DIR", str(d))
    return d


@pytest.fixture
def client(monkeypatch, backup_dir):
    monkeypatch.setenv("API_TOKEN", TOKEN)
    monkeypatch.setenv("RCON_HOST", "127.0.0.1")
    monkeypatch.setenv("RCON_PORT", "1")
    monkeypatch.setenv("RCON_PASSWORD", "pw")
    from app.main import app

    return TestClient(app)


@pytest.fixture
def auth():
    return {"Authorization": f"Bearer {TOKEN}"}
