---
name: pr
description: 현재 작업 브랜치의 변경을 한국어 커밋으로 만들고, 로컬 검증(compose config, shellcheck, pytest, 공개 파일 점검)이 통과하면 푸시해서 develop으로 PR을 연다. merge는 하지 않는다. Triggers: "/pr", "PR 올려줘", "커밋하고 PR"
---

# pr — 커밋 → 검증 → 푸시 → PR

```
브랜치 확인 → 커밋할 파일 점검 → 커밋 → 검증 → (통과 시) 푸시 → develop으로 PR
```

<HARD-GATE>
1. `main`·`develop`에서는 실행하지 않는다.
2. 검증이 **통과하지 않으면 푸시하지 않는다.** 도구가 없어서 못 돌렸으면 통과가 아니다.
3. 관계없는 파일을 섞지 않는다. 의심되면 묻는다.
4. 비밀값, 운영 데이터, `CLAUDE.local.md`의 값이 들어가면 커밋하지 않는다.
5. 푸시한 커밋은 고쳐 쓰지 않는다(`--amend`, 강제 푸시 금지).
6. PR을 merge하지 않는다.
</HARD-GATE>

Announce: `pr 스킬 실행 중 — 커밋하고 PR을 올립니다.`

## Phase 1: 상태 확인
- `git branch --show-current` — `<종류>/<번호>-<설명>` 형식이 아니면 멈춘다. 번호 N을 읽는다.
- `git status --porcelain`, `git diff --stat`, `git log --oneline origin/develop..HEAD`
- 이미 열린 PR: `gh pr list --head <브랜치> --state open` — 있으면 커밋·푸시만 하고 PR은 새로 만들지 않는다.
- 기획 파일 `docs/plan/<N>-*.md`와 이슈 라벨을 읽는다.

## Phase 2: 커밋할 파일 점검
아래가 섞였으면 멈추고 묻는다:
- 이슈와 관계없는 파일
- 비밀값: `.env`, 토큰·비밀번호처럼 보이는 문자열 (`git diff | grep -niE 'token|password|secret|rcon_password'`)
- 로컬 정보: `CLAUDE.local.md`, 그 파일의 "공개 파일 점검용 문자열" (`git grep -nF` / `git diff | grep -nF`)
- 서버 산출물: `data/`, `backups/`, `*.tar.gz`, `*.zip`, `whitelist.json`, `ops.json`, `*.log`
- Python 산출물: `__pycache__/`, `.venv/`

## Phase 3: 커밋
- 변경을 성격별로 나눌 수 있으면 커밋을 나눈다 (커밋마다 태그 1개).
- `git add <파일들>` (`git add -A` 금지 — 파일을 명시)
- 메시지를 임시 파일에 쓰고 `git commit -F <파일>`:
  ```
  feat: 월드 백업 스크립트 추가

  - scripts/backup.sh: save-off → 압축 → save-on, flock으로 중복 실행 방지
  - .env.example: BACKUP_KEEP 추가
  - docs/design/systems/03-backup.md 갱신

  Co-Authored-By: Claude <모델명> <noreply@anthropic.com>
  ```
  태그: `feat` `fix` `hotfix` `ui` `refactor` `test` `docs` `chore`

## Phase 4: 검증 → 푸시
해당 파일이 있으면 모두 통과해야 한다:
```bash
docker compose config -q
shellcheck scripts/*.sh
pytest                     # 관리 API가 생긴 뒤
git ls-files data/ .env CLAUDE.local.md   # 출력이 비어 있어야 함
```
- 하나라도 실패하거나 도구가 없으면 푸시하지 않고 멈춘다. 결과를 보고한다.
- 통과 직후에만 `git push -u origin <브랜치>`

## Phase 5: PR
- 본문을 임시 파일에 쓰고:
  `gh pr create --base develop --head <브랜치> --title "<이슈 제목>" --label "<이슈 라벨들>" --body-file <파일>`
- 본문 마지막 줄: `Generated with [Claude Code](https://claude.com/claude-code)`

## Phase 6: 보고
- PR URL, 커밋 목록, 검증 결과, 확인하지 못한 것
- CI 결과: `gh pr checks <번호>` (보조. 아직 돌고 있으면 진행 중이라고 적고, 실패하면 실패한 step을 적는다)
- "merge는 디렉터가 **Create a merge commit**으로 해주세요."

## PR 본문

```markdown
## 관련 이슈
- Closes #<번호>
- 기획 파일: `docs/plan/<번호>-<설명>.md`

## 무엇을, 왜
- ...

## 확인한 것
- 자동 검증: docker compose config / shellcheck / pytest 결과
- 수용 기준: [x] ...
- 서버에서 직접 확인한 것

## 확인하지 못한 것
- ...

## 바뀐 문서
- 기획 파일 / decisions.md / systems/... / player-guide.md
```

> `Closes #번호`는 저장소 **기본 브랜치**에 merge될 때만 이슈를 닫는다. 기본 브랜치가 `main`이면 `develop`으로 merge할 때는 닫히지 않는다.

## 범위 밖
- merge, `develop` → `main` 반영 → 디렉터
- 리뷰 → `/review`
