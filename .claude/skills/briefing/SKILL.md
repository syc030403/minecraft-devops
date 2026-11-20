---
name: briefing
description: 새 세션을 시작할 때 저장소(git), GitHub(이슈·PR), 서버(mc 컨테이너), 주기 작업(systemd 타이머), 문서(로드맵·결정·[미정])의 현재 상태를 읽기 전용으로 점검하고 한 화면으로 보고한 뒤 다음 작업을 추천한다. 아무것도 고치지 않는다. Triggers: "/briefing", "지금 상태 알려줘", "새 세션 시작", "어디까지 했지"
---

# briefing — 새 세션 상태 점검 (읽기 전용)

```
저장소 → GitHub → 서버 → 주기 작업 → 문서 → 보고(다음 작업 추천)
```

<HARD-GATE>
1. 파일 수정, 커밋, 푸시, 브랜치 변경(checkout·merge·삭제), 이슈·PR·라벨 변경을 하지 않는다. `git fetch`만 허용한다.
2. 서버를 조작하지 않는다. `docker compose up/down/restart/stop`, `docker exec`, `rcon-cli`를 실행하지 않는다.
3. sudo를 쓰지 않는다.
4. 비밀값을 출력하지 않는다. `.env` 내용을 읽거나 보여주지 않는다. 보고에 `CLAUDE.local.md`의 값은 필요한 만큼만 쓴다.
5. 명령 하나가 실패해도 멈추지 않는다. "확인하지 못한 것"에 적고 다음 단계로 간다.
6. 끝나고 다른 스킬을 자동으로 시작하지 않는다. 다음 작업은 추천만 한다.
</HARD-GATE>

Announce: `briefing 스킬 실행 중 — 현재 상태를 점검합니다 (읽기 전용).`

상세 문서(`docs/design/systems/`, 기획 파일 본문)는 여기서 다 읽지 않는다. `/plan`, `/task`가 필요할 때 읽는다.

## Phase 1: 저장소
- `git fetch origin --prune`
- `git branch --show-current`, `git status --porcelain`
- `main`과 `develop` 차이: `git log --oneline --first-parent origin/main..origin/develop`
- 로컬 `develop`이 뒤처졌는지: `git rev-list --count develop..origin/develop`
- 작업 브랜치: `git branch --list 'feature/*' 'fix/*' 'docs/*' 'chore/*'`, 그중 머지 끝난 것: `git branch --merged origin/develop`

## Phase 2: GitHub
- `gh issue list --state open --json number,title,labels`
  - `needs-decision` 라벨은 따로 표시
- `gh pr list --state open --json number,title,baseRefName,headRefName`

## Phase 3: 서버
- `docker compose ps`
- `docker logs mc --tail 20`: `Done`, `ERROR`/`WARN`, `joined the game` 줄 위주로 요약
- 컨테이너가 없거나 꺼져 있으면 "주의"로 표시하고 계속한다. 켜지 않는다.

## Phase 4: 주기 작업
- 이 저장소의 타이머 목록: `ls deploy/systemd/*.timer.in` → 이름에서 `.in`을 뗀다
- 각 타이머: `systemctl list-timers <이름> --all --no-pager` (마지막·다음 실행)
- 연결된 서비스의 최근 결과: `systemctl show <서비스> -p Result -p ExecMainExitTimestamp`
- 실패한 unit: `systemctl --failed --no-pager`
- 타이머가 설치되지 않았으면 "미설치"로 표시한다.

## Phase 5: 문서
- `docs/design/00-overview.md` 로드맵 표
- `docs/design/decisions.md` 최근 3줄
- 남은 [미정]: `grep -rn '\[미정\]' docs/design`
- 진행 중 기획: 열린 이슈의 `docs/plan/<N>-*.md`에서 체크 안 된 수용 기준 개수(`grep -c '\[ \]'`)와 `_(작성 전 — /plan)_` 여부

## Phase 6: 보고
한 화면 분량. 형식:

```
## 상태 요약
| 영역 | 상태 | 내용 |
| --- | --- | --- |
| 저장소 | 정상/주의 | 브랜치, 변경 여부, main↔develop 차이 |
| GitHub | 정상/주의 | 열린 이슈·PR 수, needs-decision |
| 서버 | 정상/주의 | 컨테이너 상태, 최근 로그 요약 |
| 주기 작업 | 정상/주의 | 타이머별 마지막 실행과 결과 |

## 진행 중인 작업
- 열린 이슈·PR·작업 브랜치, 각 기획 단계(빈 기획 / 기획 완료 / 구현 중)

## 남은 [미정]
- 문서별로 짧게

## 다음 작업 추천
- 1개, 이유 한 줄, 시작 명령 (`/issue ...`, `/plan N`, `/task N`, `/pr`)

## 확인하지 못한 것
- 실패한 명령과 이유
```

- 정리할 것(머지 끝난 로컬 브랜치, 뒤처진 `develop`)은 명령만 제안하고 실행하지 않는다.

## 범위 밖
- 문제 해결, 서버 재시작 → 디렉터 확인 후 별도 작업
- Notion 기록 읽기·쓰기 ([임시] 읽지 않음)
- 이슈 생성 → `/issue`
