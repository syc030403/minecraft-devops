# #17 월드 백업 자동화

- 이슈: #17
- 브랜치: `feature/17-world-backup-timer`
- 종류: feature · 영역: area:backup
- 선행: 없음 (관련: #10)
- 함께 나눈 이슈: 없음

## 목적
월드가 깨지거나 실수로 망가져도 하루 이내 상태로 되돌릴 수 있게 한다. 백업은 매일 자동으로 돌고, 업그레이드 전 같은 때에는 직접 실행할 수 있다. 복구가 실제로 되는 것까지 확인한다. 마크 버전 업그레이드(decisions.md 2026-11-19)를 하려면 이 작업이 먼저 끝나야 한다.

## 규칙 / 변경 내용
- [확정] `scripts/world-backup.sh`
  - 서버가 실행 중이면 `docker exec mc rcon-cli`로 `save-off` → `save-all flush` 후 압축하고, `trap`으로 성공·실패와 관계없이 `save-on`을 보낸다
  - 서버가 꺼져 있으면 rcon 없이 그대로 압축한다 (파일이 바뀌지 않으므로 일관성 유지). 로그에 남긴다
  - `save-off`나 `save-all flush`가 실패하면 백업하지 않고 0이 아닌 종료 코드로 끝낸다 (trap으로 `save-on`은 시도)
  - `flock`으로 중복 실행을 막는다. 이미 실행 중이면 메시지를 남기고 종료 코드 0 (#10과 같음)
  - `set -euo pipefail`, shellcheck 통과
- [임시] 백업 대상: `data/` 전체에서 다시 받을 수 있는 것을 뺀다
  - 포함: `world/`, `plugins/`, `config/`, `server.properties`, `whitelist.json`, `ops.json`, `banned-*.json`, `usercache.json`, 그 밖의 설정 파일
  - 제외: `libraries/`, `versions/`, `cache/`, `logs/`, `*.jar`, `world/session.lock`
- [임시] 형식: `tar` + `zstd`, 파일 이름 `world-YYYYmmdd-HHMMSS.tar.zst`
  - 임시 이름(`.partial`)으로 쓰고, 끝나면 `mv`로 바꾼다. 실패하면 trap이 `.partial`을 지운다. 그래서 완성된 백업만 정식 이름을 가진다
- [확정] 저장 위치: 저장소 `backups/` (고정 경로, 설정으로 바꾸지 않음). 없으면 만든다. 이미 gitignore돼 있음
- [확정] 보관: 완성된 백업을 최근 7개만 남긴다 (`.env` 키: `BACKUP_KEEP`, 기본 7)
  - 정리는 백업이 성공한 뒤에만 한다
  - `backups/` 안에서 `world-*.tar.zst` 이름의 일반 파일만 지운다. 빈 변수 + `rm -rf`는 쓰지 않는다
  - `BACKUP_KEEP`가 1 이상의 정수가 아니면 설정 오류로 실패한다
- [확정] 주기: systemd 시스템 타이머로 매일 04:00 + 필요할 때 직접 실행
  - `deploy/systemd/world-backup.service.in`: oneshot, 일반 사용자, `After=docker.service`, `ProtectHome=read-only` + `ReadWritePaths=@REPO_DIR@/backups`
  - `deploy/systemd/world-backup.timer.in`: `OnCalendar=*-*-* 04:00:00`, `Persistent=true` (04:00에 꺼져 있었으면 켜진 뒤 실행)
  - 생성은 `scripts/render-systemd.sh`(수정하지 않음), 설치는 디렉터가 sudo로 한다
  - 직접 실행: `scripts/world-backup.sh` 또는 `sudo systemctl start world-backup.service`
  - 로그는 `journalctl -u world-backup`
- [확정] 복구는 자동화하지 않는다. 절차를 `03-backup.md`에 적는다 (서버 정지 → 현재 `data/` 보존 → 압축 풀기 → 기동). 운영 `data/`를 덮어쓰는 복구는 디렉터가 직접 한다
- [확정] 외부(오프사이트) 백업은 이번에 하지 않는다. 로드맵 [아이디어]로 남긴다
- `.env.example`: `BACKUP_KEEP=7`
- `.gitignore`: `*.tar.zst` 추가 (`backups/` 밖에 실수로 생긴 압축 파일 대비)

## 수용 기준
- [x] 성공: `shellcheck scripts/*.sh` 통과
- [x] 성공: 서버 실행 중 직접 실행하면 `backups/world-*.tar.zst`가 생기고 종료 코드 0. 로그 순서는 save-off → save-all flush → 압축 → save-on
- [x] 성공: 압축 파일에 `world/level.dat`, `whitelist.json`이 있고 `libraries/`, `*.jar`, `world/session.lock`은 없다 (`tar --zstd -tf`)
- [x] 성공: 백업을 테스트 디렉토리에 풀고 임시 컨테이너(포트 publish 없음)로 기동하면 `Done`이 나온다. 결과를 진행 기록에 남긴다 (V9) (2026-11-20 `Done (6.754s)`, seed·화이트리스트 운영 서버와 일치, 열린 포트 0)
- [x] 성공: 타이머 설치 후 `systemctl list-timers world-backup.timer`에 다음 실행 04:00이 보인다 (다음: 2026-11-21 04:00)
- [x] 성공: `sudo systemctl start world-backup.service`로 실행하면 `Result=success`이고 journal에 성공 기록이 남는다 (2026-11-20, ProtectHome=read-only + ReadWritePaths 환경에서 save-off~save-on 정상)
- [x] 실패·예외: 압축 중에 실패하면(예: 압축 명령을 일부러 실패시킴) 0이 아닌 종료 코드, `.partial`이 남지 않음, `save-on`이 실행됨
- [x] 실패·예외: `save-off`가 실패하면 백업 파일을 만들지 않고 0이 아닌 종료 코드
- [x] 실패·예외: `BACKUP_KEEP`가 0, 음수, 문자이면 설정 오류로 실패하고 아무것도 지우지 않는다
- [x] 경계: 서버가 꺼져 있어도 백업이 되고 종료 코드 0
- [x] 경계: 동시에 두 번 실행하면 하나는 flock으로 건너뛴다 (종료 코드 0)
- [x] 경계: 백업이 8개 이상 쌓이면 가장 오래된 것부터 지워 7개가 남는다. `backups/` 안의 다른 이름 파일은 지우지 않는다
- [x] 경계: 백업 후 서버에서 블록 설치·저장이 정상 동작한다 (save-on 복귀 확인: `save-all` 응답) (`save-all` → Saved the game, `save-on` → already turned on. 블록 설치는 접속자가 없어 미확인)
- [x] 문서: `03-backup.md` [미정] 정리 (주기·보관·위치·외부·실행 방식), 복구 절차 추가

## 지켜야 할 규칙
- verification.md: V3 (`.env` 커밋 금지), V4 (공개 파일, 홈 경로 — unit은 템플릿만), V5 (`backups/` git 제외), V7 (셸 스크립트), V8 (백업 일관성), V9 (복구 가능), V10 (삭제 경로 제한), V11 (flock), V13 (복구 테스트 기동)
- V2: RCON 포트는 열지 않고 `docker exec`만 쓴다
- V12: sshd·ufw·NetworkManager·logind는 건드리지 않음. unit 설치는 sudo라 디렉터가 실행
- decisions.md: 주기 작업은 셸 스크립트 + systemd 타이머, unit은 템플릿만 (2026-11-19), 업그레이드는 백업 후 (2026-11-19)

## 영향 범위 (예상)
- 새 파일: `scripts/world-backup.sh`, `deploy/systemd/world-backup.service.in`, `deploy/systemd/world-backup.timer.in`
- 수정: `.env.example`, `.gitignore`
- 로컬 (커밋 안 함): `.env` (`BACKUP_KEEP`), `backups/`, `/etc/systemd/system/` (디렉터 설치)
- 문서:
  - `systems/03-backup.md`: [미정] 정리, 관련 파일, 복구 절차
  - `00-overview.md`: 디렉토리 `backups/` [임시] 해제, 로드맵 4 상태, 외부 백업 [아이디어] 추가
  - `README.md`: 로드맵 상태, 기술 스택 표, 구성도, 디렉토리 설명 (디렉터 요청으로 추가)
  - `systems/01-server.md`: Paper 빌드 번호 255 → 256 (디렉터 요청, 실행 중 로그로 확인)
  - `player-guide.md`: 해당 없음 — 친구에게 보이는 변화 없음 (04:00 몇 초간 저장 중지는 체감 없음) [추론]
- Notion: 현재 구성(타이머·백업 경로), 원본 로그, 작업 회고(필수), 개념 정리(백업 일관성 save-off, systemd OnCalendar/Persistent)

## 확인 방법
- 자동:
  - `shellcheck scripts/*.sh`, `docker compose config -q`
  - 서버 실행 중 / 꺼진 상태에서 직접 실행
  - `tar --zstd -tf`로 포함·제외 확인
  - 압축 실패·`save-off` 실패 흉내(테스트용 환경변수나 PATH 덮어쓰기), `BACKUP_KEEP` 잘못된 값
  - 동시 실행 2개
  - 가짜 백업 파일 9개 + 다른 이름 파일 1개로 정리 확인
  - `git grep`으로 V4 문자열·홈 경로, `git grep -nE 'down -v|rm -rf'` (V10)
- 직접:
  - 테스트 복구: 테스트 디렉토리에 풀어 `docker run --rm` (포트 없음, 운영 `data/`와 분리)로 기동해 `Done` 확인
  - 디렉터가 sudo로 unit 설치·활성화
  - `systemctl list-timers world-backup.timer`, `journalctl -u world-backup`
  - 다음 날 04:00 자동 실행 기록 (`/task` 안에서 못 보면 못 봤다고 적음)
  - 백업 후 서버에서 `save-all` 응답과 플레이 정상

## 범위 밖
- 외부(오프사이트) 백업 — 비용·계정 검토 후 별도 이슈 (로드맵 [아이디어])
- 운영 `data/`를 덮어쓰는 복구 스크립트
- 백업 실패 알림 (모니터링 이슈에서)
- 마크 버전 업그레이드 (이 작업 이후 별도 이슈)
- `render-systemd.sh` 수정

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| 백업은 매일 04:00 systemd 타이머 + 직접 실행 | 하루치 손실은 감수 가능, 접속이 없는 시간, 업그레이드 전에는 직접 실행 | 2026-11-20 |
| 보관은 최근 7개 (`BACKUP_KEEP`) | 개수 기준이 단순하고, 실패한 날이 있어도 정상 백업 7개가 남음 | 2026-11-20 |
| 저장 위치는 저장소 `backups/` 고정 | 이미 gitignore, 경로가 고정이라 삭제 범위를 제한하기 쉬움 | 2026-11-20 |
| 외부 백업은 이번에 하지 않음 | 비용·계정 확인 필요, 로드맵 [아이디어]로 | 2026-11-20 |
| 대상은 `data/`에서 다시 받을 수 있는 것을 뺀 전체 | 월드뿐 아니라 화이트리스트·설정도 복구해야 함, 용량 241M → 수십 MB | 2026-11-20 |
| 서버가 꺼져 있으면 rcon 없이 백업 | 파일이 바뀌지 않아 일관성 유지, 점검 중에도 백업 가능 | 해당 없음 |
| 복구는 절차 문서만, 스크립트 없음 | 운영 데이터를 덮어쓰는 일이라 사람이 직접 | 해당 없음 |
| 형식은 tar + zstd | 설치돼 있고 gzip보다 빠름 | 해당 없음 |
| 잠금 파일은 `backups/.lock` | 직접 실행과 타이머가 `TMPDIR`과 관계없이 같은 잠금을 씀, 서비스가 쓸 수 있는 유일한 경로 | 해당 없음 |
| `BACKUP_KEEP`가 비어 있으면 7, `07`처럼 0으로 시작하면 오류 | `.env.example`과 같은 기본값, 8진수 해석 같은 혼동 방지 | 해당 없음 |
| docker 상태를 확인할 수 없으면 백업하지 않음 (종료 코드 2) | 서버가 실행 중인데 저장 명령 없이 압축하는 경우를 막음 | 해당 없음 |
| save-on 실패는 종료 코드 4 | 백업은 됐어도 자동 저장이 꺼진 채 남으면 알아야 함 | 해당 없음 |

## 진행 기록
- 2026-11-20 빈 기획 파일 생성 (/issue)
- 2026-11-20 기획 작성 (/plan)
- 2026-11-20 구현 (/task): `world-backup.sh`, unit 템플릿 2개, 문서. 실제 백업 9.8M(129개 항목), 가짜 저장소에서 실패·경계 시험(압축 실패·save-off 실패·flush 응답 이상·서버 꺼짐·컨테이너 없음·docker 접근 실패·KEEP 검사·정리·동시 실행) 통과. 복구 시험: 임시 컨테이너(포트 없음) `Done`, seed·화이트리스트 일치. 디렉터가 unit 설치, 서비스 실행 Result=success, 다음 실행 04:00 확인
- 2026-11-20 디렉터 요청: README 기술 스택·구성도·디렉토리 설명에 백업 추가, `01-server.md` Paper 빌드 256으로 정정
