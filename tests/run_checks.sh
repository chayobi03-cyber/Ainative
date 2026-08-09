#!/usr/bin/env bash
# v3.0 지식 베이스 품질 게이트.
# 네트워크·API 키가 필요 없으므로 폐쇄망 CI에서 그대로 돈다.
# 종료 코드 0 = 적재 가능, 1 = 차단.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
run() {
  local name="$1"; shift
  # printf의 폭 지정은 바이트 기준이라 한글이 섞이면 어긋난다. 결과를 앞에 둔다.
  if out=$("$@" 2>&1); then
    echo "  PASS  $name"
  else
    echo "  FAIL  $name"
    echo "$out" | sed 's/^/    /'
    fail=1
  fi
}

echo "=== v3.0 품질 게이트 ==="

# 1. 감사 하네스 — T-03/04/05/08 중 하나라도 FAIL이면 0이 아닌 코드
run "T-01~T-08 청크 감사" python3 tools/kb_audit.py kb/chunks --quiet

# 2. 저장소 정합성 — manifest 3자 일치, 색인 대상 분리, 빌더 입력 자족성,
#    confidence 필터 정책 문서 일치, 정정 원장 회귀 시험, 병합 보존 불변식.
#    이 검사들은 예전에 이 파일 안의 heredoc이었다. 문법 검사도 자기시험도 받지
#    못하는 자리였고 `compileall tools` 대상에서도 빠져 있었다.
run "저장소 정합성 (6종)" python3 tools/check_consistency.py

# 3. T-18 게이트 자기시험 — 차단 검사 전체가 실제로 결함을 잡는지.
#    한 번도 발화한 적 없는 검사는 작동을 보장하지 않는다. 픽스처마다 어느 게이트가
#    FAIL이어야 하는지를 못박아 두므로, 엉뚱한 검사가 대신 발화해도 통과하지 않는다.
run "T-18 게이트 자기시험 (T-03/04/05/08/13)" python3 tools/check_gate_selftest.py

# 4. 벡터 DB 페이로드 검증 — 외부 패키지 없이 도는 부분만
run "업로드 어댑터 dry-run (6개 타깃)" bash -c \
  'for t in chromadb pinecone qdrant weaviate faiss jsonl; do
     python3 tools/upload_vectors.py --dry-run --target "$t" >/dev/null || exit 1
   done'

# 5. 골든셋 생성 가능 여부
run "골든셋 생성" python3 tools/make_golden.py kb/manifest.jsonl --stats

# 6. 도구 스크립트 문법
run "tools/*.py 컴파일" python3 -m compileall -q tools

# 7. T-17 에이전트 표면 — SKILL.md 규격, 라우팅 색인 동기, AGENTS.md 경로.
#    색인은 생성물이라 재빌드 후 재생성을 잊으면 에이전트를 없는 청크로 안내한다.
run "T-17 에이전트 표면" python3 tools/check_agent_surface.py

# 8. T-17 자기시험 — 규격 위반 픽스처가 실제로 FAIL을 유발하는가.
run "T-17 자기시험(픽스처가 FAIL을 유발)" bash -c \
  '! python3 tools/check_agent_surface.py --skills tests/fixtures/agent_surface_broken'

# 9. T-20 참조 무결성 · 평가 커버리지 — 업데이트 이식이 여기서 깨진다.
#    chunk_id는 정정·판정 원장과 문서 곳곳에서 참조되는데 청크는 빌더 출력이라
#    다음 버전에서 이름이 바뀔 수 있다. supersedes로 이관 대상을 함께 알려준다.
run "T-20 참조 무결성·평가 커버리지" python3 tools/check_references.py

# 10. T-19 벤더 역량 행렬 — 근거 없이 "지원한다"고 적힌 셀이 없는가.
#    한 벤더에서 확인한 절차를 다른 벤더에 그대로 적용하는 사고를 막는다.
run "T-19 벤더 역량 행렬" python3 tools/check_vendor_matrix.py

# 11. T-19 자기시험 — 결함 픽스처가 FAIL을 유발하는가.
run "T-19 자기시험(픽스처가 FAIL을 유발)" bash -c \
  '! python3 tools/check_vendor_matrix.py --file tests/fixtures/vendor_matrix_broken/vendors.yaml'

# 12. 최적화 하네스 자기시험 — 안전장치가 발화하는가.
#    이 하네스의 가치는 절반이 안전장치다(test 차단·누출 거부). 발화한 적 없는
#    안전장치는 작동을 보장하지 않는다.
run "최적화 하네스 자기시험" python3 tools/optimize.py selftest

# 13. T-16 재검토 기한. 기한 초과 후 유예 14일까지는 WARN이고 그 뒤 차단한다.
#    YAML은 알림을 보내지 않는다 — 지금까지 기한은 적혀만 있었다.
#    모델 가격 항목(2026-09-01)이 방치되면 2026-09-16부터 이 단계가 막는다. 의도한 동작이다.
run "T-16 재검토 기한" python3 tools/check_freshness.py

# 14. T-14 검색 회귀 — 자동 qrels(본문 전용).
#    여기까지 이 게이트에는 검색 항목이 하나도 없었다. ci/gate.sh가 평가를 돌리긴
#    했지만 `|| true`라 아티팩트만 남고 아무것도 막지 못했다. Recall이 절반으로
#    떨어져도 CI는 초록이었다.
run "T-14 검색 회귀 (자동 qrels)" python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --qrels tests/qrels_auto.jsonl tests/qrels_adjudicated.jsonl --mode body \
  --baseline tests/baseline_retrieval.json --max-drop 0.02

# 15. T-14 검색 회귀 — held-out(실제 질의에 가까운 세트, 프로덕션 설정).
#     표본이 40건뿐이라 흔들림이 크므로 허용 낙폭을 넓게 잡는다.
run "T-14 검색 회귀 (held-out)" python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --views body,fields,index --fuse rrf --expand-hops 1 \
  --baseline tests/baseline_heldout.json --max-drop 0.05

echo
if [ "$fail" -eq 0 ]; then
  echo "결과: 통과 — 적재 가능"
else
  echo "결과: 실패 — 적재 차단"
fi
exit "$fail"
