# minecraft-devops — Claude 작업 규칙

노트북 1대에 Docker로 Paper 마인크래프트 서버를 운영하고, 백업·DDNS·관리 API까지 자동화하는 인프라 저장소.
이 파일은 작업 규칙 요약이다. 원본은 `docs/development/collaboration.md`.

```
/issue → /plan → /task → /pr → (다른 사람 PR은) /review → 디렉터가 merge
```

| 문서 | 내용 |
| --- | --- |
| `CLAUDE.local.md` | 호스트 IP, 인터페이스, 보안 설정, 실제 포트 (gitignore, 공개 금지) |
| `docs/design/00-overview.md` | 서버 목적, 구성, 디렉토리, 로드맵 |
| `docs/design/systems/` | 영역별 기준 문서 (server, network, backup, api, monitoring) |
| `docs/design/decisions.md` | 결정 기록 |
| `docs/design/verification.md` | 항상 지켜야 할 규칙과 확인 방법 |
| `docs/plan/README.md` | 기획 파일 틀 |
| `docs/development/contributor-guide.md` | 사람용 사용법 |

## 역할과 결정
- 사용자는 디렉터(결정권자), Claude는 개발 파트너. 제안은 하되 확정하지 않는다.
- 사소하고 되돌리기 쉬운 구현은 판단해서 진행하고 보고에 "임의로 정한 부분"으로 적는다.
- 방향이 갈리는 결정은 선택지와 추천안을 제시하고 디렉터가 고르게 한다.
- **외부 비용·계정·결제가 생기는 일**(도메인, 유료 서비스, 외부 백업 저장소)은 반드시 먼저 확인한다.
- `docs/design`의 [미정] 사항은 임의로 확정하지 않는다.
- **승인 없이 하지 않는 일**
  - sudo 명령 실행 → 명령어만 제시하고 디렉터가 직접 실행
  - sshd·ufw·NetworkManager·logind 변경 → 원격 접속이 끊길 수 있음. 명령을 보여주고 승인. logind는 재시작 금지(재부팅으로 적용)
  - 데이터가 사라지는 명령 → `docker compose down -v`, `data/`·백업 삭제

## 소통
- 한국어 존댓말, 짧고 직접적으로. 확실하지 않으면 추측하지 말고 확인 명령을 먼저 제시한다.
- 문서에서 [확정] / [임시] / [미정] / [아이디어]를 구분해 표시한다.
- **이모지 사용 금지.** 답변, 문서, 코드·주석, 로그 메시지, 이슈, PR, 커밋 메시지 어디에도 쓰지 않는다.
- 끝나면 보고: 바꾼 것, 확인한 방법, **확인하지 못한 것**, 임의로 정한 부분, 커밋·푸시 여부.

## 코드 규칙
- **공개 저장소다.** `CLAUDE.local.md`의 값(IP, 인터페이스, 실제 포트)과 비밀값을 코드·문서·이슈·PR·커밋 메시지에 쓰지 않는다.
- 비밀값·호스트별 값은 `.env`에 둔다. 저장소에는 키 이름만 적은 `.env.example`을 둔다.
- 포트: Docker publish는 ufw를 우회한다.
  - 외부 공개는 마크 서버 포트 하나만.
  - 그 외 서비스는 `127.0.0.1:포트:포트` 또는 Tailscale IP로 바인딩.
  - RCON(25575)은 절대 `ports`에 넣지 않는다.
- 서버 설정은 `data/` 안의 파일을 직접 고치지 않고 `compose.yaml` 환경변수로 관리한다.
- 셸 스크립트: `#!/usr/bin/env bash` + `set -euo pipefail`, 여러 번 실행해도 결과가 같게(멱등), 실패하면 0이 아닌 종료 코드, 주기 실행은 `flock`으로 중복 방지.
- 식별자·파일 이름은 영어, 주석·문서·로그 메시지는 한국어 가능.
- 과한 도구·라이브러리를 먼저 들이지 않는다.

## 검증
- 자동 (해당 파일이 있으면 모두 통과해야 함):
  - `docker compose config -q`
  - `shellcheck scripts/*.sh`
  - `pytest` (관리 API가 생긴 뒤)
- 직접 확인: 기동 로그의 `Done`, `ss -tlnp`로 열린 포트, 친구 접속, 백업 복구.
- 규칙별 확인 방법은 `docs/design/verification.md`. 직접 확인을 못 했으면 못 했다고 적는다.
- 도구가 없어서 못 돌렸으면 통과가 아니다. 멈추고 설치 명령을 제시한다.
- CI는 없다. 로컬 검증이 유일한 검사다. 통과해야만 푸시한다.

## 문서
- 기능을 바꾸면 같은 작업에서 `docs/design/systems/` 문서를 고친다. 친구에게 영향이 있으면 `docs/player-guide.md`도.
- 방향이 바뀌면 `docs/design/decisions.md` 표 맨 위에 `| 날짜 | 결정 | 이유 | [#12 기획](../plan/12-....md) |`를 추가하고, 기획 파일 "이 기획에서 내린 결정"에도 적는다.

## Git
- 브랜치: `main`(안정·운영) ← `develop`(통합) ← 작업 브랜치 `feature/`·`fix/`·`docs/`·`chore/` + `<이슈번호>-<영어-소문자-설명>`
- **`main`과 `develop`에 직접 커밋하지 않는다.** 작업 브랜치는 최신 `origin/develop`에서 만들고 PR은 `develop`으로.
- **커밋과 푸시는 각각 디렉터가 요청할 때만.** (`/pr` 호출, `/issue` 새 이슈 확인, `/plan` 승인은 그 요청에 해당)
- PR merge와 `develop` → `main` 반영은 디렉터가 한다.
- 커밋 메시지는 한국어: 첫 줄 `<태그>: <요약>` + 빈 줄 + 변경 목록 + 마지막 줄 `Co-Authored-By:`
  - 태그: `feat` `fix` `hotfix` `ui` `refactor` `test` `docs` `chore` (커밋마다 1개)
- 메시지는 파일로 넘긴다: `git commit -F <파일>`
- 푸시한 커밋은 고쳐 쓰지 않는다(`--amend`, 강제 푸시 금지).
- **커밋 금지**: `.env`, `CLAUDE.local.md`, `data/`, `backups/`, 백업 압축 파일, `whitelist.json`, `ops.json`, 로그.
