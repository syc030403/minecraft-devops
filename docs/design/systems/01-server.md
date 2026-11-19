# 01. 서버 (`area:server`)

마크 서버 컨테이너의 정의와 설정.

## 사양
- [확정] 이미지: `itzg/minecraft-server`, 컨테이너 이름 `mc`
- [확정] `TYPE=PAPER`, `VERSION=LATEST`, `MEMORY=8G`, `TZ=Asia/Seoul`
- [확정] `ONLINE_MODE=TRUE` (정품 계정만)
- [확정] `WHITELIST` + `ENFORCE_WHITELIST=TRUE`
- [확정] 포트: 외부 포트(값은 `CLAUDE.local.md`) → 컨테이너 25565. 포트 규칙은 `02-network.md`.
- [확정] 월드 데이터는 `./data`에 마운트, git에 넣지 않음

## 규칙
- [확정] 서버 설정은 `data/` 안 파일(`server.properties` 등)을 직접 고치지 않고 `compose.yaml` 환경변수로 관리한다.
- [확정] RCON은 컨테이너 내부에서만 쓴다 (`docker exec mc rcon-cli ...`).
- [미정] 재시작 정책 (`restart: unless-stopped` 등)
- [미정] `VERSION=LATEST` 유지 vs 버전 고정 (자동 업데이트로 플러그인·월드 호환 문제가 생길 수 있음)
- [미정] view-distance, simulation-distance 등 성능 설정
- [미정] 외부 포트를 `compose.yaml`에 직접 쓸지 `.env`로 뺄지 (공개 저장소)

## 운영 명령
- 화이트리스트 추가: `docker exec mc rcon-cli whitelist add 닉네임`
- 상태: `docker compose ps`, `docker logs mc --tail 100`

## 관련 파일
- `compose.yaml` (작성 전)
- `.env.example` (작성 전)

## 확인 방법
- `docker compose config -q`
- `docker compose up -d` → `docker logs mc`에 `Done` 출력
- verification.md: V1, V2, V5, V6, V13, V14
