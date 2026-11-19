# 02. 네트워크 (`area:network`)

포트 공개, 방화벽, 원격 접속, DDNS.

## 포트 공개
- [확정] Docker로 publish한 포트는 ufw를 우회한다.
- [확정] 외부(인터넷) 공개는 마크 서버 포트 하나만.
- [확정] 그 외 서비스는 `127.0.0.1:포트:포트` 또는 Tailscale IP로 바인딩.
- [확정] RCON(25575)은 `ports`에 절대 넣지 않는다.
- [확정] 마크 서버 포트는 `.env`의 `MC_PORT`로 지정한다 (`compose.yaml`에 실제 값을 쓰지 않음).
- [확정] 공인 IP 직결이라 공유기 포트포워딩은 없다. Docker publish가 ufw를 우회하므로 ufw 규칙 추가도 필요 없다.
- [임시] publish는 IPv4(`0.0.0.0`)와 IPv6(`[::]`) 모두에 열린다.

## 원격 접속
- [확정] 원격 관리는 Tailscale로만. SSH는 키 인증만.
- [확정] sshd·ufw·NetworkManager·logind 변경은 원격 접속을 끊을 수 있다. 명령을 보여주고 디렉터 승인 후 디렉터가 실행.
- 상세 설정 값은 `CLAUDE.local.md` (공개 금지).

## DDNS
- [확정] DuckDNS로 유동 공인 IP를 도메인에 연결한다.
- [확정] DuckDNS 토큰은 `.env`에 둔다. 로그·커밋에 남기지 않는다.
- [확정] 갱신: `scripts/duckdns-update.sh` + systemd 시스템 타이머 `duckdns-update.timer` (부팅 1분 뒤, 이후 5분마다)
- [확정] `ip=`를 비워 요청을 보낸 공인 IP로 갱신. IPv4만 (유선에 공인 IPv6 없음)
- [확정] 도메인은 공개 문서에 쓰지 않는다. 실제 값은 `.env`(`DUCKDNS_DOMAIN`)와 `CLAUDE.local.md`. 친구에게는 메시지로 전달
- [확정] 토큰은 curl 설정을 표준 입력으로 넘겨 출력·로그·프로세스 인자에 남기지 않는다
- [확정] unit 파일은 `deploy/systemd/*.in` 템플릿에서 `scripts/render-systemd.sh`로 생성(`build/`, gitignore). 설치는 디렉터가 sudo로
- 운영 명령
  - 상태: `systemctl list-timers duckdns-update.timer`
  - 로그: `journalctl -u duckdns-update.service`
  - 수동 갱신: `scripts/duckdns-update.sh` (설정만 확인: `--dry-run`)
  - 토큰 재발급 후: `.env`의 `DUCKDNS_TOKEN` 교체

## 관련 파일
- `compose.yaml`의 `ports`
- `scripts/duckdns-update.sh`, `scripts/render-systemd.sh`
- `deploy/systemd/duckdns-update.service.in`, `duckdns-update.timer.in`

## 확인 방법
- `docker compose config`의 `ports` 확인
- `ss -tlnp`로 호스트에서 열린 포트 확인
- 외부망(휴대폰 데이터 등)에서 접속 테스트
- verification.md: V1, V2, V3, V4, V12
