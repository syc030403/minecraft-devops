# 03. 백업 (`area:backup`)

월드 백업, 보관, 복구.

## 규칙
- [확정] 백업 전에 `save-off` + `save-all flush`, 끝나거나 실패해도 `save-on` (trap으로 보장).
- [확정] 주기 실행은 `flock`으로 중복 실행을 막는다.
- [확정] 오래된 백업 정리는 백업 디렉토리 안의 백업 파일만 지운다 (빈 변수 + `rm -rf` 금지).
- [확정] 백업 결과물은 git에 넣지 않는다.
- [확정] 복구가 실제로 되는지 확인한 기록이 있어야 "백업 완료"로 본다.
- [확정] 주기: 매일 04:00 systemd 시스템 타이머 (`Persistent=true`, 그 시각에 꺼져 있었으면 켜진 뒤 실행) + 필요할 때 직접 실행 (업그레이드 전 등)
- [확정] 보관: 완성된 백업을 최근 7개만 남긴다 (`.env`의 `BACKUP_KEEP`). 정리는 백업이 성공한 뒤에만
- [확정] 저장 위치: 저장소 `backups/` 고정 (설정으로 바꾸지 않음)
- [확정] 외부(오프사이트) 백업은 하지 않는다. 비용·계정 검토 후 별도 이슈 (로드맵 [아이디어])
- [확정] 실행 방식: 셸 스크립트 + systemd 시스템 타이머 (decisions.md 2026-11-19)
- [임시] 대상: `data/`에서 다시 받을 수 있는 것을 뺀 전체
  - 제외: `libraries/`, `versions/`, `cache/`, `logs/`, `data/` 바로 아래 `*.jar`, `world/session.lock`
  - 포함: 월드, `plugins/`(안의 jar 포함), `config/`, `server.properties`, `whitelist.json`, `ops.json` 등
- [임시] 형식: `tar` + `zstd`, `backups/world-YYYYmmdd-HHMMSS.tar.zst`. 임시 이름(`.…partial`)으로 쓰고 끝나면 이름을 바꿔, 정식 이름은 완성된 백업만 가진다
- [확정] 서버가 꺼져 있으면 저장 명령 없이 백업한다 (파일이 바뀌지 않음). docker 상태를 확인할 수 없으면 백업하지 않고 실패

## 운영 명령
- 직접 백업: `scripts/world-backup.sh` (또는 `sudo systemctl start world-backup.service`)
- 목록: `ls -lh backups/`
- 내용 확인: `tar --zstd -tf backups/world-<시각>.tar.zst`
- 로그: `journalctl -u world-backup`
- 다음 실행: `systemctl list-timers world-backup.timer`
- 종료 코드: 0 성공·건너뜀, 1 설정 오류, 2 서버 저장 명령 실패, 3 압축 실패, 4 save-on 실패

## 타이머 설치
1. `backups/`가 있어야 서비스가 시작된다 (`ReadWritePaths`). 처음 한 번 `scripts/world-backup.sh`를 직접 실행한다
2. `scripts/render-systemd.sh` → `build/systemd/`에 unit 생성
3. 출력된 sudo 명령을 디렉터가 직접 실행 (`install`, `daemon-reload`, `enable --now world-backup.timer`)

## 복구 절차 (운영 데이터를 덮어쓰므로 디렉터가 직접)
1. 서버 정지: `docker compose down` (`-v` 금지)
2. 현재 데이터 보존: `mv data data.before-restore-<날짜>` (확인 후 디렉터가 지움)
3. 풀기: `mkdir data && tar --zstd -xf backups/world-<시각>.tar.zst -C data`
4. 기동: `docker compose up -d` → `docker logs mc --tail 50`에 `Done`. jar·라이브러리는 기동할 때 다시 받는다
5. 접속해서 월드·화이트리스트 확인

복구 시험(운영과 분리): 백업을 임시 디렉토리에 풀고 포트 없이 임시 컨테이너로 기동해 `Done` 확인.
```
docker run -d --rm --name mc-restore-test -v <임시디렉토리>:/data \
  -e EULA=TRUE -e TYPE=PAPER -e VERSION=<MC_VERSION> -e MEMORY=2G itzg/minecraft-server:latest
```

## 관련 파일
- `scripts/world-backup.sh`
- `deploy/systemd/world-backup.service.in`, `deploy/systemd/world-backup.timer.in`
- `.env.example` (`BACKUP_KEEP`)

## 확인 방법
- `shellcheck scripts/*.sh`
- 백업 실행 → 파일 생성 확인 → 테스트 위치에 복구 → 서버 기동 확인
- verification.md: V7, V8, V9, V10, V11
