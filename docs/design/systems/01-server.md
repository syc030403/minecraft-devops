# 01. 서버 (`area:server`)

마크 서버 컨테이너의 정의와 설정.

## 사양
- [확정] 이미지: `itzg/minecraft-server`, 컨테이너 이름 `mc`
- [확정] `TYPE=PAPER`, `MEMORY=6G`, `TZ=Asia/Seoul`
- [확정] 버전: `.env`의 `MC_VERSION`에 고정. 현재 26.3 (Paper 26.3-256, 2026-11-20 기동 로그로 확인. 첫 기동은 255였고 컨테이너를 다시 만들 때 같은 26.3 안에서 빌드가 올라감). 업그레이드는 백업 후 별도 이슈
- [확정] `ONLINE_MODE=TRUE` (정품 계정만)
- [확정] `ENABLE_WHITELIST` + `ENFORCE_WHITELIST=TRUE`
- [확정] `EULA=TRUE` (Minecraft EULA 동의)
- [확정] 포트: `.env`의 `MC_PORT`(값은 `CLAUDE.local.md`) → 컨테이너 25565. 포트 규칙은 `02-network.md`
- [확정] 월드 데이터는 `./data`에 마운트, git에 넣지 않음
- [임시] `restart: unless-stopped`, `stop_grace_period: 1m`
- [확정] 이미지 태그: `compose.yaml`에 itzg 릴리스 태그로 고정. 현재 `2026.11.0-java25` (2026-11-23). 마크 버전은 `MC_VERSION`으로 따로 고정하고, 같은 마크 버전 안의 Paper 빌드(`PAPER_BUILD`)는 고정하지 않음
- [임시] `JVM_XX_OPTS=-XX:-UseBASE64Intrinsics`: Java4Shell(CVE-2026-114938) 완화. `2026.11.0`에는 이미지 자동 적용이 없어서 직접 넣음. 자동 적용(`FIX_JAVA4SHELL_EXPLOIT`, itzg PR #4400)이 들어간 릴리스로 올릴 때 뺀다

## 규칙
- [확정] 서버 설정은 `data/` 안 파일(`server.properties` 등)을 직접 고치지 않고 `compose.yaml` 환경변수로 관리한다.
- [확정] RCON은 컨테이너 내부에서만 쓴다 (`docker exec mc rcon-cli ...`). 비밀번호는 이미지가 자동 생성.
- [확정] 화이트리스트 닉네임은 공개 파일에 쓰지 않는다.
- [미정] view-distance, simulation-distance 등 성능 설정
- [확정] 이미지는 `latest`나 Java 변형 태그(`java25` 등)처럼 움직이는 태그를 쓰지 않는다. 올릴 때는 아래 "이미지 업데이트" 절차를 따르고 PR로 반영한다.

## 이미지 업데이트
1. 백업: `sudo systemctl start world-backup.service` → `systemctl show world-backup.service -p Result`가 `success`인지 확인
2. itzg 릴리스 노트 확인 (Java 변형 변경, 깨지는 변경, 이미지가 자동으로 넣게 된 설정)
3. 작업 브랜치에서 `compose.yaml`의 태그를 바꾼다
4. `docker compose pull` (태그가 없으면 여기서 실패하고, 돌고 있는 컨테이너는 그대로) → `docker compose up -d`
5. `docker logs mc --tail 50`에 `Done`, 버전이 `MC_VERSION`과 같은지 확인
6. 문제가 있으면 이전 태그로 되돌리고 `docker compose up -d`. 마크 버전이 그대로라 월드는 영향 없음
7. 이미지 태그를 바꾸면 컨테이너를 다시 만들어 1분 안팎 끊기므로 접속자가 없을 때 한다

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
