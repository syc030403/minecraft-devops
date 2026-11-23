# #22 GitHub Actions로 compose config와 shellcheck 자동 검사

- 이슈: #22
- 브랜치: `chore/22-github-actions-ci`
- 종류: chore · 영역: 없음
- 선행: 없음
- 함께 나눈 이슈: 없음

## 목적
develop·main으로 가는 PR과 merge 결과를 GitHub Actions에서 자동으로 검사한다. 로컬 검증을 빠뜨리거나 로컬 환경 차이로 놓친 문제를 PR 화면에서 바로 보게 한다. CI는 보조이고, 푸시 전 로컬 검증 규칙은 그대로 둔다.

## 규칙 / 변경 내용
- [확정] workflow 파일 하나: `.github/workflows/check.yml`
- [확정] 실행 시점: develop·main 대상 `pull_request`, develop·main `push`(merge 후), `workflow_dispatch`(수동). 작업 브랜치 push는 PR로만 돈다 (같은 검사 두 번 방지)
- [확정] 검사 항목 (각각 별도 step으로 두어 어디서 실패했는지 보이게):
  1. `docker compose config -q` (V6)
  2. `shellcheck scripts/*.sh` (V7)
  3. V7: `scripts/*.sh`마다 `set -euo pipefail`이 있음
  4. V2: `docker compose config`의 published 포트에 25575가 없음
  5. V1: `host_ip`가 없거나 `0.0.0.0`인 published 포트가 정확히 1개
  6. V3·V5: `git ls-files .env CLAUDE.local.md data/ backups/` 결과가 비어 있음
  7. V4 일부: `git grep -nE '/home/[A-Za-z0-9_]'` 결과가 비어 있음
- [확정] CI에 넣지 않는 것: `CLAUDE.local.md`의 "공개 파일 점검용 문자열" 검사. 그 값을 workflow나 저장소에 쓰면 공개되므로 로컬에서만 한다
- [확정] `compose.yaml`의 필수 변수(`MC_PORT`, `MC_VERSION`)는 workflow `env`에 더미 값을 넣는다: `MC_PORT=25565`, `MC_VERSION=LATEST`. 실제 포트를 쓰지 않는다
- [확정] CI는 보조: 로컬 검증 규칙(통과해야 푸시)은 유지하고, 브랜치 보호로 merge를 막지 않는다. PR에서 결과를 보고 디렉터가 판단
- [임시] runner는 `ubuntu-24.04`로 고정 (`ubuntu-latest`는 움직이는 태그). [추론] shellcheck, docker compose, jq가 기본 설치돼 있음. `/task`에서 확인하고 없으면 설치 step 추가
- [임시] 외부 action은 `actions/checkout`만 쓰고 커밋 SHA로 고정(옆에 버전 주석). 현재 `v7.0.1` (`3d3c42e5…`). `permissions: contents: read`, secrets는 쓰지 않음
- [임시] 검사 로직은 별도 스크립트 없이 workflow step에 직접 쓴다 (작게 유지)
- [확정] "CI가 없다"고 적힌 문서를 고친다: `CLAUDE.md`, `docs/development/collaboration.md`, `README.md`. 로드맵 8번은 [확정]으로
- [임시] `/pr` 보고와 `/review` 검증에 `gh pr checks <번호>` 결과 확인을 한 줄씩 추가

## 수용 기준
- [ ] 성공: 이 브랜치의 develop 대상 PR에서 workflow가 돌고 모든 step이 통과한다 (`gh pr checks`)
- [ ] 성공: develop에 merge되면 push 트리거로 다시 돌고 통과한다 (merge 후 확인)
- [ ] 성공: `gh workflow run check.yml --ref <브랜치>`로 수동 실행된다
- [x] 실패·예외: 각 검사 명령을 로컬에서 일부러 틀린 입력으로 돌리면 0이 아닌 코드로 끝난다. 틀린 입력은 임시 사본으로 만들고 커밋하지 않는다
  - 25575를 publish한 compose 사본
  - 공개 포트가 2개인 compose 사본
  - `set -euo pipefail`이 없는 스크립트 사본
  - shellcheck 경고가 있는 스크립트 사본
