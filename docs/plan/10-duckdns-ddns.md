# #10 DuckDNS로 유동 IP 대응

- 이슈: #10
- 브랜치: `feature/10-duckdns-ddns`
- 종류: feature · 영역: area:network
- 선행: 없음 (관련: #1)
- 함께 나눈 이슈: 없음

## 목적
유동 공인 IP가 바뀌어도 친구들이 같은 도메인으로 접속할 수 있게, 노트북이 DuckDNS를 자동으로 갱신한다. 이 작업의 스크립트·타이머 방식은 이후 주기 작업(백업)의 기준이 된다.

## 규칙 / 변경 내용
- [확정] `scripts/duckdns-update.sh`
  - `.env`의 `DUCKDNS_DOMAIN`, `DUCKDNS_TOKEN`을 읽는다. 값이 없으면 메시지와 함께 실패
  - DuckDNS update API를 `ip=` 비움으로 호출한다. DuckDNS가 요청을 보낸 공인 IP로 갱신
  - 응답 `OK`면 종료 코드 0, `KO`나 네트워크 오류면 0이 아닌 종료 코드
  - 토큰은 출력, 로그, 프로세스 목록(`ps`)에 남기지 않는다. curl에 URL을 인자로 넘기지 않고 표준 입력 설정(`curl -K -`)으로 전달하며, `set -x`는 쓰지 않는다
  - `flock`으로 중복 실행을 막는다. 이미 실행 중이면 메시지를 남기고 종료 코드 0
  - `--dry-run`: 설정 검사와 요청 내용(토큰은 가림)만 출력하고, 네트워크 호출은 하지 않는다
  - `set -euo pipefail`, shellcheck 통과
- [확정] systemd 시스템 타이머
  - `deploy/systemd/duckdns-update.service.in`: oneshot, 실행 사용자는 일반 사용자, network-online 이후
  - `deploy/systemd/duckdns-update.timer.in`: 부팅 1분 뒤, 이후 5분마다
  - 템플릿의 사용자·경로 자리표시자를 `scripts/render-systemd.sh`가 채워 `build/systemd/`에 생성한다. `build/`는 gitignore
  - 설치·활성화는 sudo가 필요하다. Claude는 명령만 제시하고 디렉터가 실행한다
  - 로그는 `journalctl -u duckdns-update`
- [확정] IPv4만 갱신. 유선 인터페이스에 공인 IPv6가 없음 (2026-11-19 확인)
- [확정] 도메인은 공개 문서에 쓰지 않는다. 실제 값은 `.env`와 `CLAUDE.local.md`. 친구에게는 메시지로 전달
- `.env.example`: `DUCKDNS_DOMAIN=`, `DUCKDNS_TOKEN=` (값 없이)
- 함께 기록 (이슈 메모): 로드맵에 [아이디어] 4개 추가 — 공유기 도입 검토, GUI 끄기, Ubuntu Server 이전, 호스트 설정 자동화

## 수용 기준
- [ ] 성공: `shellcheck scripts/*.sh` 통과
- [ ] 성공: `--dry-run`이 설정을 검사하고 토큰을 가린 요청만 출력한다 (네트워크 호출 없음)
- [ ] 성공: 실제 실행 시 DuckDNS 응답 `OK`, 종료 코드 0. 이후 도메인 조회 결과가 유선 공인 IP와 같다
- [ ] 성공: 타이머 설치 후 `systemctl list-timers`에 다음 실행이 보이고, 5분 뒤 `journalctl`에 성공 기록이 남는다
- [ ] 성공: 도메인:포트로 외부망에서 접속 (디렉터)
- [ ] 실패·예외: `.env`에 값이 없으면 메시지와 함께 0이 아닌 종료 코드
- [ ] 실패·예외: 잘못된 토큰이면 `KO`로 0이 아닌 종료 코드, 출력에 토큰 없음
- [ ] 경계: 동시에 두 번 실행하면 하나는 flock으로 건너뛴다
- [ ] 경계: 실행 출력, journal, `ps`에 토큰이 나타나지 않는다
- [ ] 경계: 공개 파일에 토큰, 도메인, 사용자 홈 경로가 없다 (V4 문자열 포함)
- [ ] 성공: `00-overview.md` 로드맵에 [아이디어] 4개 추가

## 지켜야 할 규칙
- verification.md: V3 (비밀값), V4 (공개 파일), V7 (셸 스크립트), V11 (중복 실행 방지)
- V12: sshd·ufw·NetworkManager·logind는 건드리지 않음. systemd unit 설치는 sudo라 디렉터가 실행
- decisions.md: 공개 저장소, 호스트 정보 분리 (2026-11-18)

## 영향 범위 (예상)
- 새 파일: `scripts/duckdns-update.sh`, `scripts/render-systemd.sh`, `deploy/systemd/duckdns-update.service.in`, `deploy/systemd/duckdns-update.timer.in`
- 수정: `.env.example`, `.gitignore` (`build/`)
- 로컬 (커밋 안 함): `.env` (도메인·토큰), `/etc/systemd/system/` (디렉터 설치)
- 문서:
  - `systems/02-network.md`: DDNS [미정] 정리
  - `00-overview.md`: 디렉토리, 로드맵 [아이디어] 4개
  - `README.md`: 기술 스택 DuckDNS "사용 중", 로드맵 상태
- Notion: 현재 구성(서비스·타이머), 원본 로그, 작업 회고(필수), 개념 정리(DDNS, systemd 타이머)

## 확인 방법
- 자동:
  - `shellcheck scripts/*.sh`
  - `--dry-run`
  - 값이 빈 `.env`로 실패 확인
  - 가짜 토큰으로 `KO` 확인
  - 동시 실행 2개
  - 출력·journal에서 토큰 grep (값을 출력하지 않고 개수만)
  - 공개 파일 점검: `git grep` (V4 문자열, `/home/`)
- 직접:
  - 디렉터가 sudo로 unit 설치·활성화
  - `systemctl list-timers`, `journalctl -u duckdns-update`
  - 도메인 조회 결과와 유선 공인 IP 비교
  - 외부망에서 도메인:포트로 접속

## 범위 밖
- IPv6(AAAA) 갱신
- 공유기 도입, GUI 끄기, Ubuntu Server 이전, 호스트 설정 자동화 (로드맵 [아이디어]로만 기록)
- 백업 (로드맵 4)
- 재부팅 후 자동 실행의 실제 확인 (재부팅은 서버가 멈추는 일이라, 디렉터가 원할 때 별도로)

## 이 기획에서 내린 결정
| 결정 | 이유 | decisions.md |
| --- | --- | --- |
| 갱신은 셸 스크립트 + systemd 시스템 타이머 (부팅 1분 뒤, 5분마다) | 로그인 없이 동작, journal 로그, 실무 방식. 이후 주기 작업의 기준 | 2026-11-19 |
| unit 파일은 저장소에 템플릿만 두고 설치할 때 생성 | 공개 저장소에 사용자 이름·홈 경로를 남기지 않음 | 2026-11-19 |
| 도메인은 공개 문서에 쓰지 않음 | 서버 주소+포트가 공개되면 스캔·공격 대상이 되기 쉬움 | 2026-11-19 |
| IPv4만 갱신 | 공인 IPv6가 없음 | 해당 없음 |

## 진행 기록
- 2026-11-19 빈 기획 파일 생성 (/issue)
- 2026-11-19 기획 작성 (/plan)
