# 02. 네트워크 (`area:network`)

포트 공개, 방화벽, 원격 접속, DDNS.

## 포트 공개
- [확정] Docker로 publish한 포트는 ufw를 우회한다.
- [확정] 외부(인터넷) 공개는 마크 서버 포트 하나만.
- [확정] 그 외 서비스는 `127.0.0.1:포트:포트` 또는 Tailscale IP로 바인딩.
- [확정] RCON(25575)은 `ports`에 절대 넣지 않는다.

## 원격 접속
- [확정] 원격 관리는 Tailscale로만. SSH는 키 인증만.
- [확정] sshd·ufw·NetworkManager·logind 변경은 원격 접속을 끊을 수 있다. 명령을 보여주고 디렉터 승인 후 디렉터가 실행.
- 상세 설정 값은 `CLAUDE.local.md` (공개 금지).

## DDNS
- [확정] DuckDNS로 유동 공인 IP를 도메인에 연결한다.
- [확정] DuckDNS 토큰은 `.env`에 둔다. 로그·커밋에 남기지 않는다.
- [미정] 갱신 방식: 스크립트 + cron/systemd 타이머 vs 컨테이너
- [미정] 갱신 주기
- [미정] 도메인을 공개 문서에 적을지 (공개하면 서버 주소가 노출됨)

## 관련 파일
- `compose.yaml`의 `ports`
- `scripts/` DDNS 스크립트 (작성 전)

## 확인 방법
- `docker compose config`의 `ports` 확인
- `ss -tlnp`로 호스트에서 열린 포트 확인
- 외부망(휴대폰 데이터 등)에서 접속 테스트
- verification.md: V1, V2, V3, V4, V12
