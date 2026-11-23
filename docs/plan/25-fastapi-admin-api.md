# #25 FastAPI 관리 API

- 이슈: #25
- 브랜치: `feature/25-fastapi-admin-api`
- 종류: feature · 영역: area:api
- 선행: 없음
- 함께 나눈 이슈: 없음 (쓰기 기능은 이후 별도 이슈)

## 목적
서버 상태를 HTTP로 조회하는 읽기 전용 관리 API를 만든다. 지금은 `/briefing`이나 SSH로만 상태를 알 수 있다. 이 API는 이후 모니터링(로드맵 6)과 모니터링 GUI(로드맵 7)의 데이터 출처가 된다. Docker 멀티 컨테이너 구성(내부 네트워크, 읽기 전용 마운트, 비root 실행, healthcheck)을 직접 다뤄 본다.

## 규칙 / 변경 내용
- [확정] 기능 범위: 읽기 전용. 서버 상태를 바꾸는 엔드포인트는 만들지 않는다
  - `GET /health`: 인증 없음. API 프로세스가 살아 있는지만 응답 (`{"status":"ok"}`). 컨테이너 healthcheck에 쓴다
  - `GET /status`: mc 서버 온라인 여부, 접속자 수/최대, 접속자 이름 목록. RCON `list` 결과를 파싱한다
    - RCON 연결 실패 시 200 + `online: false`. 모니터링이 "서버 꺼짐"을 정상 응답으로 받게 한다
  - `GET /backups/latest`: `backups/`에서 가장 최근 `world-*.tar.zst`의 이름·시각·크기와 전체 개수. 없으면 `latest: null`
- [확정] 인증: 네트워크 제한 + 토큰
  - `/health`를 뺀 모든 엔드포인트에 `Authorization: Bearer <API_TOKEN>`. 없거나 틀리면 401
  - 비교는 `hmac.compare_digest`
  - `API_TOKEN`은 `.env`. 비어 있으면 compose가 기동을 거부한다 (`${API_TOKEN:?...}`)
- [확정] 실행 방식: 컨테이너. compose에 `api` 서비스 추가, 코드는 `api/` (`api/` [임시] 해제)
  - mc와는 compose 내부 네트워크의 RCON(`mc:25575`)으로 통신. RCON은 계속 `ports`에 넣지 않는다 (V2)
  - `docker.sock`은 마운트하지 않는다 (root 권한과 같음)
  - `./backups`를 `/backups:ro`로 마운트. `data/`는 마운트하지 않는다
  - 비root 사용자로 실행, `restart: unless-stopped`, healthcheck는 `/health`
  - 베이스 이미지는 `python:3.12-slim` 계열 태그로 고정 [임시]
  - 포트: `127.0.0.1:${API_PORT}:8000`, `${API_TAILSCALE_IP}:${API_PORT}:8000` (실제 값은 `.env`, `CLAUDE.local.md` 참고)
- [확정] RCON 비밀번호: `.env`의 `RCON_PASSWORD`를 mc와 api에 똑같이 넘긴다
  - 지금은 이미지가 자동 생성한 값을 쓰고 있어, 처음 적용할 때 mc 컨테이너를 다시 만들어야 한다 (서버 잠깐 중단, 접속자 없을 때 디렉터 확인 후)
- [임시] RCON 클라이언트는 라이브러리 없이 직접 구현 (프로토콜이 작고 학습 목적, 라이브러리 최소화). 타임아웃 3초
  - 보내는 명령은 고정 문자열 `list`뿐. 사용자 입력을 RCON으로 넘기지 않는다
- [임시] 의존성: `fastapi`, `uvicorn` (버전 고정). 테스트는 `pytest`, `httpx`
- [임시] 테스트 실행: Dockerfile `test` 단계에서 컨테이너 안 `pytest` (`docker build --target test api/`). 호스트에 Python 패키지를 설치하지 않는다
  - 스킬·CLAUDE.md의 `pytest` 줄을 이 명령으로 바꾼다
