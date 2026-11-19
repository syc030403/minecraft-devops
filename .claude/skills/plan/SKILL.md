---
name: plan
description: /issue가 만든 빈 기획 파일(docs/plan/<번호>-<설명>.md)을 채운다 — 목적, 변경 내용, 수용 기준, 영향 범위, 확인 방법. 정한 결정은 decisions.md에 기록하고, 너무 크면 이슈 나누기를 제안한다. 코드는 고치지 않는다. Triggers: "/plan 12", "12번 기획해줘", "기획 파일 채워줘"
---

# plan — 빈 기획 파일 채우기

```
이슈 번호 → 브랜치·기획 파일 확인 → develop 합치기 → 맥락 읽기
  → 막힌 곳 질문(있으면 멈춤) → 초안 → 승인 → 기획 파일·decisions.md 커밋·푸시
```

<HARD-GATE>
1. 코드·설정·시스템 문서는 수정하지 않는다. 쓰는 파일은 기획 파일과 `docs/design/decisions.md`뿐이다.
2. 브랜치나 빈 기획 파일이 없으면 `/issue <번호>`를 먼저 하라고 알리고 멈춘다. (예외: 이 스킬 안에서 이슈 나누기를 승인받은 경우)
3. [미정] 사항을 임의로 확정하지 않는다. 막히면 질문하고 멈춘다.
4. 커밋·푸시·라벨 변경·나눈 이슈 등록은 초안 승인 후에만 한다.
5. `main`·`develop`에 직접 커밋하지 않는다.
6. 공개 저장소다. 기획 파일에 `CLAUDE.local.md`의 값과 비밀값을 쓰지 않는다. 필요하면 "`CLAUDE.local.md` 참고"로 적는다.
7. 끝난 뒤 `task`를 자동으로 시작하지 않는다.
</HARD-GATE>

Announce: `plan 스킬 실행 중 — #<N> 기획 파일을 채웁니다.`

## Phase 0: 입력 확인
- 이슈 번호가 없으면 멈춘다. 아이디어 글만 받았으면 `/issue <글>`부터 하라고 알린다.

## Phase 1: 상태 확인
- `git status --porcelain` — 변경이 있으면 멈추고 묻는다.
- `git fetch origin`
- `gh issue view <N> --json number,title,state,labels,body` — 닫혀 있으면 멈춘다.
- 브랜치 찾기: `git branch -a --list "*/<N>-*"` — 없으면 멈춤 (`/issue <N>` 안내).
- `git checkout <브랜치>` → `git merge origin/develop` (충돌 나면 멈추고 알림)
- `docs/plan/<N>-*.md`가 있는지, `_(작성 전 — /plan)_` 표시가 남아 있는지 확인. 이미 채워져 있으면 덮어쓸지 묻는다.

## Phase 2: 맥락 읽기 (추측 금지)
- 이슈 본문과 댓글 (`gh issue view <N> --comments`)
- `CLAUDE.md`, `CLAUDE.local.md`(있으면, 값은 공개 파일에 옮기지 않음)
- `docs/plan/README.md`
- `docs/design/00-overview.md`, 관련 `docs/design/systems/*.md`
- `docs/design/decisions.md`, `docs/design/verification.md`
- 관련 파일: `compose.yaml`, `scripts/`, `.env.example` 등을 grep
- 관련 이슈: `gh issue list --state all --search "<핵심어>"`

## Phase 3: 막힌 곳 확인
- 이 작업을 [미정] 사항이 막고 있으면: 질문 최대 3개, 각각 선택지 + 추천안 + 이유. 답을 받을 때까지 멈춘다.
- 기존 결정(`decisions.md`)과 충돌하면 알린다.
- 버그인데 재현 방법이 없으면 묻는다.
- 외부 비용·계정이 생기는 선택이면 먼저 확인한다.

## Phase 4: 초안
- 기획 파일의 모든 절을 채운다. 해당 없으면 `해당 없음 — <이유>`, 추론한 내용은 `[추론]`.
- 수용 기준은 확인 가능한 문장으로: 성공 / 실패·예외 / 경계.
- "지켜야 할 규칙"에 이 작업이 건드리는 `verification.md` 항목 번호(V1…)를 적는다.
- "확인 방법"은 자동(검증 명령)과 직접(서버에서 확인할 것)으로 나눈다.
- `decisions.md`에 추가할 줄이 있으면 초안에 포함한다.
- **너무 크면 나누기 제안**: 이슈 하나 = 끝나면 실제로 써볼 수 있는 단계 하나. 파일 10개 또는 300줄을 넘을 것 같으면 나누는 안(제목·범위·선행 관계)을 제시한다.

## Phase 5: 승인 게이트
보여줄 것:
- 기획 파일 전체 초안
- `decisions.md`에 추가할 줄
- 커밋 메시지, 푸시할 브랜치
- (해당 시) `needs-decision` 라벨, 나눌 이슈 목록

확인받기 전에는 아무것도 쓰지 않는다.

## Phase 6: 쓰기
1. (나누기 승인 시) 새 이슈부터 만든다 — 각 이슈의 브랜치·빈 기획 파일은 `/issue` 절차를 따른다.
2. 기획 파일 쓰기. 진행 기록에 `- <오늘 날짜> 기획 작성 (/plan)` 추가.
3. `decisions.md` 표 맨 위(헤더 바로 아래)에 줄 추가.
4. 커밋 (`git commit -F <파일>`):
   ```
   docs: #<N> 기획: <제목>

   - docs/plan/<N>-<slug>.md 작성
   - decisions.md: <추가한 결정 요약>   ← 있을 때만

   Co-Authored-By: Claude <모델명> <noreply@anthropic.com>
   ```
5. `git push`
6. [미정] 때문에 시작할 수 없으면 `gh issue edit <N> --add-label needs-decision`
7. `git checkout develop`

## Phase 7: 보고
- 기획 요약(목적, 수용 기준 개수), 내린 결정, 남은 [미정], 커밋·푸시 결과
- `다음 단계: /task <N>` (또는 `needs-decision`이면 결정 후)

## 범위 밖
- 구현·설정 변경 → `/task`
- 시스템 문서 갱신 → `/task` Phase 7
- PR → `/pr`
