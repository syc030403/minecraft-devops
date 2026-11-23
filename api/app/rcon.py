"""최소 RCON 클라이언트 (Source RCON 프로토콜, 마인크래프트가 쓰는 형식).

패킷: [길이 int32][요청 id int32][종류 int32][본문 ASCII][\\x00\\x00]  (모두 little-endian)
흐름: 로그인(종류 3) -> 응답 id가 -1이면 비밀번호 틀림 -> 명령(종류 2) -> 응답 본문
"""

import socket
import struct

TYPE_AUTH = 3
TYPE_COMMAND = 2
# 마인크래프트 응답 본문은 최대 4096바이트. 그보다 큰 길이는 잘못된 패킷으로 본다
MAX_PACKET = 4096 + 10


class RconError(Exception):
    """연결·인증·응답 오류."""


def _pack(req_id: int, ptype: int, body: str) -> bytes:
    payload = struct.pack("<ii", req_id, ptype) + body.encode("utf-8") + b"\x00\x00"
    return struct.pack("<i", len(payload)) + payload


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise RconError("서버가 연결을 끊음")
        buf += chunk
    return buf


def _read_packet(sock: socket.socket) -> tuple[int, int, str]:
    (length,) = struct.unpack("<i", _recv_exact(sock, 4))
    if not 10 <= length <= MAX_PACKET:
        raise RconError(f"잘못된 패킷 길이: {length}")
    data = _recv_exact(sock, length)
    req_id, ptype = struct.unpack("<ii", data[:8])
    return req_id, ptype, data[8:-2].decode("utf-8", errors="replace")


def command(host: str, port: int, password: str, cmd: str, timeout: float = 3.0) -> str:
    """RCON으로 명령 하나를 보내고 응답 본문을 돌려준다. 실패하면 RconError."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall(_pack(1, TYPE_AUTH, password))
            req_id, _, _ = _read_packet(sock)
            if req_id == -1:
                raise RconError("RCON 인증 실패")
            sock.sendall(_pack(2, TYPE_COMMAND, cmd))
            req_id, _, body = _read_packet(sock)
            if req_id != 2:
                raise RconError(f"예상하지 않은 응답 id: {req_id}")
            return body
    except OSError as e:  # 연결 거부, 타임아웃, 이름 해석 실패 등
        raise RconError(f"RCON 연결 실패: {e.__class__.__name__}") from e
