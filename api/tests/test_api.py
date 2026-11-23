import os

import pytest

from app import main, rcon


def test_health_needs_no_token(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.parametrize("path", ["/status", "/backups/latest"])
@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer wrong"},
        {"Authorization": "test-token"},
        {"Authorization": "Basic test-token"},
    ],
)
def test_protected_endpoints_reject_bad_token(client, path, headers):
    assert client.get(path, headers=headers).status_code == 401


def test_empty_api_token_rejects_everything(client, auth, monkeypatch):
    monkeypatch.setenv("API_TOKEN", "")
    assert client.get("/status", headers={"Authorization": "Bearer "}).status_code == 401
    assert client.get("/status", headers=auth).status_code == 401


def test_status_online(client, auth, monkeypatch):
    monkeypatch.setattr(
        rcon,
        "command",
        lambda *a, **k: "There are 2 of a max of 20 players online: Alice, Bob",
    )
    r = client.get("/status", headers=auth)
    assert r.status_code == 200
    assert r.json() == {
        "online": True,
        "players_online": 2,
        "players_max": 20,
        "players": ["Alice", "Bob"],
    }


def test_status_offline_when_rcon_fails(client, auth, monkeypatch):
    def fail(*a, **k):
        raise rcon.RconError("연결 실패")

    monkeypatch.setattr(rcon, "command", fail)
    r = client.get("/status", headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["online"] is False
    assert "error" in body


@pytest.mark.parametrize(
    "text, expected",
    [
        ("There are 0 of a max of 20 players online: ", (0, 20, [])),
        ("There are 1 of a max of 20 players online: Steve", (1, 20, ["Steve"])),
        (
            "There are 3 of a max of 10 players online: A_1, b2, C3",
            (3, 10, ["A_1", "b2", "C3"]),
        ),
        ("§6There are 1 of a max of 20 players online:§r Steve\n", (1, 20, ["Steve"])),
    ],
)
def test_parse_list(text, expected):
    assert main.parse_list(text) == expected


def test_parse_list_unknown_format():
    assert main.parse_list("Unknown command") is None


def test_backups_empty(client, auth):
    r = client.get("/backups/latest", headers=auth)
    assert r.status_code == 200
    assert r.json() == {"count": 0, "latest": None}


def test_backups_latest_ignores_other_files(client, auth, backup_dir):
    for name in [
        "world-20261121-040000.tar.zst",
        "world-20261123-040007.tar.zst",
        "world-20261122-040000.tar.zst",
    ]:
        (backup_dir / name).write_bytes(b"x" * 10)
    (backup_dir / "world-20261124-040000.tar.zst.partial").write_bytes(b"x")
    (backup_dir / ".lock").write_bytes(b"")
    (backup_dir / "world-20261125-040000.tar.zst").mkdir()  # 디렉토리는 무시

    r = client.get("/backups/latest", headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 3
    assert body["latest"]["name"] == "world-20261123-040007.tar.zst"
    assert body["latest"]["size_bytes"] == 10
    assert body["latest"]["modified"].endswith("+00:00")


def test_backups_dir_missing(client, auth, backup_dir):
    os.rmdir(backup_dir)
    r = client.get("/backups/latest", headers=auth)
    assert r.status_code == 503
