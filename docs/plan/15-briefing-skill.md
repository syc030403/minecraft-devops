# #15 새 세션 시작용 상태 점검 스킬 /briefing 추가

- 이슈: #15
- 브랜치: `chore/15-briefing-skill`
- 종류: chore · 영역: 없음
- 선행: 없음
- 함께 나눈 이슈: 없음

## 목적
새 세션을 시작할 때 `/briefing` 한 번으로 저장소·서버·작업 상태를 파악하고 다음 작업을 추천받는다. 매번 긴 프롬프트를 붙여 넣지 않고, 같은 순서로 빠짐없이 확인한다.

## 규칙 / 변경 내용
- [확정] 스킬 이름 `briefing`. `/status`, `/resume`은 Claude Code 기본 명령이라 피한다
- 새 파일 `.claude/skills/briefing/SKILL.md`. 다른 스킬과 같은 구조(frontmatter, 흐름도, HARD-GATE, Phase, 범위 밖)
- HARD-GATE
  1. 파일 수정, 커밋, 푸시, 이슈·PR·라벨 변경을 하지 않는다
  2. 서버를 조작하지 않는다 (`up`, `down`, `restart`, `rcon-cli` 명령 실행 금지). 읽기 전용 명령만
  3. sudo를 쓰지 않는다
  4. 보고에 비밀값을 출력하지 않는다 (`.env` 내용을 읽어 보여주지 않음)
  5. 끝나고 다른 스킬을 자동으로 시작하지 않는다
- Phase
  1. 저장소: `git status --porcelain`, 현재 브랜치, `git fetch`, `origin/main..origin/develop` 차이, 머지 끝난 로컬 브랜치
  2. GitHub: 열린 이슈(라벨 포함, `needs-decision` 강조), 열린 PR
  3. 서버: `docker compose ps`, `docker logs mc --tail 20` (오류·`Done`·접속 기록), `rcon-cli list`는 쓰지 않음 [추론: 서버 조작이 아니지만 RCON 명령이라 제외]
  4. 주기 작업: `systemctl list-timers`에서 이 저장소의 타이머(`duckdns-update` 등, `deploy/systemd/*.timer.in` 기준), 최근 실패는 `systemctl --failed`
  5. 문서: `00-overview.md` 로드맵, `decisions.md` 최근 3줄, `docs/design`의 `[미정]` 목록(grep), 진행 중 기획 파일(체크 안 된 수용 기준)
  6. 보고
- 보고 형식: 한 화면 분량
  - 상태 요약 표 (저장소 / GitHub / 서버 / 주기 작업, 각각 정상·주의)
  - 진행 중인 작업 (열린 이슈·PR·브랜치)
  - 남은 [미정]
  - 다음 작업 추천 1개와 이유, 시작 명령 (`/issue ...` 또는 `/plan N`)
  - 확인하지 못한 것 (명령 실패, 도구 없음)
- [임시] Notion은 읽지 않는다. 상태 확인에 필요한 정보는 저장소와 서버에 있고, Notion 호출은 느리고 길다
- 문서 갱신
  - `CLAUDE.md`, `docs/development/collaboration.md`: 작업 흐름에 "새 세션은 `/briefing`" 한 줄, 스킬 표에 추가
  - `docs/development/contributor-guide.md`: 명령 표에 `/briefing`
  - `README.md`: 작업 흐름 표와 디렉토리 설명의 스킬 목록

## 수용 기준
- [ ] 성공: `.claude/skills/briefing/SKILL.md`가 있고 Claude Code 스킬 목록에 `briefing`이 보인다
- [ ] 성공: 이 노트북에서 실행하면 위 6개 Phase를 거쳐 보고 형식대로 출력한다
- [ ] 성공: 보고에 다음 작업 추천과 시작 명령이 있다
- [ ] 실패·예외: 실행 전후 `git status`가 같고 커밋·푸시·서버 변경이 없다
- [ ] 실패·예외: 명령 하나가 실패해도(예: 컨테이너가 꺼짐) 멈추지 않고 "확인하지 못한 것"에 적고 끝까지 보고한다
- [ ] 경계: 보고에 `.env` 값, 토큰이 없다
- [ ] 경계: CLAUDE.md, collaboration.md, contributor-guide.md, README의 스킬 목록이 서로 맞다

## 지켜야 할 규칙
- V3, V4 (스킬 파일과 문서에 로컬 값 없음)
- decisions.md: 이모지 금지 (2026-11-19), 공개 저장소 (2026-11-18)

## 영향 범위 (예상)
- 새 파일: `.claude/skills/briefing/SKILL.md` (약 80줄)
- 문서: `CLAUDE.md`, `docs/development/collaboration.md`, `docs/development/contributor-guide.md`, `README.md`
- Notion: 작업 회고는 해당 없음 (chore, 새 개념 없음 [추론]). 배운 게 있으면 /task에서 판단

## 확인 방법
- 자동:
  - V4 문자열 `git grep -nF` 결과 없음
  - `grep -rn briefing CLAUDE.md docs/development README.md`로 문서 반영 확인
- 직접:
  - 새 세션(또는 이 세션)에서 `/briefing` 실행 → 보고 형식 확인, 실행 전후 `git status` 비교
  - `docker compose stop` 같은 상황 재현은 하지 않는다. 실패 처리는 스킬 문구로 확인

## 범위 밖
- Notion 요약, 백업 상태 확인 (백업 스킬·타이머가 생기면 Phase 4에 자동 포함되도록 타이머 기준으로만 작성)
- 자동 실행 (세션 시작 hook)

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| 새 세션 시작은 읽기 전용 `/briefing` 스킬로. 상세 문서는 각 스킬이 필요할 때 읽음 | 매번 같은 순서로 상태 확인, 시작 시 컨텍스트 절약 | 2026-11-20 |
| Notion은 /briefing에서 읽지 않음 [임시] | 상태 정보는 저장소·서버에 있고 Notion 호출이 느림 | 해당 없음 |

## 진행 기록
- 2026-11-20 빈 기획 파일 생성 (/issue)
- 2026-11-20 기획 작성 (/plan)
