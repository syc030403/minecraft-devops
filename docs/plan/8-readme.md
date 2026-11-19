# #8 저장소 README 작성

- 이슈: #8
- 브랜치: `docs/8-readme`
- 종류: docs · 영역: 없음
- 선행: 없음
- 함께 나눈 이슈: 없음

## 목적
공개 포트폴리오 저장소의 첫 화면에서, 방문자가 "무엇을, 어떤 구조로, 어떻게 안전하게, 어떤 방식으로 만들고 있는지"를 한 화면에 파악하고 자세한 문서로 넘어갈 수 있게 한다. 라이선스와 저장소 설명·토픽도 함께 정리한다.

## 규칙 / 변경 내용
- [확정] `README.md`를 저장소 루트에 둔다. 한국어만, 150줄 안팎
- [확정] 요약형이다. 자세한 내용은 `docs/` 링크로 넘기고, 같은 내용을 두 곳에 길게 쓰지 않는다
- [확정] 구성도는 mermaid로 그린다. 배지와 스크린샷은 넣지 않는다 (스크린샷은 모니터링 GUI가 생기면 추가)
- [확정] 공개 금지: IP, 실제 포트(`MC_PORT`로 표기), 서버 주소, 닉네임, Notion 주소
- 절 구성:
  1. 제목 + 한 줄 소개
  2. 소개: 목적 3줄 (노트북 1대 + Docker 운영, 운영 자동화, Docker·DevOps 학습)
  3. 구성도 (mermaid)
     - 친구 → 인터넷 → 공인 IP:`MC_PORT` → Docker 포트 공개 → `mc` 컨테이너(Paper) ↔ `./data`
     - 운영자 → Tailscale → SSH / `rcon-cli`
     - DuckDNS는 예정으로 표시
  4. 기술 스택 표: Docker Compose, itzg/minecraft-server, Paper 26.3, Tailscale, ufw, 예정(DuckDNS, FastAPI, 모니터링)
  5. 보안 설계 5줄
     - 외부 공개 포트 하나
     - RCON 미공개
     - Docker publish의 ufw 우회와 그 대응
     - 비밀값은 `.env`
     - 호스트 정보는 저장소 밖에 둠
  6. 실행 방법: `.env.example` 복사 → 값 채우기 → `docker compose up -d` → `rcon-cli whitelist add`
  7. 작업 흐름: `/issue → /plan → /task → /pr`, 기획 파일과 결정 기록으로 남김
  8. 로드맵 표: 완료 / 진행 중 / 예정
  9. 문서 안내: `docs/design`, `docs/plan`, `docs/development`, `docs/player-guide.md` 링크
  10. 디렉토리 구조 (짧게)
  11. 라이선스: MIT + 비어웨어 분위기의 한 줄 ("쓸 만했다면 언젠가 맥주 한 잔")
- [확정] `LICENSE`: MIT, `Copyright (c) 2026 syc030403`
- [확정] GitHub 저장소 설정 (`/task`에서 `gh repo edit`)
  - 설명: "노트북 1대로 운영하는 Docker 마인크래프트 서버와 운영 자동화"
  - 토픽: `docker`, `docker-compose`, `minecraft-server`, `papermc`, `devops`, `homelab`, `tailscale`
- [임시] 로드맵 진행 상태는 README에만 적는다. `00-overview.md` 로드맵은 결정 상태([확정]/[아이디어])를 유지한다

## 수용 기준
- [ ] 성공: 루트에 `README.md`가 있고, 위 11개 절이 있다
- [ ] 성공: GitHub에서 mermaid 구성도가 그림으로 보인다
- [ ] 성공: README의 상대 링크가 모두 실제 파일을 가리킨다
- [ ] 성공: 실행 방법의 키 이름(`MC_PORT`, `MC_VERSION`)과 명령이 `compose.yaml`·`.env.example`과 일치한다
- [ ] 성공: 루트에 MIT `LICENSE`가 있고, GitHub가 "MIT license"로 인식한다
- [ ] 성공: 저장소 설명과 토픽 7개가 설정돼 있다 (`gh repo view`)
- [ ] 경계: 150줄 안팎 (`wc -l`, 180줄 이하)
- [ ] 경계: 로드맵 상태가 실제와 맞다 (#1은 "배포 완료, 외부 접속 확인 중")
- [ ] 실패·예외: 공개 파일 점검 문자열(V4), 닉네임, Notion 주소, 이모지가 README·LICENSE에 없다

## 지켜야 할 규칙
- V3 비밀값 없음, V4 공개 파일에 로컬 정보 없음
- decisions.md: 공개 저장소 (2026-11-18), 이모지 금지 (2026-11-19)

## 영향 범위 (예상)
- 새 파일: `README.md`, `LICENSE`
- 문서: `docs/design/00-overview.md` (디렉토리 표에 README, LICENSE)
- GitHub 저장소 설정: 설명, 토픽
- Notion: 해당 없음 — 문서 작업이고 새로 배운 개념이 없음 [추론]

## 확인 방법
- 자동:
  - 상대 링크 존재 확인 (링크를 뽑아 `test -e`)
  - `wc -l README.md`
  - V4 문자열·이모지·`notion.com` grep
  - `gh repo view --json description,repositoryTopics,licenseInfo` (라이선스 인식은 merge 후 기본 브랜치에서)
- 직접: GitHub 브랜치 화면에서 README 렌더링과 mermaid 그림 확인 (디렉터)

## 범위 밖
- 영어 README, 배지, 스크린샷

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| README는 한국어, 요약형 + 문서 링크, mermaid 구성도, 배지 없음 | 문서 전체가 한국어이고, docs와 중복을 피함. CI가 없어 배지로 보여줄 상태가 없음 | 2026-11-19 |
| 라이선스 MIT + README에 비어웨어 분위기 한 줄 | 가장 익숙한 표준 라이선스이고 면책 조항이 있음. 맥주 문구는 법적 효력 없는 분위기용 | 2026-11-19 |
| 저장소 설명·토픽 설정 | 저장소 목록·검색 노출 | 해당 없음 |

## 진행 기록
- 2026-11-19 빈 기획 파일 생성 (/issue)
- 2026-11-19 기획 작성 (/plan)
