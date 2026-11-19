#!/usr/bin/env bash
# DuckDNS 도메인을 이 호스트의 현재 공인 IPv4로 갱신한다.
#
# 사용: scripts/duckdns-update.sh [--dry-run]
# 설정: 저장소 루트 .env 의 DUCKDNS_DOMAIN(서브도메인만), DUCKDNS_TOKEN
#
# 종료 코드: 0 성공(또는 이미 실행 중이라 건너뜀), 1 설정 오류, 2 DuckDNS가 KO 응답, 3 네트워크 오류
# 토큰은 출력·로그·프로세스 인자에 남기지 않는다 (curl 설정을 표준 입력으로 전달).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${ENV_FILE:-$REPO_DIR/.env}"
LOCK_FILE="${LOCK_FILE:-${TMPDIR:-/tmp}/duckdns-update.lock}"

DRY_RUN=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY_RUN=1 ;;
  *) echo "사용법: $0 [--dry-run]" >&2; exit 1 ;;
esac

log() { echo "duckdns: $*"; }
err() { echo "duckdns: 오류: $*" >&2; }

# .env를 source하지 않고 필요한 키만 읽는다 (임의 코드 실행 방지)
read_env() {
  local key="$1" value
  value="$(sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n 1)"
  value="${value%\"}"; value="${value#\"}"
  value="${value%\'}"; value="${value#\'}"
  printf '%s' "$value"
}

if [[ ! -r "$ENV_FILE" ]]; then
  err ".env를 읽을 수 없습니다: $ENV_FILE"
  exit 1
fi

DOMAIN="$(read_env DUCKDNS_DOMAIN)"
TOKEN="$(read_env DUCKDNS_TOKEN)"

if [[ -z "$DOMAIN" || -z "$TOKEN" ]]; then
  err ".env에 DUCKDNS_DOMAIN과 DUCKDNS_TOKEN을 설정하세요"
  exit 1
fi
# curl 설정에 그대로 들어가므로 허용 문자만 받는다
if [[ ! "$DOMAIN" =~ ^[a-z0-9-]+$ ]]; then
  err "DUCKDNS_DOMAIN은 서브도메인만 (영어 소문자, 숫자, -). 예: myserver"
  exit 1
fi
if [[ ! "$TOKEN" =~ ^[A-Za-z0-9-]+$ ]]; then
  err "DUCKDNS_TOKEN 형식이 올바르지 않습니다"
  exit 1
fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "이미 실행 중이라 건너뜁니다"
  exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  log "dry-run: 요청 https://www.duckdns.org/update?domains=${DOMAIN}&token=****(${#TOKEN}자)&ip=&verbose=true"
  log "dry-run: 네트워크 호출은 하지 않았습니다"
  exit 0
fi

# ip= 를 비우면 DuckDNS가 요청을 보낸 공인 IP로 갱신한다
if ! response="$(printf 'url = "https://www.duckdns.org/update?domains=%s&token=%s&ip=&verbose=true"\n' "$DOMAIN" "$TOKEN" \
    | curl --silent --show-error --fail --max-time 15 --retry 2 --config - 2>&1)"; then
  err "DuckDNS 요청 실패: ${response//$TOKEN/****}"
  exit 3
fi

# verbose 응답: 1줄 OK|KO, 2줄 IPv4, 3줄 IPv6, 4줄 UPDATED|NOCHANGE
status="$(sed -n 1p <<<"$response")"
ipv4="$(sed -n 2p <<<"$response")"
change="$(sed -n 4p <<<"$response")"

if [[ "$status" != "OK" ]]; then
  err "DuckDNS가 거부했습니다 (응답: ${status:-없음}). 도메인과 토큰을 확인하세요"
  exit 2
fi

log "갱신 성공: ${DOMAIN} -> ${ipv4:-?} (${change:-?})"