- [x] 실패·예외: 필수 변수 더미 값이 없으면 compose step이 실패한다 (로컬에서 `env -u`로 확인)
- [x] 경계: workflow에 `CLAUDE.local.md`의 값, 비밀값, secrets 참조가 없다 (V3·V4 로컬 점검)
- [ ] 경계: 작업 브랜치 push와 PR이 함께 있을 때 workflow가 PR 쪽에서 한 번만 돈다
- [x] 경계: "CI가 없다"는 문구가 `CLAUDE.md`·`collaboration.md`·`README.md`에 남아 있지 않다

## 지켜야 할 규칙
- verification.md: V1, V2, V3, V4, V5, V6, V7 (CI가 검사하는 항목이자, 이 변경 자체가 지켜야 하는 항목)
- 관련 기존 결정: 도메인·실제 포트는 공개 문서에 쓰지 않음 (2026-11-19, #10)

## 영향 범위 (예상)
- 새 파일: `.github/workflows/check.yml`
- 문서: `CLAUDE.md`, `docs/development/collaboration.md`, `README.md`, `docs/design/00-overview.md`(로드맵 8번), `docs/design/verification.md`(CI가 검사하는 항목 표시)
- 스킬: `.claude/skills/pr/SKILL.md`, `.claude/skills/review/SKILL.md` (한 줄씩)
- compose / 스크립트 / `.env.example` / 테스트: 해당 없음 — 검사만 추가하고 동작은 바꾸지 않음
- 서버: 해당 없음 — 운영 서버에 반영할 것 없음
- [추론] 파일 9개, 줄 수는 100줄 안팎. 나누지 않음

## 확인 방법
- 자동 (로컬): `docker compose config -q`, `shellcheck scripts/*.sh`, V3·V4 로컬 점검, workflow 문법은 GitHub이 실행할 때 확인
- 직접:
  - PR을 연 뒤 `gh pr checks <번호>`와 Actions 실행 로그에서 step별 결과
  - `gh workflow run`으로 수동 실행 결과
  - merge 후 develop push 실행 결과 (디렉터가 merge한 뒤 `/briefing` 등에서 확인)
  - 위 실패 기준의 로컬 음성 테스트

## 범위 밖
- 브랜치 보호(required status checks) 설정
- pytest (관리 API가 생기면 그때 step 추가)
- 배포 자동화(CD), 서버에 자동 반영
- 의존성 자동 갱신 (Dependabot, Renovate)
- 로컬 문자열 점검의 CI 이전

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| 실행 시점: develop·main 대상 PR, develop·main push, 수동 실행 | PR에서 미리 보고 merge 결과도 다시 확인. 작업 브랜치 push 중복 실행 방지 | 2026-11-23 |
| 검사: compose config, shellcheck, 한 줄 규칙(V1·V2·V3·V5·V7, V4 홈 경로) | 한 줄로 되는 규칙은 함께 자동화. 로컬 문자열은 공개할 수 없어 제외 | 2026-11-23 |
| CI는 보조. 로컬 검증 유지, merge를 막지 않음 | V4 로컬 문자열 점검은 로컬에서만 가능. 1인 운영이라 디렉터가 PR에서 판단 | 2026-11-23 |

## 진행 기록
- 2026-11-23 빈 기획 파일 생성 (/issue)
- 2026-11-23 기획 작성 (/plan)
- 2026-11-23 구현 (/task): `check.yml`(step 9개: 도구 버전 + 검사 8개), 문서·스킬 갱신. `.env` 없는 임시 사본에서 정상 경로는 전부 통과했다. 음성 테스트도 전부 실패로 잡혔다: 25575, 공개 포트 2개, pipefail 없음, shellcheck 경고, 더미 변수 없음, .env·data 추적, 홈 경로. `127.0.0.1` 바인딩 추가는 통과. CI 실제 실행은 PR 후 확인
