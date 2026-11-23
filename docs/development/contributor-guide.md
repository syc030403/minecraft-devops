# 기여 가이드 (사람용)

Claude Code 스킬로 이슈 → 기획 → 구현 → PR을 진행하는 방법. 규칙 전체는 `collaboration.md`.

## 준비
1. GitHub CLI 설치·로그인: `gh auth login`
2. 저장소 클론 후 `develop` 브랜치 확인: `git fetch origin && git checkout develop`
3. 검증 도구
   - Docker + Compose
   - shellcheck: `sudo apt install shellcheck`
   - 관리 API 테스트는 Docker로 돌린다: `docker build --target test api/` (호스트에 Python 패키지 불필요)
4. 로컬 파일 (커밋 금지)
   - `.env` — `.env.example`을 복사해 값 채우기
   - `CLAUDE.local.md` — 호스트 정보. 서버 운영자만 가짐

## 한 번의 작업 흐름

| 단계 | 입력 | 결과 | 확인할 것 |
| --- | --- | --- | --- |
| 1 | `/issue 월드 백업 자동화` | 이슈 초안 | 제목·라벨·브랜치 이름 확인 후 승인 |
| | | 이슈 + 브랜치 + 빈 기획 파일 푸시 | |
| 2 | `/plan 12` | 기획 초안 | 수용 기준, [미정] 질문에 답하고 승인 |
| | | 기획 파일 커밋·푸시 | |
| 3 | `/task 12` | 구현 + 검증 + 보고 | "확인하지 못한 것"을 직접 확인 (서버 기동, 접속 등) |
| 4 | `/pr` | 커밋 → 검증 → 푸시 → PR | PR 본문 확인 |
| 5 | GitHub에서 merge | `develop`에 반영 | **Create a merge commit** 사용 |
| 6 | (가끔) `develop` → `main` PR | 운영 반영 | 서버에 배포 후 확인 |

다른 사람 PR은 `/review 10`.

### 호출 형식
| 호출 | 뜻 |
| --- | --- |
| `/briefing` | 새 세션 시작 시 현재 상태 점검과 다음 작업 추천 (읽기 전용) |
| `/issue <아이디어 글>` | 새 이슈 만들기 |
| `/issue 12` | 웹에서 만든 12번 이슈에 브랜치·빈 기획 파일만 만들기 |
| `/plan 12` | 12번 기획 파일 채우기 (번호 필수) |
| `/task 12` | 12번 구현 |
| `/pr` | 현재 브랜치(`feature/12-...`)에서 번호를 읽어 PR |
| `/review 10` | 10번 **PR** 리뷰 |

중간에 멈추려면 `중단`, `여기까지`, `stop`.

## 라벨
- 종류 1개: `feature` `bug` `docs` `chore`
- 영역 0개 이상: `area:server` `area:network` `area:backup` `area:api` `area:monitoring`
- `needs-decision`: 결정이 필요해 시작할 수 없는 이슈. 결정을 `decisions.md`에 남기고 라벨을 떼면 `/task` 가능.

## 웹에서 이슈를 만들 때
- 템플릿(기능·버그·문서·정리)을 고르고 목적 한 줄과 메모만 쓴다.
- 그다음 CLI에서 `/issue <번호>`로 브랜치와 빈 기획 파일을 만든다.

## 주의
- 공개 저장소다. 이슈·PR·커밋에 IP, 실제 포트, 토큰, 서버 주소를 쓰지 않는다.
- `Closes #N`은 기본 브랜치에 merge될 때만 이슈를 닫는다. 기본 브랜치가 `main`이면 `develop` merge 때는 수동으로 닫거나, 기본 브랜치를 `develop`으로 바꾼다.
- Claude가 제시한 sudo 명령은 내용을 읽고 직접 실행한다.