- `.env.example`: `API_PORT=`, `API_TAILSCALE_IP=`, `API_TOKEN=`, `RCON_PASSWORD=` (이름만)

## 수용 기준
- [ ] 성공: `docker build --target test api/` 통과 (RCON 파싱, 인증, 백업 조회 단위 테스트)
- [ ] 성공: `docker compose up -d` 후 `api`가 healthy, `127.0.0.1`과 Tailscale IP에서 `/health` 200
- [ ] 성공: 토큰을 넣은 `/status`가 `online: true`, 접속자 수가 `docker exec mc rcon-cli list`와 같다
- [ ] 성공: 토큰을 넣은 `/backups/latest`가 `ls -t backups/world-*.tar.zst | head -1`과 같은 파일
- [ ] 실패·예외: 토큰이 없거나 틀리면 `/status`, `/backups/latest`가 401
- [ ] 실패·예외: mc가 꺼져 있으면 `/status`가 200 + `online: false`, API는 죽지 않는다 (테스트는 가짜 RCON)
- [ ] 실패·예외: `API_TOKEN`이나 `RCON_PASSWORD`가 비어 있으면 `docker compose config` 실패
- [ ] 경계: 백업 0개이면 `/backups/latest`가 `latest: null`, `count: 0`
- [ ] 경계: `backups/`의 다른 이름 파일(`.partial`, `.lock`)은 무시
- [ ] 경계: 접속자 0명·여러 명 모두 `list` 파싱이 맞다 (단위 테스트)
- [ ] 보안: `docker compose config`의 `ports`에서 host_ip 없는 항목은 마크 서버 포트 하나, 25575 없음 (V1, V2)
- [ ] 보안: `ss -tlnp`에서 API 포트가 `127.0.0.1`과 Tailscale IP에만 열림
- [ ] 보안: api 컨테이너에 `docker.sock` 마운트 없음, 비root 실행 (`docker inspect`, `docker exec api id`)
- [ ] 운영: mc를 다시 만든 뒤 기동 로그 `Done`, `world-backup.sh`가 계속 성공 (rcon-cli가 새 비밀번호 사용)
- [ ] 문서: `04-api.md` [미정] 3개 정리, 관련 파일·확인 방법 갱신

