#!/usr/bin/env bash
# CI 진입점 — 어떤 CI에서든 이 한 줄만 부르면 된다.
#
#   ./ci/gate.sh
#
# 설계 의도
#   - 외부 의존성 0 (Python 3.11 표준 라이브러리 + bash). 설치 단계가 없다.
#   - 네트워크 불필요 → 폐쇄망 러너에서 그대로 돈다.
#   - GitHub Actions에 묶이지 않는다. GitLab/Jenkins/Azure는 ci/README.md 참조.
#
# 종료 코드
#   0 = 적재 가능
#   1 = 차단 (구조 결함)
#
# 환경 변수
#   REQUIRE_OWNERS=1   담당자 미지정 시 실패시킨다. **인수인계 완료 후 켤 것.**
#                      기본값은 경고만 — 인수인계 전에는 비어 있는 게 정상이다.
#   EXPIRY_WARN_DAYS   재검토 기한 임박 경고 일수 (기본 30)
set -uo pipefail
cd "$(dirname "$0")/.."

REQUIRE_OWNERS="${REQUIRE_OWNERS:-0}"
EXPIRY_WARN_DAYS="${EXPIRY_WARN_DAYS:-30}"
mkdir -p out

echo "=== Ainative 품질 게이트 ==="
python3 --version

fail=0

# 1) 구조 게이트 (차단)
if ./tests/run_checks.sh; then
  :
else
  fail=1
fi

echo
echo "=== 부가 점검 (기본은 경고) ==="

# 2) 담당자 지정 — 인수인계 전에는 비어 있는 게 정상이므로 기본은 경고
if [ "$REQUIRE_OWNERS" = "1" ]; then
  python3 tools/check_owners.py --require || fail=1
else
  python3 tools/check_owners.py || true
fi

# 3) 재검토 기한 — 상세 표를 남긴다.
#    차단 판정은 tests/run_checks.sh의 T-16이 이미 했으므로 여기서는 보고만 한다.
python3 tools/check_freshness.py --warn-days "$EXPIRY_WARN_DAYS" \
  --json out/freshness.json || true

# 4) 리포트 보관 (아티팩트용 — 여기서는 차단하지 않는다)
#    검색 품질의 차단은 tests/run_checks.sh의 T-14가 이미 했다.
#    이 단계는 추이를 남기기 위한 것이며 held-out·음성 질의까지 포함한다.
python3 tools/kb_audit.py kb/chunks --json out/audit.json --quiet || true
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --qrels tests/qrels_auto.jsonl tests/qrels_adjudicated.jsonl \
  --mode body --json out/retrieval.json >/dev/null 2>&1 || true
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --negatives tests/negative_queries.jsonl \
  --views body,fields,index --fuse rrf --expand-hops 1 \
  --json out/retrieval-heldout.json >/dev/null 2>&1 || true

echo
if [ "$fail" -eq 0 ]; then
  echo "게이트 통과 — 적재 가능"
else
  echo "게이트 실패 — 적재 차단"
fi
exit "$fail"
