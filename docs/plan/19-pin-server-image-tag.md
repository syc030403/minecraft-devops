# #19 마인크래프트 서버 이미지 태그 고정

- 이슈: #19
- 브랜치: `chore/19-pin-server-image-tag`
- 종류: chore · 영역: area:server
- 선행: 없음 (관련: #17)
- 함께 나눈 이슈: 없음

## 목적
서버 이미지를 `latest` 대신 정해진 릴리스 태그로 고정해, `docker compose pull`이나 컨테이너 재생성 때 이미지(시작 스크립트·Java 버전)가 예고 없이 바뀌지 않게 한다. 이미지를 올릴 때는 백업 후 태그를 바꾸는 PR로만 올린다.

## 규칙 / 변경 내용
- [확정] `compose.yaml`의 `image`를 `itzg/minecraft-server:<릴리스>-java25` 형태의 릴리스 태그로 고정한다. 값은 `.env`가 아니라 `compose.yaml`에 직접 둔다 (호스트별 값이 아니고, 올린 이력이 커밋으로 남음)
- [확정] 고를 태그: 지금 실행 중인 이미지와 같은 빌드의 릴리스 태그. 실행 중 이미지는 2026-11-19 빌드, `java25` 변형, 소스 커밋 `2b70dfc`. `/task`에서 Docker Hub 태그 목록과 digest를 대조해 정한다. 같은 digest의 태그가 없으면 가장 가까운 릴리스를 고르고 진행 기록에 이유를 적는다
- [확정] itzg 릴리스 태그 형식은 `YYYY.M.P`와 `YYYY.M.P-java25` (Docker Hub 태그 목록으로 확인)
- [확정] 고른 태그: `2026.11.0-java25` (digest `8d5080d8…`). 실행 중이던 `latest` 이미지(digest `eb30f3c5…`, 커밋 `2b70dfc`)와 같은 digest의 릴리스 태그는 없었다. 이 커밋은 `2026.11.0`보다 15커밋 앞서 있었다 (GitHub compare)
- [임시] 그 15커밋 안에 Java4Shell(CVE-2026-114938) 완화(itzg PR #4400, `-XX:-UseBASE64Intrinsics` 자동 추가)가 있어서, `compose.yaml`에 `JVM_XX_OPTS: "-XX:-UseBASE64Intrinsics"`를 직접 넣는다. 자동 적용이 들어간 릴리스로 올릴 때 뺀다 (/task 중 디렉터 결정)
- [확정] Paper 빌드(`PAPER_BUILD`)는 고정하지 않는다. 같은 마크 버전(`MC_VERSION`) 안의 빌드 갱신은 허용
- [확정] 업데이트 절차 (`01-server.md`에 적음):
  1. 백업: `sudo systemctl start world-backup.service`로 수동 백업하고 성공 확인
  2. itzg 릴리스 노트 확인 (Java 변형 변경, 깨지는 변경)
  3. 작업 브랜치에서 `compose.yaml` 태그 변경 → `docker compose pull` → `docker compose up -d`
  4. `docker logs mc`에 `Done`, 버전이 `MC_VERSION`과 같은지 확인
  5. PR로 반영. 문제가 있으면 이전 태그로 되돌리고 `up -d` (마크 버전이 그대로이므로 월드는 영향 없음)
- [확정] 복구 시험 명령(`03-backup.md`)의 `:latest`를 `compose.yaml`과 같은 태그를 쓰도록 바꾼다

## 수용 기준
- [x] 성공: `docker compose config`의 `mc` 이미지가 `itzg/minecraft-server:<릴리스>-java25` 형태이고 `latest`가 아니다
- [x] 성공: 고정 후 `docker compose up -d` → `docker logs mc`에 `Done`. 마크 버전은 26.3 그대로
- [x] 성공: 새 컨테이너의 java 프로세스에 `-XX:-UseBASE64Intrinsics`가 붙어 있다
- [x] 성공: `01-server.md`의 [미정] "이미지 태그 고정 여부"와 [임시] "이미지 태그 `latest`"가 [확정] 릴리스 태그 고정으로 바뀌고 업데이트 절차가 있다
- [x] 성공: `03-backup.md` 복구 시험 명령이 `latest`를 쓰지 않는다
- [x] 실패·예외: 적은 태그가 Docker Hub에 없으면 `docker compose pull`이 실패하고, 실행 중인 컨테이너는 그대로 남는다 (`up -d` 전에 `pull`로 먼저 확인)
- [x] 경계: 고정한 뒤 `docker compose pull`을 다시 해도 이미지 ID가 바뀌지 않고, `docker compose up -d`를 두 번 해도 두 번째에는 재생성이 없다
- [x] 경계: `git grep -n 'minecraft-server:latest' -- ':!docs/plan' ':!docs/design/decisions.md'` 결과가 비어 있다 (지난 기획·결정 기록은 이력이므로 그대로 둠)

## 지켜야 할 규칙
- verification.md: V1, V2, V4, V6, V13, V14
- 관련 기존 결정: 마크 버전은 `MC_VERSION`에 고정, 업그레이드는 백업 후 별도 이슈 (2026-11-19, #1)

## 영향 범위 (예상)
- compose: `compose.yaml` (`image` 한 줄)
- 스크립트: 해당 없음 — 이미지 태그를 읽는 스크립트가 없음
- 설정(.env.example): 해당 없음 — 값을 compose.yaml에 둠
- 테스트: 해당 없음 — pytest 대상 없음
- 문서: `docs/design/systems/01-server.md`, `docs/design/systems/03-backup.md`. 친구 영향 없음 (`player-guide.md` 변경 없음)
- 운영: [추론] 이미지 문자열이 바뀌면 compose가 설정 변경으로 보고 컨테이너를 한 번 다시 만든다. 1분 안팎 서버가 끊기므로 접속자가 없을 때 적용

## 확인 방법
- 자동: `docker compose config -q`, `docker compose config | grep image`, `shellcheck scripts/*.sh`, V4 공개 파일 점검, 위 `git grep`
- 직접:
  - 적용 전 `docker image inspect`로 고른 태그의 digest와 실행 중 이미지 비교
  - `docker compose pull` → `docker compose up -d` → `docker logs mc --tail 50`에 `Done`과 버전
  - `docker compose up -d` 한 번 더 → `mc  Running` (재생성 없음)
  - 친구(또는 본인) 외부망 접속 확인 (V14)

## 범위 밖
- 마크 버전 업그레이드 (`MC_VERSION` 변경) — 백업 후 별도 이슈
- Paper 빌드 고정 (`PAPER_BUILD`)
- 이미지 자동 업데이트 도구 (Renovate, Watchtower 등)
- 성능 설정 [미정] (view-distance 등)

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| 서버 이미지는 `compose.yaml`에 itzg 릴리스 태그(`<릴리스>-java25`)로 고정 | 재기동·pull 때 이미지가 예고 없이 바뀌지 않게. 읽기 쉽고 한 줄로 올릴 수 있음. 올린 이력이 커밋으로 남음 | 2026-11-23 |
| Paper 빌드는 고정하지 않음 | 같은 마크 버전 안 빌드는 월드와 호환되는 버그·보안 수정 | 2026-11-23 |
| 이미지 업데이트는 백업 후 태그 변경 PR로 | 문제 시 이전 태그로 되돌리기 쉬움 | 2026-11-23 |
| `2026.11.0-java25`로 고정하고 Java4Shell 완화 플래그를 `JVM_XX_OPTS`로 직접 넣음 (/task 중) | 실행 중 이미지와 같은 릴리스 태그가 없고, 가장 가까운 릴리스에는 완화가 빠져 있음. 다음 릴리스를 기다리지 않고 지금 고정 | 2026-11-23 |

## 진행 기록
- 2026-11-20 빈 기획 파일 생성 (/issue)
- 2026-11-23 기획 작성 (/plan)
- 2026-11-23 구현 (/task): `2026.11.0-java25` + 완화 플래그. 접속자 0명 확인 후 재생성, Paper 26.3-258 `Done (7.058s)`