## 지켜야 할 규칙
- verification.md: V1 (새 포트는 127.0.0.1·Tailscale IP만), V2 (RCON은 ports에 없음), V3 (`API_TOKEN`·`RCON_PASSWORD`는 `.env`에만), V4 (Tailscale IP·실제 포트를 공개 파일에 쓰지 않음), V6 (compose 문법), V13 (mc 다시 만든 뒤 `Done`)
- V8: 백업 스크립트의 `rcon-cli`가 바뀐 비밀번호로도 동작해야 한다
- V12: sshd·ufw·NetworkManager·logind는 건드리지 않음
- 04-api.md [확정]: 외부 비공개, RCON 명령 입력 검증
- decisions.md: 이미지 태그 고정 (#19 방침을 베이스 이미지에도 적용)

## 영향 범위 (예상)
- 새 파일: `api/Dockerfile`, `api/requirements.txt`, `api/requirements-dev.txt`, `api/app/main.py`, `api/app/rcon.py`, `api/tests/` (2~3개). 테스트 포함 약 300~400줄 [추론]. 나누기 기준에 걸칠 수 있으나 읽기 전용으로 범위를 이미 줄였으므로 나누지 않음
- 수정: `compose.yaml` (`api` 서비스, mc에 `RCON_PASSWORD`), `.env.example`
- 로컬 (커밋 안 함): `.env` 키 4개, mc 컨테이너 다시 만들기
- 문서:
  - `systems/04-api.md`: [미정] 정리, 엔드포인트, 관련 파일
  - `systems/02-network.md`: API 포트 바인딩
  - `00-overview.md`: 구성도 "관리 API(예정)", 디렉토리 `api/`, 로드맵 5
  - `CLAUDE.md`, `docs/development/collaboration.md`, `contributor-guide.md`, 스킬(task·pr·review): `pytest` 실행 명령
  - `README.md`: 로드맵·구성
  - `player-guide.md`: 해당 없음 — 친구에게 보이는 변화 없음 (mc 다시 만들 때 잠깐 중단만 미리 알림) [추론]
- Notion: 현재 구성(서비스·포트), 원본 로그, 작업 회고(필수), 개념 정리(compose 내부 네트워크와 서비스 이름 DNS, RCON 프로토콜, 멀티 스테이지 빌드)

## 위험
- [추론] 부팅 시 Docker가 Tailscale보다 먼저 뜨면 Tailscale IP 바인딩 실패로 api 기동이 실패할 수 있다. `/task`에서 재부팅 후 확인하고, 문제가 있으면 디렉터와 대응을 정한다
- mc를 다시 만드는 동안 서버가 잠깐 멈춘다 (기동 약 10초 + 종료 대기)

## 확인 방법
- 자동:
  - `docker build --target test api/`
  - `docker compose config -q`, `shellcheck scripts/*.sh`
  - `docker compose config`로 ports 점검 (V1, V2)
  - V4 문자열·홈 경로 `git grep`
- 직접:
  - mc 다시 만들기 → `docker logs mc`에서 `Done`
  - `curl`로 `/health`, `/status`, `/backups/latest` (토큰 있음·없음), 127.0.0.1과 Tailscale IP 각각
  - `ss -tlnp`로 API 포트 바인딩
  - `docker inspect api`로 마운트·사용자
  - `scripts/world-backup.sh` 직접 실행 성공 (RCON 비밀번호 변경 영향)
  - mc를 멈춘 상태에서 `/status` `online: false` (디렉터 확인 후, 못 하면 못 했다고 적음)
  - 재부팅 후 api 기동 (못 하면 못 했다고 적음)

## 범위 밖
- 쓰기 기능 (공지, 백업 실행, 화이트리스트, 재시작) — 별도 이슈
- systemd 타이머 결과 조회 — 컨테이너에서 볼 수 없음. 모니터링 이슈에서 방법을 정한다
- TPS·메모리 같은 성능 지표, 서버 버전 조회
- CI에 pytest 추가 — 별도 이슈 또는 `/task`에서 디렉터 요청 시
- GUI·알림

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| 관리 API 첫 범위는 읽기 전용 | 모니터링·GUI에 필요한 게 조회이고 서버를 바꿀 위험이 없음. 쓰기는 별도 이슈 | 2026-11-23 |
| 인증은 127.0.0.1·Tailscale 바인딩 + `.env`의 Bearer 토큰 | 단순하고 Tailnet 안의 다른 기기도 막음. 쓰기 기능에도 그대로 씀 | 2026-11-23 |
| API는 compose 서비스 컨테이너, RCON은 내부 네트워크, docker.sock 마운트 금지 | Docker 학습 목적, 격리, root 권한과 같은 소켓 노출 방지 | 2026-11-23 |
| RCON 비밀번호를 `.env`로 고정해 mc·api가 함께 씀 | 자동 생성 값은 api가 읽을 방법이 data/ 마운트뿐 | 해당 없음 |
| RCON 클라이언트 직접 구현 | 프로토콜이 작고 학습 목적, 라이브러리 최소화 | 해당 없음 |
| pytest는 Dockerfile test 단계에서 실행 | 호스트 패키지 설치 없음(sudo 불필요), 운영 이미지에 테스트 도구 없음 | 해당 없음 |
| RCON 실패 시 `/status`는 200 + `online: false` | 서버 꺼짐은 오류가 아니라 상태. 모니터링이 다루기 쉬움 | 해당 없음 |

## 진행 기록
- 2026-11-23 빈 기획 파일 생성 (/issue)
- 2026-11-23 기획 작성 (/plan)
