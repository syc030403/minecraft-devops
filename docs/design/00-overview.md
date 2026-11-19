# 00. 개요

## 목적
- [확정] 노트북 1대에서 Docker로 자바판 마인크래프트(Paper) 서버를 운영해 친구들과 함께 플레이한다.
- [확정] 운영(백업, DDNS, 관리 API, 모니터링)을 자동화하고 과정을 포트폴리오로 정리한다.

## 구성

```
친구(자바판) ──인터넷──▶ 공인 유동 IP : 마크 서버 포트 ──▶ mc 컨테이너 :25565
                              ▲
                     DuckDNS (유동 IP 갱신)

운영자 ──Tailscale──▶ SSH / 관리 API(예정) / RCON(컨테이너 내부만)
```

- 호스트: Ubuntu 노트북 1대. 상세(IP, 인터페이스, 보안 설정)는 `CLAUDE.local.md`.
- 서버: `itzg/minecraft-server` 컨테이너 `mc` → `systems/01-server.md`
- 네트워크: 외부 공개는 마크 서버 포트 하나, 나머지는 Tailscale → `systems/02-network.md`
- 백업 → `systems/03-backup.md`
- 관리 API → `systems/04-api.md`
- 모니터링 → `systems/05-monitoring.md`

## 디렉토리

| 경로 | 내용 | git |
| --- | --- | --- |
| `README.md` | 저장소 소개 (요약 + 문서 링크) | O |
| `LICENSE` | MIT | O |
| `compose.yaml` | 서버 정의 | O |
| `scripts/` | 백업, DDNS 등 스크립트 | O |
| `.env.example` | `.env` 키 목록 | O |
| `.env` | 비밀값·호스트별 값 | X |
| `data/` | 컨테이너가 만드는 월드 데이터 | X |
| `backups/` | 백업 결과물 [임시] 위치 | X |
| `docs/` | 기준 문서, 기획 파일, 협업 문서, 플레이어 안내 | O |
| `.claude/skills/` | 협업 스킬 | O |
| `CLAUDE.local.md` | 로컬 전용 정보 | X |

## 영역 라벨

| 문서 | 라벨 |
| --- | --- |
| `systems/01-server.md` | `area:server` |
| `systems/02-network.md` | `area:network` |
| `systems/03-backup.md` | `area:backup` |
| `systems/04-api.md` | `area:api` |
| `systems/05-monitoring.md` | `area:monitoring` |

## 로드맵

| 순서 | 내용 | 영역 | 상태 |
| --- | --- | --- | --- |
| 1 | Docker 설치 확인 (`docker run --rm hello-world`) | server | [확정] |
| 2 | `compose.yaml` 작성·배포, 친구 접속 테스트 | server, network | [확정] |
| 3 | DuckDNS DDNS (유동 IP 대응) | network | [확정] |
| 4 | 월드 백업 자동화 | backup | [확정] |
| 5 | FastAPI 관리 API | api | [아이디어] |
| 6 | 모니터링 | monitoring | [아이디어] |
| 7 | 모니터링 GUI (에반게리온 풍) | monitoring, api | [아이디어] |
| 8 | GitHub Actions (compose config, shellcheck) | — | [아이디어] |

로드맵 항목은 `/issue`로 이슈를 만들어 진행한다.
