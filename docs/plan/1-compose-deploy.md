# #1 compose.yaml 작성·배포 및 친구 접속 테스트

- 이슈: #1
- 브랜치: `feature/1-compose-deploy`
- 종류: feature · 영역: area:server, area:network
- 선행: 없음
- 함께 나눈 이슈: 없음

## 목적
친구들이 외부에서 접속할 수 있는 Paper 서버를 compose 한 파일로 띄우고, 다시 띄워도 같은 상태가 되게 한다.

## 규칙 / 변경 내용
- [확정] `compose.yaml` 서비스 `mc`, 컨테이너 이름 `mc`, 이미지 `itzg/minecraft-server`
- [확정] 환경변수: `TYPE=PAPER`, `MEMORY=6G`, `TZ=Asia/Seoul`, `ONLINE_MODE=TRUE`, 화이트리스트 사용 + 강제
- [확정] 외부 포트는 `.env`의 `MC_PORT` → 컨테이너 25565. `compose.yaml`에는 `"${MC_PORT:?...}:25565"`만 쓴다. 값이 없으면 compose가 오류를 낸다
- [확정] 버전: `.env`의 `MC_VERSION`. 첫 기동은 `LATEST`로 하고, 기동 로그에서 확인한 버전으로 고정한다. 업그레이드는 백업 후 별도 이슈로
- [확정] RCON은 컨테이너 내부에서만 쓴다(`docker exec mc rcon-cli`). `ports`에 넣지 않는다
- [확정] 월드 데이터는 `./data:/data`
- [확정] `EULA=TRUE`: Minecraft EULA 동의. 서버 실행에 필수
- [임시] `restart: unless-stopped`: 재부팅·크래시 후 자동 재시작, 직접 멈추면 그대로 멈춤
- [임시] `stop_grace_period: 1m`: 종료할 때 월드 저장 시간을 확보
- [임시] 이미지 태그는 `latest`. 마크 버전은 `MC_VERSION`으로 따로 고정
- [임시] 화이트리스트 등록은 `rcon-cli whitelist add`로 한다. 닉네임은 공개 파일에 쓰지 않는다
- `.env.example`: `MC_PORT=`, `MC_VERSION=LATEST`

## 수용 기준
- [x] 성공: `docker compose config -q` 통과
- [x] 성공: `docker compose up -d` 후 `docker logs mc`에 `Done (` 출력
- [x] 성공: `ss -tlnp`에서 새로 열린 포트가 `0.0.0.0:<MC_PORT>` 하나이고 25575는 호스트에 없음
- [x] 성공: 화이트리스트에 등록한 계정으로 외부망(휴대폰 데이터 테더링 등)에서 접속 (2026-11-19, 도메인으로 접속. 서버 로그의 접속 IP가 서버 공인 IP와 다름)
- [x] 성공: 친구 1명 이상 접속 (2026-11-19, 로그 `joined the game`)
- [x] 실패·예외: 화이트리스트에 없는 계정은 접속 거부 (2026-11-20, 본인 계정을 잠시 빼고 접속 → `You are not whitelisted on this server!`, 확인 후 다시 추가)
- [x] 실패·예외: `.env`에 `MC_PORT`가 없으면 `docker compose config`가 오류
- [x] 경계: `docker compose down` → `up -d` 후 월드·화이트리스트 유지 (월드는 확인: 시드 동일. 화이트리스트는 2026-11-20 재기동 전후 `whitelist list` 5명 동일)
- [x] 경계: `MC_VERSION`을 확인된 버전으로 고정하고 다시 띄워도 같은 버전

## 지켜야 할 규칙
- verification.md: V1, V2, V3, V4, V5, V6, V13, V14
- V12: sshd·ufw·NetworkManager·logind를 건드리지 않음
- decisions.md: 서버 사양 (2026-11-18), 이번 기획의 결정 3건

## 영향 범위 (예상)
- 새 파일: `compose.yaml`, `.env.example`
- 로컬 파일 (커밋 안 함): `.env`, `data/`
- 문서: `systems/01-server.md` (메모리, 버전, 재시작, [미정] 정리), `systems/02-network.md` (포트), `CLAUDE.md` 서버 사양 줄 (8G → 6G, 버전 고정), `docs/player-guide.md` (게임 버전)
- Notion: 현재 구성 (서비스 구성, 메모리 13Gi), 원본 로그

## 확인 방법
- 자동: `docker compose config -q`, `docker compose config`의 ports 확인 (V1·V2), 공개 파일 점검 문자열 `git grep` (V4), `git ls-files .env data/` 비어 있음 (V3·V5)
- 직접: 기동 로그 `Done`, `ss -tlnp`, 화이트리스트 등록, 외부망 접속, 친구 접속, `down`/`up` 후 유지

## 범위 밖
- DuckDNS (로드맵 3), 백업 (로드맵 4)
- view-distance 등 성능 설정 ([미정] 유지)
- 플러그인, 모니터링 GUI
- 이미지 태그 고정

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| MEMORY 6G (8G에서 변경) | 실제 메모리 13Gi, 가용 9.4Gi. 8G 힙이면 컨테이너가 약 10G를 씀 | 2026-11-19 |
| 외부 포트는 `.env`의 `MC_PORT` | 공개 저장소에 실제 포트를 두지 않음 | 2026-11-19 |
| 마크 버전은 첫 기동 버전으로 `MC_VERSION`에 고정 | 자동 업그레이드되면 월드를 되돌릴 수 없음 | 2026-11-19 |
| 고정 버전 26.3 (Paper 26.3-255) | 2026-11-19 첫 기동 로그에서 확인 | — |

## 진행 기록
- 2026-11-19 빈 기획 파일 생성 (/issue)
- 2026-11-19 기획 작성 (/plan)
- 2026-11-19 구현 (/task): compose.yaml, .env.example 작성, 기동·포트·버전 고정·재생성 확인. 화이트리스트·외부 접속은 디렉터 확인 대기
- 2026-11-20 직접 확인 완료 (#12): 외부 접속, 친구 접속, 비화이트리스트 거부, 재기동 후 화이트리스트 유지
