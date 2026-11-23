# 04. 관리 API (`area:api`)

서버 상태 확인·관리용 HTTP API.

## 규칙
- [확정] FastAPI. 첫 범위는 읽기 전용 (#25). 쓰기 기능(공지, 백업 실행, 화이트리스트, 재시작)은 별도 이슈 [아이디어]
- [확정] 외부에 공개하지 않는다. `127.0.0.1` 또는 Tailscale IP로만 바인딩.
- [확정] RCON 명령을 만들 때 입력을 검증한다 (명령 주입 금지). 지금은 고정 명령 `list`만 보낸다.
- [확정] 인증: 바인딩 제한 + `Authorization: Bearer <API_TOKEN>`. `/health`만 인증 없음
  - 토큰은 `.env`의 `API_TOKEN`. 비어 있으면 compose가 기동을 거부하고, 앱도 모든 요청을 401로 거부한다
  - 비교는 `hmac.compare_digest`
- [확정] 위치·실행: `api/` 코드, compose 서비스 `api` 컨테이너
  - mc와는 compose 내부 네트워크의 RCON(`mc:25575`)으로 통신. RCON 포트는 publish하지 않는다
  - RCON 비밀번호는 `.env`의 `RCON_PASSWORD`를 mc와 api가 함께 쓴다. 바꾸면 `docker compose up -d`로 mc도 다시 만든다
  - `docker.sock`과 `data/`는 마운트하지 않는다. `backups/`만 읽기 전용(`/backups:ro`)
  - 비root(uid 10001), 읽기 전용 루트 파일시스템, `cap_drop: ALL`, `no-new-privileges`
  - 호스트 포트는 `.env`의 `API_PORT`, Tailscale IP는 `API_TAILSCALE_IP`
- [임시] 베이스 이미지 `python:3.12.16-slim-trixie`, `fastapi`·`uvicorn` 버전 고정 (`api/requirements.txt`)
- [임시] RCON 클라이언트는 직접 구현 (`api/app/rcon.py`), 타임아웃 3초
- [임시] 자동 문서(`/docs`, `/openapi.json`)는 끔

## 엔드포인트
| 경로 | 인증 | 응답 |
| --- | --- | --- |
| `GET /health` | 없음 | `{"status":"ok"}`. 컨테이너 healthcheck용 |
| `GET /status` | 토큰 | `{"online":true,"players_online":0,"players_max":20,"players":[]}`. RCON 실패 시 200 + `{"online":false,"error":"..."}` |
| `GET /backups/latest` | 토큰 | `{"count":6,"latest":{"name":"world-...tar.zst","size_bytes":...,"modified":"...+00:00"}}`. 백업 없으면 `latest: null`, 디렉토리 없으면 503 |

- 백업은 `world-YYYYmmdd-HHMMSS.tar.zst` 정식 이름의 일반 파일만 센다 (`.partial`, `.lock` 무시). 최신은 이름 순서 기준
- 시각은 UTC (ISO 8601)

## 운영
- 빌드·기동: `docker compose build api && docker compose up -d api`
- 테스트: `docker build --target test api/` (컨테이너 안에서 pytest, 호스트 설치 없음)
- 호출 예 (Tailscale 기기에서): `curl -H "Authorization: Bearer $API_TOKEN" http://<Tailscale IP>:<API_PORT>/status`
- 로그: `docker logs api`
- 토큰 교체: `.env`의 `API_TOKEN` 변경 후 `docker compose up -d api`

## 관련 파일
- `api/Dockerfile` (base / test / runtime 단계), `api/requirements*.txt`
- `api/app/main.py`, `api/app/rcon.py`, `api/tests/`
- `compose.yaml`의 `api` 서비스, mc의 `RCON_PASSWORD`
- `.env.example`: `RCON_PASSWORD`, `API_PORT`, `API_TAILSCALE_IP`, `API_TOKEN`

## 확인 방법
- `docker build --target test api/`
- `docker compose config`의 `ports` (api는 `127.0.0.1`·Tailscale IP만)
- `ss -tlnp`로 API 포트 바인딩
- verification.md: V1, V2, V3, V4
