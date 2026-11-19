#!/usr/bin/env bash
# deploy/systemd/*.in 템플릿의 자리표시자를 채워 build/systemd/ 에 unit 파일을 만든다.
# 저장소에는 사용자 이름·홈 경로를 남기지 않기 위해 템플릿만 커밋한다.
#
# 사용: scripts/render-systemd.sh
#   @USER@     -> 실행 사용자 (기본: 현재 사용자, RUN_USER로 바꿀 수 있음)
#   @REPO_DIR@ -> 이 저장소의 절대 경로
# 설치(sudo)는 출력되는 명령을 사람이 직접 실행한다.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$REPO_DIR/deploy/systemd"
OUT_DIR="$REPO_DIR/build/systemd"
RUN_USER="${RUN_USER:-$(id -un)}"

if [[ "$RUN_USER" == "root" ]]; then
  echo "render-systemd: 오류: root로 실행하지 마세요 (일반 사용자로 실행)" >&2
  exit 1
fi
# sed 구분자와 겹치지 않게 검사
if [[ "$REPO_DIR" == *"|"* || "$RUN_USER" == *"|"* ]]; then
  echo "render-systemd: 오류: 경로나 사용자 이름에 '|'가 있습니다" >&2
  exit 1
fi

shopt -s nullglob
templates=("$SRC_DIR"/*.in)
if [[ ${#templates[@]} -eq 0 ]]; then
  echo "render-systemd: 오류: 템플릿이 없습니다: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
units=()
for tpl in "${templates[@]}"; do
  name="$(basename "$tpl" .in)"
  sed -e "s|@USER@|${RUN_USER}|g" -e "s|@REPO_DIR@|${REPO_DIR}|g" "$tpl" > "$OUT_DIR/$name"
  units+=("$name")
  echo "생성: build/systemd/$name"
done

echo
echo "설치 (직접 실행):"
echo "  sudo install -m 644 ${OUT_DIR}/* /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
for u in "${units[@]}"; do
  [[ "$u" == *.timer ]] && echo "  sudo systemctl enable --now $u"
done
