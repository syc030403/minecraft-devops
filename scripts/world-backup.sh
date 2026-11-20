#!/usr/bin/env bash
# 월드 데이터(data/)를 backups/ 에 tar+zstd로 백업하고 오래된 백업을 정리한다.
#
# 사용: scripts/world-backup.sh
# 설정: 저장소 루트 .env 의 BACKUP_KEEP (남길 백업 개수, 없으면 7)
#
# 서버(mc 컨테이너)가 실행 중이면 save-off + save-all flush 후 압축하고, 끝나면(실패해도) save-on.
# 서버가 꺼져 있으면 파일이 바뀌지 않으므로 그대로 압축한다.
#
# 종료 코드: 0 성공(또는 이미 실행 중이라 건너뜀), 1 설정 오류, 2 서버 저장 명령 실패,
#            3 압축 실패, 4 save-on 실패(자동 저장이 꺼진 채 남았을 수 있음)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$REPO_DIR/.env"
DATA_DIR="$REPO_DIR/data"
BACKUP_DIR="$REPO_DIR/backups"
LOCK_FILE="$BACKUP_DIR/.lock"
CONTAINER="mc"
DEFAULT_KEEP=7
# 정식 백업 파일 이름. 정리할 때 이 형식만 지운다
NAME_RE='^world-[0-9]{8}-[0-9]{6}\.tar\.zst$'

log() { echo "world-backup: $*"; }
err() { echo "world-backup: 오류: $*" >&2; }

if [[ $# -ne 0 ]]; then
  echo "사용법: $0" >&2
  exit 1
fi

# .env를 source하지 않고 필요한 키만 읽는다 (임의 코드 실행 방지)
read_env() {
  local key="$1" value=""
  if [[ -r "$ENV_FILE" ]]; then
    value="$(sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n 1)"
    value="${value%\"}"; value="${value#\"}"
    value="${value%\'}"; value="${value#\'}"
  fi
  printf '%s' "$value"
}

KEEP="$(read_env BACKUP_KEEP)"
KEEP="${KEEP:-$DEFAULT_KEEP}"
if [[ ! "$KEEP" =~ ^[1-9][0-9]*$ ]]; then
  err "BACKUP_KEEP는 1 이상의 정수여야 합니다 (현재: '$KEEP')"
  exit 1
fi

if [[ ! -d "$DATA_DIR/world" ]]; then
  err "월드 디렉토리가 없습니다: data/world"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "이미 실행 중이라 건너뜁니다"
  exit 0
fi

# 서버 상태: running이면 저장 명령을 보낸다. docker에 닿지 못하면 상태를 모르므로 중단
if ! state="$(docker ps -a --filter "name=^${CONTAINER}\$" --format '{{.State}}' 2>&1)"; then
  err "docker 상태를 확인할 수 없습니다: $state"
  exit 2
fi

stamp="$(date +%Y%m%d-%H%M%S)"
name="world-${stamp}.tar.zst"
target="$BACKUP_DIR/$name"
partial="$BACKUP_DIR/.${name}.partial"
if [[ -e "$target" ]]; then
  err "같은 이름의 백업이 이미 있습니다: $name"
  exit 3
fi

save_off_sent=0
cleanup() {
  local rc=$?
  rm -f -- "$partial"
  if [[ "$save_off_sent" -eq 1 ]]; then
    if docker exec "$CONTAINER" rcon-cli save-on >/dev/null 2>&1; then
      log "save-on"
    else
      err "save-on 실패. 직접 실행하세요: docker exec $CONTAINER rcon-cli save-on"
      [[ "$rc" -eq 0 ]] && rc=4
    fi
  fi
  exit "$rc"
}
trap cleanup EXIT

rcon() { docker exec "$CONTAINER" rcon-cli "$@" 2>&1; }

if [[ "$state" == "running" ]]; then
  save_off_sent=1
  if ! out="$(rcon save-off)"; then
    err "save-off 실패: $out"
    exit 2
  fi
  log "save-off"
  if ! out="$(rcon save-all flush)" || [[ "$out" != *"Saved the game"* ]]; then
    err "save-all flush 실패: $out"
    exit 2
  fi
  log "save-all flush"
else
  log "서버가 실행 중이 아니라 저장 명령 없이 백업합니다 (상태: ${state:-없음})"
fi

# 다시 받을 수 있는 것(라이브러리, 서버 jar, 캐시, 로그)은 뺀다.
# --anchored + --no-wildcards-match-slash: data/ 바로 아래 항목만 제외 (plugins/ 안 jar는 포함)
log "압축 시작: $name"
if ! tar --create --zstd --file "$partial" -C "$DATA_DIR" \
    --anchored --no-wildcards-match-slash \
    --exclude='./libraries' --exclude='./versions' --exclude='./cache' \
    --exclude='./logs' --exclude='./*.jar' --exclude='./world/session.lock' \
    .; then
  err "압축 실패"
  exit 3
fi
mv -- "$partial" "$target"
log "백업 완료: backups/$name ($(du -h "$target" | cut -f1))"

# 정리: backups/ 바로 아래, 정식 이름 형식의 일반 파일만. 이름에 시각이 있어 정렬 = 시간순
mapfile -t backups < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'world-*.tar.zst' -printf '%f\n' \
  | grep -E "$NAME_RE" | sort)
remove=$(( ${#backups[@]} - KEEP ))
for (( i = 0; i < remove; i++ )); do
  rm -f -- "${BACKUP_DIR:?}/${backups[i]}"
  log "오래된 백업 삭제: ${backups[i]}"
done
log "보관 중: $(( ${#backups[@]} - (remove > 0 ? remove : 0) ))개 (최대 $KEEP)"
