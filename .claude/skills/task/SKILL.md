---
name: task
description: 기획 파일대로 구현한다 — 조사, (필요하면) 테스트 먼저, 구현, 검증(compose config, shellcheck, pytest, 서버 확인), 문서·기획 파일 갱신. 커밋·푸시·PR은 하지 않는다. Triggers: "/task 12", "12번 구현해줘", "12번 작업 시작"
---

# task — 기획 → 구현 → 검증

```
이슈 확인 → 브랜치 이동·develop 합치기 → 기획 파일 읽기 → 조사
  → 테스트 먼저(해당 시) → 구현 → 검증 → 문서 갱신 → 보고
```

<HARD-GATE>
1. `main`·`develop`에서 직접 작업하지 않는다.
2. 이슈·기획 파일에 없는 곳을 고치거나 [미정]을 정해야 하면 멈추고 묻는다.
3. 버그는 **원인을 증거로 확인하기 전에** 고치지 않는다.
4. 검증이 통과하지 않으면 "끝났다"고 하지 않는다. 도구가 없어서 못 돌렸으면 통과가 아니다.
5. 커밋·푸시·PR을 하지 않는다.
6. sudo 명령은 실행하지 않고 제시한다. sshd·ufw·NetworkManager·logind 변경은 명령을 보여주고 승인받는다.
7. 데이터가 사라지는 명령(`docker compose down -v`, `data/`·백업 삭제)은 승인 없이 실행하지 않는다.
8. 공개 파일에 `CLAUDE.local.md`의 값과 비밀값을 쓰지 않는다. 필요한 값은 `.env`로 뺀다.
</HARD-GATE>

Announce: `task 스킬 실행 중 — #<N> 구현을 시작합니다.`

중단: `중단` / `여기까지` / `stop`이면 바로 멈추고 진행 상황을 보고한다.

## Phase 1: 이슈 확인
- `gh issue view <N> --json number,title,state,labels,body`
- 닫혀 있거나 `needs-decision` 라벨이 있으면 멈춘다.
- 본문 "선행" 이슈가 열려 있으면 계속할지 묻는다.

## Phase 2: 준비
- `git status --porcelain` — 변경이 있으면 멈추고 묻는다.
- `git fetch origin` → `git checkout <종류>/<N>-<slug>` → `git merge origin/develop`
- `docs/plan/<N>-*.md` 읽기. `_(작성 전 — /plan)_`이 남아 있으면 `/plan <N>` 먼저 하라고 알리고 멈춘다.
- `docs/design/verification.md`에서 기획 파일이 가리키는 항목을 읽는다.

## Phase 3: 조사
- 바꿀 곳을 grep으로 모두 찾는다 (`compose.yaml`, `scripts/`, `.env.example`, `docs/`).
- 현재 상태 확인이 필요하면 읽기 전용 명령으로: `docker compose ps`, `docker logs mc --tail 100`, `ss -tlnp`, `docker compose config`.
- **버그면** 원인 가설 1~3개를 `파일:줄` 또는 로그 근거와 함께 세우고 하나씩 확인한다. 확인된 원인을 보고에 적는다.

## Phase 4: 테스트 먼저 (해당 시)
- 관리 API(Python)나 스크립트의 판단 로직이 바뀌면 수용 기준을 테스트로 먼저 쓰고 **실패하는 것을 확인**한다.
- 셸 스크립트는 가능하면 `--dry-run` 같은 확인 모드를 두고 그 출력으로 검증한다.
- 테스트를 위한 테스트는 늘리지 않는다.

## Phase 5: 구현
- `CLAUDE.md` 코드 규칙을 지킨다:
  - 비밀값·호스트별 값은 `.env` (새 키는 `.env.example`에도 추가)
  - 서버 설정은 `compose.yaml` 환경변수로 (`data/` 직접 수정 금지)
  - 셸: `set -euo pipefail`, 멱등, 실패 시 0이 아닌 종료 코드, 주기 실행은 `flock`
  - 포트: 외부 공개는 마크 서버 포트 하나, 나머지는 127.0.0.1 또는 Tailscale IP, RCON은 `ports`에 넣지 않음
- 기획에 없는 파일·수치·주기를 정해야 하면 멈추고 묻는다.
- 관계없는 문제를 발견하면 고치지 말고 "따로 볼 것"에 적는다.

## Phase 6: 검증
자동 (해당 파일이 있으면 모두):
```bash
docker compose config -q
shellcheck scripts/*.sh
pytest                     # 관리 API가 생긴 뒤
```
규칙 점검 (`verification.md`):
- V1·V2 포트: `docker compose config`의 `ports` 확인
- V3·V4 공개 파일 점검: `git status`, `git diff`, `CLAUDE.local.md`의 "공개 파일 점검용 문자열"로 `git grep -nF`
- 그 밖에 기획 파일이 가리키는 항목

직접 확인 (서버 반영이 필요한 변경):
- 실행 전 무엇을 할지 알리고 진행. 예: `docker compose up -d` → `docker logs mc --tail 50`에서 `Done` 확인
- 친구 접속, 외부 포트 확인처럼 직접 할 수 없는 것은 **확인 목록**으로 만들어 보고에 넣는다.

수용 기준을 하나씩 체크한다. 못 한 것은 못 했다고 적는다.

## Phase 7: 문서 갱신
- 기획 파일: 수용 기준 체크, "이 기획에서 내린 결정", 진행 기록 `- <오늘 날짜> 구현 (/task)`
- `docs/design/decisions.md` (방향이 바뀐 경우)
- 관련 `docs/design/systems/*.md`
- `docs/design/verification.md` (새로 지켜야 할 규칙이 생긴 경우)
- `docs/player-guide.md` (친구에게 영향이 있는 경우)
- Notion 운영 기록 (설정 변경, 문제 해결, 새로 알게 된 것이 있는 경우. 형식은 `CLAUDE.md` "기록")
- Notion 학습 기록 (형식은 `CLAUDE.md` "기록")
  - 작업 회고 `#N <이슈 제목>`: feature·bug는 필수, docs·chore는 새로 배운 게 있을 때만. PR 번호는 `/pr` 뒤에 채운다
  - 개념 정리: 이번 작업에서 새로 다룬 개념. 이미 있는 주제면 덧붙인다
  - 작업 회고 ↔ 개념 정리 ↔ 원본 로그 ↔ 트러블슈팅을 서로 링크한다

## Phase 8: 보고
```
## 바꾼 것
## 수용 기준   ([x] / [ ])
## 확인한 것   (명령과 결과)
## 확인하지 못한 것
## 임의로 정한 부분
## 새 결정
## 따로 볼 것
```
- 커밋·푸시하지 않았음을 적는다.
- `다음 단계: 확인 후 /pr`

## 범위 밖
- 커밋·푸시·PR → `/pr`
- 기획 변경 → 디렉터 확인 후 기획 파일 수정
