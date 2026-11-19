# 01. 서버 (`area:server`)

마크 서버 컨테이너의 정의와 설정.

## 사양
- [확정] 이미지: `itzg/minecraft-server`, 컨테이너 이름 `mc`
- [확정] `TYPE=PAPER`, `MEMORY=6G`, `TZ=Asia/Seoul`
- [확정] 버전: `.env`의 `MC_VERSION`에 고정. 현재 26.3 (Paper 26.3-255). 업그레이드는 백업 후 별도 이슈
- [확정] `ONLINE_MODE=TRUE` (정품 계정만)
- [확정] `ENABLE_WHITELIST` + `ENFORCE_WHITELIST=TRUE`
- [확정] `EULA=TRUE` (Minecraft EULA 동의)
- [확정] 포트: `.env`의 `MC_PORT`(값은 `CLAUDE.local.md`) → 컨테이너 25565. 포트 규칙은 `02-network.md`
- [확정] 월드 데이터는 `./data`에 마운트, git에 넣지 않음
- [임시] `restart: unless-stopped`, `stop_grace_period: 1m`
- [임시] 이미지 태그 `latest` (마크 버전은 `MC_VERSION`으로 따로 고정)

## 규칙
- [확정] 서버 설정은 `data/` 안 파일(`server.properties` 등)을 직접 고치지 않고 `compose.yaml` 환경변수로 관리한다.
- [확정] RCON은 컨테이너 내부에서만 쓴다 (`docker exec mc rcon-cli ...`). 비밀번호는 이미지가 자동 생성.
- [확정] 화이트리스트 닉네임은 공개 파일에 쓰지 않는다.
- [미정] view-distance, simulation-distance 등 성능 설정
- [미정] 이미지 태그 고정 여부

## 운영 명령
- 기동·재생성: `docker compose up -d`
- 정지: `docker compose down` (`-v` 금지)
- 화이트리스트: `docker exec mc rcon-cli whitelist add 닉네임`, `whitelist list`
- 상태: `docker compose ps`, `docker logs mc --tail 100`

## 관련 파일
- `compose.yaml`
- `.env.example` (`MC_PORT`, `MC_VERSION`)

## 확인 방법
- `docker compose config -q`
- `docker compose up -d` → `docker logs mc`에 `Done` 출력
- verification.md: V1, V2, V5, V6, V13, V14
