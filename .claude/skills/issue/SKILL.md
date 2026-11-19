---
name: issue
description: GitHub 이슈를 등록(또는 기존 이슈를 받아)하고, develop에서 작업 브랜치와 빈 기획 파일을 만들어 커밋·푸시한 뒤 이슈에 링크한다. 기획 내용은 쓰지 않는다. Triggers: "/issue 월드 백업 자동화", "/issue 12", "이거 이슈로 만들어줘", "이슈 등록해줘"
---

# issue — 이슈 + 브랜치 + 빈 기획 파일

```
입력(아이디어 글 | 이슈 번호)
  → 이슈 생성(초안 확인) 또는 기존 이슈 확인
  → origin/develop에서 작업 브랜치
  → 빈 기획 파일 커밋·푸시
  → 이슈 본문에 기획 파일 링크
  → develop 복귀
```

<HARD-GATE>
1. 기획 내용을 쓰지 않는다. `docs/plan/README.md`의 "빈 기획 파일" 형태로만 만든다.
2. 코드·설정·다른 문서는 수정하지 않는다.
3. 새 이슈는 초안(제목·라벨·본문·브랜치 이름)을 보여주고 확인받은 뒤 만든다. 이미 있는 이슈 번호를 받았으면 그 자체가 진행 요청이다.
4. `main`·`develop`에 직접 커밋하지 않는다.
5. 공개 저장소다. 이슈·커밋에 `CLAUDE.local.md`의 값(IP, 인터페이스, 실제 포트)과 비밀값을 쓰지 않는다.
6. 라벨을 임의로 만들지 않는다.
7. 끝난 뒤 `plan`을 자동으로 시작하지 않는다.
</HARD-GATE>

Announce: `issue 스킬 실행 중 — 이슈와 빈 기획 파일을 만듭니다.`

## Phase 0: 사전 확인
- `git status --porcelain` — 변경이 있으면 멈추고 어떻게 할지 묻는다.
- `gh auth status` — 로그인 안 돼 있으면 멈춘다.
- `git fetch origin`
- `git rev-parse --verify origin/develop` — 없으면 멈추고 알린다.

## Phase 1: 입력 판별
- 숫자만 → Phase 2B (기존 이슈)
- 글 → Phase 2A (새 이슈)
- 비어 있으면 무엇을 이슈로 만들지 묻는다.

## Phase 2A: 새 이슈 초안
1. 중복 검색: `gh issue list --state all --search "<핵심어>" --limit 20`. 비슷한 이슈가 있으면 보여주고 계속할지 묻는다.
2. 종류 라벨 정확히 1개 (겹치면 bug > feature > docs > chore):

   | 라벨 | 브랜치 접두어 | 언제 |
   | --- | --- | --- |
   | `feature` | `feature/` | 새 기능, 서버 설정·동작 변경 |
   | `bug` | `fix/` | 의도와 다르게 동작 |
   | `docs` | `docs/` | 문서만 바뀜 |
   | `chore` | `chore/` | 정리, 도구, 이미지·의존성 버전 |

3. 영역 라벨 0개 이상 (`docs/design/systems/`와 1:1):
   `area:server` `area:network` `area:backup` `area:api` `area:monitoring`
4. 제목은 한국어. slug는 영어 소문자-하이픈 3~5단어 (예: `world-backup-cron`).
5. 본문은 아래 "이슈 본문 형식". 버그는 `## 재현`이 필수 — 모르면 묻는다.
6. 초안을 보여주고 확인받는다:
   ```
   제목: 월드 백업 자동화
   라벨: feature, area:backup
   브랜치: feature/<N>-world-backup-cron  (N은 생성 후 확정)
   본문:
   ...
   ```

## Phase 2B: 기존 이슈
- `gh issue view <N> --json number,title,state,labels,body`
- 닫혀 있으면 멈춘다.
- 종류 라벨이 없거나 2개 이상이면 무엇으로 할지 묻는다.
- 브랜치 중복 확인: `git ls-remote --heads origin "*/<N>-*"`, `git branch --list "*/<N>-*"` — 있으면 알리고 멈춘다.
- slug는 제목에서 만들고 보고에 적는다.

## Phase 3: 생성
1. 라벨 존재 확인: `gh label list --limit 100`. 필요한 라벨이 없으면 멈추고 알린다.
2. (2A만) 본문을 임시 파일에 쓰고 `gh issue create --title "<제목>" --label "<라벨,...>" --body-file <파일>` → 번호 N 확인.
3. `git checkout -b <접두어><N>-<slug> origin/develop`
4. `docs/plan/<N>-<slug>.md` 작성 — `docs/plan/README.md`의 "빈 기획 파일" 형태 그대로. 진행 기록 첫 줄: `- <오늘 날짜> 빈 기획 파일 생성 (/issue)` (`date +%F`).
5. 커밋 메시지를 임시 파일에 쓰고 `git add docs/plan/<N>-<slug>.md && git commit -F <파일>`:
   ```
   docs: #<N> 빈 기획 파일: <제목>

   - docs/plan/<N>-<slug>.md 생성

   Co-Authored-By: Claude <모델명> <noreply@anthropic.com>
   ```
6. `git push -u origin <브랜치>`
7. 이슈 본문의 `## 기획` 절 "기획 파일" 줄을 링크로 바꾼다.
   - 저장소 이름: `gh repo view --json nameWithOwner -q .nameWithOwner`
   - `- 기획 파일: [docs/plan/<N>-<slug>.md](https://github.com/<owner>/<repo>/blob/<브랜치>/docs/plan/<N>-<slug>.md)`
   - `gh issue view <N> --json body -q .body > <파일>` → 수정 → `gh issue edit <N> --body-file <파일>`
8. `git checkout develop`

## Phase 4: 보고
- 이슈 URL, 라벨, 브랜치, 기획 파일 경로, 커밋 해시, 푸시 결과
- 확인하지 못한 것 (있으면)
- `다음 단계: /plan <N>`

## 이슈 본문 형식

```markdown
<목적 한 줄>

## 재현            ← 버그만
- 상태: ...
- 한 것: ...
- 기대: ...
- 실제: ...

## 메모
- 아이디어, 참고, 정해야 할 것

## 기획
- 기획 파일: (작성 전)
- 선행: 없음 / #11
```

## 범위 밖
- 기획 작성 → `/plan`
- 구현 → `/task`
- 라벨 생성 → 디렉터 확인 후 별도 작업
