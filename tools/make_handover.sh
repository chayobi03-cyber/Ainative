#!/usr/bin/env bash
# 인수인계 패키지(zip) 생성.
#
# 사내 전달용으로 저장소 스냅샷을 묶고, 받는 쪽이 git 없이도 바로 검증할 수 있게
# START-HERE.md 와 재검토 일정(.ics)을 함께 넣는다.
#
#   ./tools/make_handover.sh                       # dist/ainative-v3.0-handover-<date>.zip
#   ./tools/make_handover.sh --organizer a@b.com   # .ics 주최자 지정
#
# 게이트가 실패하면 패키지를 만들지 않는다 — 깨진 상태를 인수인계하지 않기 위함.
set -uo pipefail
cd "$(dirname "$0")/.."

ORGANIZER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --organizer) ORGANIZER="${2:-}"; shift 2 ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
done

STAMP="$(date +%Y%m%d)"
NAME="ainative-v3.0-handover-${STAMP}"
OUT="dist/${NAME}.zip"
STAGE="$(mktemp -d)/${NAME}"

echo "=== 1/4 품질 게이트 ==="
if ! ./tests/run_checks.sh >/dev/null 2>&1; then
  echo "게이트 실패 — 패키지를 만들지 않습니다. ./tests/run_checks.sh 로 원인을 확인하십시오." >&2
  exit 1
fi
echo "  통과"

echo "=== 2/4 파일 수집 ==="
mkdir -p "$STAGE"
# git 추적 파일만 담는다. 산출물·캐시가 섞이지 않는다.
git ls-files -z | while IFS= read -r -d '' f; do
  mkdir -p "$STAGE/$(dirname "$f")"
  cp "$f" "$STAGE/$f"
done
echo "  $(git ls-files | wc -l)개 파일"

echo "=== 3/4 부속 자료 생성 ==="
if [ -n "$ORGANIZER" ]; then
  python3 tools/make_calendar.py --organizer "$ORGANIZER" --out "$STAGE/ainative-review.ics" 2>/dev/null
else
  python3 tools/make_calendar.py --out "$STAGE/ainative-review.ics" 2>/dev/null
fi
python3 tools/kb_audit.py kb/chunks --json "$STAGE/audit-report.json" --quiet
python3 tools/eval_retrieval.py kb/manifest.jsonl tests/golden_retrieval.jsonl \
  --mode body --json "$STAGE/retrieval-report.json" >/dev/null

cat > "$STAGE/START-HERE.md" <<'START'
# 인수인계 — 여기서부터

Ainative v3.0 사내 AI 협업 지식 베이스. 압축을 풀고 아래 순서대로 진행한다.

## 1. 먼저 돌려본다 (2분)

Python 3.11만 있으면 된다. **설치할 패키지도 네트워크도 필요 없다.**

```bash
./tests/run_checks.sh     # 8/8 통과해야 정상
./ci/gate.sh              # 게이트 + 담당자·기한 경고
```

담당자 미기입 경고가 나오는 것이 **정상**이다 — 아직 안 채웠기 때문이다.

## 2. 무엇을 받았는지 (5분)

| 파일 | 먼저 읽을 것 |
|---|---|
| `README.md` | 전체 개요·현재 상태 |
| `docs/HANDOVER.md` | **인수인계 체크리스트 — 이 문서가 핵심** |
| `docs/TEST-RESULTS.md` | 무엇이 검증됐고 무엇이 안 됐는지 |
| `docs/INTERNAL-FILL-INS.md` | 사내에서 채워야 할 항목 |

**한 줄 요약: 구조는 검증됐고 내용은 검증되지 않았다.** 청크 100개의 인용 수치는
구조 시험만 통과했을 뿐 사실 대조를 거치지 않았다.

## 3. 바로 해야 할 4가지 (1시간)

1. **`OWNERS.yaml` 담당자 기입** → `python3 tools/check_owners.py` 로 확인
2. **재검토 일정 캘린더 등록** — 동봉된 `ainative-review.ics` 를 가져오기
   (담당자 기입 후 `python3 tools/make_calendar.py --out x.ics` 로 다시 뽑으면 담당자가 들어간다)
3. **CI 연결** — `ci/README.md` 에서 사내 CI에 맞는 예시를 골라 붙인다.
   담당자 기입이 끝나면 `REQUIRE_OWNERS=1` 로 바꿔 미지정을 차단한다.
4. **임베딩 모델·벡터 DB 확정** — `kb/chunks/v3-korean-rag.md` 근거 참조.
   확정 전에 골든셋으로 2~3개 모델을 비교할 것. 한 번 임베딩하면 교체 = 전량 재임베딩이다.

## 4. 절대 놓치면 안 되는 것 4가지

문서를 다 읽지 못하더라도 이것만은.

1. **검색 평가는 `--mode body` 로만 한다.** 기본값은 Recall@10 = 1.000이 나오는데
   질문을 색인해 두고 그 질문으로 찾은 것이라 아무 의미가 없다.
2. **`tests/fixtures/t13_broken/` 은 실패해야 정상이다.** 고치면 검사가 작동하는지
   아무도 모르게 된다.
3. **`kb/corrections.yaml` 의 정정이 어디에도 적용되지 않으면 빌드가 실패한다.**
   버그가 아니라 설계다. 이미 반영됐다면 해당 항목을 원장에서 지운다.
4. **`confidence` 필터를 검색 앱이 실제로 걸어야 한다.** KB는 필드를 제공할 뿐이고,
   필터가 없으면 초안(`draft`)이 검증된 답과 똑같은 얼굴로 나간다.
   지금 배포 가능한 것은 `verified` 42 + `auto-merged` 46 = **88개**다.

## 5. 동봉 자료

| 파일 | 내용 |
|---|---|
| `ainative-review.ics` | 재검토 일정 3건 (Google/Outlook/Apple 공통) |
| `audit-report.json` | 청크 감사 결과 (T-01~T-13) |
| `retrieval-report.json` | BM25 검색 평가 (본문 전용 모드) |

## 6. 재빌드

**저장소만으로 완결된다.** 외부 Drive가 필요 없다.

```bash
python3 tools/build_v3.py --v1 kb/_inputs/v1/rag_chunks \
  --v23-chunks kb/_inputs/v23/chunks \
  --v23-manifest kb/_inputs/v23/chunk-manifest.jsonl \
  --authored kb/authored --out kb
./tests/run_checks.sh
```
START

echo "=== 4/4 압축 ==="
mkdir -p dist
rm -f "$OUT"
( cd "$(dirname "$STAGE")" && zip -qr "$OLDPWD/$OUT" "$(basename "$STAGE")" )
rm -rf "$(dirname "$STAGE")"

echo
echo "생성: $OUT ($(du -h "$OUT" | cut -f1))"
echo "  최상위: ${NAME}/START-HERE.md 부터 읽도록 안내하십시오."
