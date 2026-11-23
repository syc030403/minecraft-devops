"""가짜 RCON 서버로 클라이언트 프로토콜을 확인한다."""

import socket
import struct
import threading

import pytest

from app import rcon


def _send(conn, req_id, ptype, body):
    payload = struct.pack("<ii", req_id, ptype) + body.encode() + b"\x00\x00"
    conn.sendall(struct.pack("<i", len(payload)) + payload)


def _recv(conn):
    (length,) = struct.unpack("<i", conn.recv(4, socket.MSG_WAITALL))
    data = conn.recv(length, socket.MSG_WAITALL)
    req_id, ptype = struct.unpack("<ii", data[:8])
    return req_id, ptype, data[8:-2].decode()


@pytest.fixture
def fake_server():
    """password와 응답을 받아 연결 1개를 처리하는 서버. (host, port, 받은 명령 목록)을 돌려준다."""
    servers = []

    def start(password, reply):
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        servers.append(srv)
        received = []

        def run():
            conn, _ = srv.accept()
            with conn:
                req_id, ptype, body = _recv(conn)
                assert ptype == 3
                if body != password:
                    _send(conn, -1, 2, "")
                    return
                _send(conn, req_id, 2, "")
                req_id, ptype, body = _recv(conn)
                received.append((ptype, body))
                _send(conn, req_id, 0, reply)

        threading.Thread(target=run, daemon=True).start()
        return "127.0.0.1", srv.getsockname()[1], received

    yield start
    for s in servers:
        s.close()


def test_command_success(fake_server):
    host, port, received = fake_server("secret", "There are 0 of a max of 20 players online: ")
    out = rcon.command(host, port, "secret", "list", timeout=2)
    assert out == "There are 0 of a max of 20 players online: "
    assert received == [(2, "list")]


def test_command_wrong_password(fake_server):
    host, port, _ = fake_server("secret", "")
    with pytest.raises(rcon.RconError):
        rcon.command(host, port, "wrong", "list", timeout=2)


def test_command_connection_refused():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()  # 아무도 듣지 않는 포트
    with pytest.raises(rcon.RconError):
        rcon.command("127.0.0.1", port, "secret", "list", timeout=1)
