# 항상 지켜야 할 규칙과 확인 방법

기획 파일 "지켜야 할 규칙"에는 이 문서의 번호(V1…)를 적는다.
"자동"은 명령으로 확인, "직접"은 사람이 서버·외부망에서 확인. 직접 확인을 못 했으면 보고에 못 했다고 적는다.

| 번호 | 규칙 | 확인 방법 | 종류 |
| --- | --- | --- | --- |
| V1 | 외부(인터넷) 공개 포트는 마크 서버 포트 하나뿐 | `docker compose config`의 `ports`에서 `host_ip`가 없거나 `0.0.0.0`인 것이 마크 서버 포트 하나인지. 나머지는 `127.0.0.1` 또는 Tailscale IP | 자동 |
| V2 | RCON(25575)은 `ports`에 없음 | `docker compose config`의 `ports`에 25575가 없는지 | 자동 |
| V3 | 비밀값이 git에 없음 | `git ls-files .env` 출력이 비어 있음. `git diff --cached`에 토큰·비밀번호 없음. 새 키는 `.env.example`에 이름만 | 자동 |
| V4 | 공개 파일에 로컬 정보가 없음 | `CLAUDE.local.md`의 "공개 파일 점검용 문자열" 각각으로 `git grep -nF '<값>'` 결과가 비어 있음. `git ls-files CLAUDE.local.md` 비어 있음 | 자동 |
| V5 | 월드 데이터가 git에 없음 | `git ls-files data/ backups/` 출력이 비어 있음 | 자동 |
| V6 | compose 문법이 맞음 | `docker compose config -q` | 자동 |
| V7 | 셸 스크립트 규칙 | `shellcheck scripts/*.sh` 통과, `set -euo pipefail` 있음 | 자동 |
| V8 | 백업 일관성 | 백업 전 `save-off` + `save-all flush`, `trap`으로 `save-on` 보장. 코드 확인 + 실행 로그 | 자동+직접 |
| V9 | 백업은 복구 가능 | 테스트 위치에 복구 후 서버 기동 확인. 기획 파일 진행 기록에 남김 | 직접 |
| V10 | 데이터 파괴 명령 없음 | `git grep -nE 'down -v|rm -rf'` 결과 검토. 삭제 경로는 고정 디렉토리 안으로 제한 | 자동 |
| V11 | 주기 작업 중복 실행 방지 | 주기 실행 스크립트에 `flock` 있음 | 자동 |
| V12 | 원격 접속을 끊을 수 있는 변경은 승인 후 | sshd·ufw·NetworkManager·logind 변경은 기획·PR에 명령과 되돌리는 방법이 있고 디렉터가 실행 | 직접 |
| V13 | 서버가 정상 기동 | `docker compose up -d` → `docker logs mc --tail 50`에 `Done` | 직접 |
| V14 | 친구가 접속 가능 | 외부망에서 화이트리스트 계정으로 접속, 비화이트리스트 계정은 거부 | 직접 |
