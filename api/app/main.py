"""관리 API (읽기 전용). 규칙: docs/design/systems/04-api.md

설정은 환경변수에서 요청마다 읽는다 (compose.yaml, .env):
  API_TOKEN      Bearer 토큰. 비어 있으면 보호된 엔드포인트는 모두 401
  RCON_HOST      기본 mc (compose 내부 네트워크의 서비스 이름)
  RCON_PORT      기본 25575
  RCON_PASSWORD  mc와 같은 값
  BACKUP_DIR     기본 /backups (읽기 전용 마운트)
"""

import hmac
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException

from . import rcon

# world-backup.sh와 같은 정식 백업 이름. 이름 순서 = 시간 순서
BACKUP_NAME_RE = re.compile(r"^world-\d{8}-\d{6}\.tar\.zst$")
LIST_RE = re.compile(r"There are (\d+) of a max(?: of)? (\d+) players online:(.*)", re.S)
COLOR_CODE_RE = re.compile("§.")

app = FastAPI(title="minecraft-devops 관리 API", docs_url=None, redoc_url=None, openapi_url=None)


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("API_TOKEN", "")
    scheme, _, given = (authorization or "").partition(" ")
    if (
        not expected
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(given.encode(), expected.encode())
    ):
        raise HTTPException(
            status_code=401, detail="인증 실패", headers={"WWW-Authenticate": "Bearer"}
        )


def parse_list(text: str) -> tuple[int, int, list[str]] | None:
    """RCON `list` 응답을 (접속자 수, 최대, 이름 목록)으로. 형식이 다르면 None."""
    m = LIST_RE.search(COLOR_CODE_RE.sub("", text))
    if not m:
        return None
    names = [n.strip() for n in m.group(3).split(",") if n.strip()]
    return int(m.group(1)), int(m.group(2)), names


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/status", dependencies=[Depends(require_token)])
def status() -> dict:
    try:
        text = rcon.command(
            os.environ.get("RCON_HOST", "mc"),
            int(os.environ.get("RCON_PORT", "25575")),
            os.environ.get("RCON_PASSWORD", ""),
            "list",  # 고정 명령만 보낸다. 사용자 입력을 RCON으로 넘기지 않는다
        )
    except rcon.RconError as e:
        return {"online": False, "error": str(e)}
    parsed = parse_list(text)
    if parsed is None:
        return {"online": True, "error": "list 응답을 해석하지 못함"}
    online, max_players, names = parsed
    return {"online": True, "players_online": online, "players_max": max_players, "players": names}


@app.get("/backups/latest", dependencies=[Depends(require_token)])
def backups_latest() -> dict:
    backup_dir = Path(os.environ.get("BACKUP_DIR", "/backups"))
    if not backup_dir.is_dir():
        raise HTTPException(status_code=503, detail="백업 디렉토리를 찾을 수 없음")
    files = sorted(
        p for p in backup_dir.iterdir() if BACKUP_NAME_RE.match(p.name) and p.is_file()
    )
    if not files:
        return {"count": 0, "latest": None}
    latest = files[-1]
    st = latest.stat()
    return {
        "count": len(files),
        "latest": {
            "name": latest.name,
            "size_bytes": st.st_size,
            "modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        },
    }
