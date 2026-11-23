---
name: review
description: 다른 사람의 PR을 임시 git worktree에서 직접 검증하고, 인프라 정확성(포트 노출, 비밀값, 백업 일관성, 데이터 손실, 원격 접속 영향)·프로젝트 규칙·기획 수용 기준·작업 흐름 기준으로 리뷰한다. 디렉터 확인 후 PR에 승인 또는 댓글을 남긴다. Triggers: "/review 10", "10번 PR 리뷰해줘"
---

# review — 다른 사람 PR 리뷰

```
PR 읽기 → 기준 모으기 → worktree에서 검증 → 코드 읽기 → 작업 흐름 점검
  → 걸러내기 → 디렉터에게 보고 → (확인 후) PR에 리뷰 남기기
```

<HARD-GATE>
1. 코드·문서를 고치지 않는다. 고칠 것은 리뷰로 알린다.
2. 디렉터의 작업 폴더를 건드리지 않는다. 검증은 임시 `git worktree`에서 하고 끝나면 지운다.
3. PR의 코드로 실제 서버(`mc` 컨테이너, `data/`)를 띄우거나 바꾸지 않는다. 정적 검증만 한다.
4. PR에 남기기 전에 결과를 디렉터에게 보여주고 확인받는다.
5. 승인(`--approve`)은 "꼭 고칠 것 없음 + 검증 통과 + 작업 흐름 지킴"일 때만. 그 밖에는 `--comment`. `--request-changes`와 merge는 하지 않는다.
6. 모든 지적에 `파일:줄`과 **구체적인 실패 상황**을 붙인다. 끝까지 확인하지 못한 것은 "확인 필요"로 적는다.
7. [미정] 사항을 리뷰에서 정하지 않는다.
8. 리뷰 글에 `CLAUDE.local.md`의 값과 비밀값을 쓰지 않는다.
</HARD-GATE>

Announce: `review 스킬 실행 중 — PR #<번호>를 리뷰합니다.`

## Phase 1: PR 읽기
- `gh pr view <번호> --json number,title,author,baseRefName,headRefName,labels,body,files`
- `gh pr diff <번호>`

## Phase 2: 기준 모으기
- 연결된 이슈, 기획 파일(수용 기준)
- `CLAUDE.md`, `docs/design/verification.md`, `docs/design/decisions.md`, 관련 `docs/design/systems/*.md`

## Phase 3: 직접 검증
```bash
git fetch origin pull/<번호>/head:review/pr-<번호>
git worktree add "<임시폴더>" review/pr-<번호>
cd "<임시폴더>"
docker compose config -q          # compose.yaml이 있으면 (.env가 필요하면 .env.example을 복사해 임시로)
shellcheck scripts/*.sh           # 스크립트가 있으면
pytest                            # 관리 API가 있으면
cd - && git worktree remove --force "<임시폴더>" && git branch -D review/pr-<번호>
```
`<임시폴더>`는 스크래치 디렉터리 아래에 만든다.

CI 결과도 본다: `gh pr checks <번호>`. CI는 보조라서 위 로컬 검증을 대신하지 않는다.

## Phase 4: 코드 읽기 (호출하는 곳까지 따라가기)
### A. 정확성 (인프라 체크리스트)
- **포트 노출**: 마크 서버 포트 외에 host IP 없이 publish된 포트가 있는지. Docker publish는 ufw를 우회한다. RCON(25575)이 `ports`에 있는지.
- **비밀값**: 토큰·비밀번호가 코드, 커밋, 로그 출력(`set -x`, `curl` URL 출력)에 남는지. 새 키가 `.env.example`에 있는지.
- **공개 저장소 노출**: `CLAUDE.local.md`의 값(IP, 인터페이스, 실제 포트)이 들어갔는지.
- **백업 일관성**: 백업 전 `save-off` + `save-all flush`, 끝나거나 실패해도 `save-on`(trap)이 보장되는지. 서버가 꺼져 있을 때의 동작.
- **삭제 안전성**: 오래된 백업 정리가 엉뚱한 경로를 지울 수 없는지 (빈 변수 + `rm -rf`, glob, 상대 경로).
- **중복 실행**: cron·타이머 작업에 `flock`이 있는지, 오래 걸릴 때 겹치지 않는지.
- **데이터 손실**: `docker compose down -v`, 볼륨·`data/` 삭제, 이미지 교체 시 데이터 경로 변경.
- **원격 접속 영향**: sshd·ufw·NetworkManager·logind를 건드리는지. 그렇다면 승인 절차와 되돌리는 방법이 있는지.
- **스크립트 견고성**: `set -euo pipefail`, 따옴표 없는 변수, 실패 시 종료 코드, 멱등성.
- **API**(생긴 뒤): 127.0.0.1/Tailscale 바인딩, 인증, RCON 명령 주입(입력 검증).

### B. 프로젝트 규칙 (`CLAUDE.md`)
### C. 기획과 맞는가 (수용 기준 하나씩)
### D. 테스트·검증
### E. 문서 (systems, decisions, verification, player-guide)
### F. 정리 (낮은 우선순위)

## Phase 5: 작업 흐름 점검
- 이슈 연결과 `Closes #N`
- 브랜치 이름(`<종류>/<N>-<설명>`)과 종류 라벨이 1:1인지
- 기획 파일이 채워져 있는지 (`_(작성 전 — /plan)_`이 남아 있지 않은지)
- 커밋 형식 (`<태그>: <요약>`)
- PR 본문의 "확인한 것 / 확인하지 못한 것"
- 서버에서 직접 확인이 필요한 변경인데 확인 기록이 있는지
- 범위를 넘은 변경

## Phase 6: 걸러내기
각 지적마다 다시 확인한다: 실제로 생길 수 있는가? 다른 곳(ufw, compose 기본값, 다른 스크립트)에서 이미 막고 있지 않은가? 아니면 뺀다.

## Phase 7: 디렉터에게 보고
```
판정: 승인 / 수정 필요 / 디렉터 판단 필요

## 꼭 고칠 것      (파일:줄 — 실패 상황)
## 고치면 좋은 것
## 확인 필요
## 검증 결과
## 작업 흐름
```

## Phase 8: PR에 남기기 (확인받은 뒤)
- 협업자에게 쓰는 글로 다듬어 임시 파일에 쓴다.
- `gh pr review <번호> --approve --body-file <파일>` 또는 `--comment --body-file <파일>`
- 자기 PR은 승인할 수 없다 → 댓글로 남긴다.

## 범위 밖
- 수정 → PR 작성자
- merge → 디렉터
