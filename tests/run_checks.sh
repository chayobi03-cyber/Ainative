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

# 2. 매니페스트 정합성
run "매니페스트 ↔ 청크 파일 수 일치" python3 - <<'PY'
import json, sys, pathlib
man = [json.loads(l) for l in open('kb/manifest.jsonl') if l.strip()]
emb = [json.loads(l) for l in open('kb/embeddings.jsonl') if l.strip()]
files = sorted(p.stem for p in pathlib.Path('kb/chunks').glob('*.md'))
ids = sorted(m['chunk_id'] for m in man)
assert ids == files, f"manifest {len(ids)} vs files {len(files)}: {set(ids)^set(files)}"
assert sorted(e['chunk_id'] for e in emb) == ids, "embeddings 불일치"
for m in man:
    p = pathlib.Path('kb') / m['file_path']
    assert p.exists(), f"file_path 깨짐: {m['file_path']}"
PY

# 3. 색인 대상 분리 — 원본이 색인에 섞이면 중복 히트가 난다
run "ingestion exclude 경로 실재 확인" python3 - <<'PY'
import pathlib
for d in ('kb/docs', 'kb/sources', 'kb/authored'):
    assert pathlib.Path(d).is_dir(), f"{d} 없음 — ingestion.yaml exclude와 불일치"
assert not list(pathlib.Path('kb/chunks').glob('**/sources/*')), "chunks 안에 원본 혼입"
PY

# 4. 자족성 — 빌더 입력이 저장소 안에 있는가.
#    없으면 청크를 영영 재빌드할 수 없다(docs/HANDOVER.md §A-1).
run "빌더 입력 자족성" python3 - <<'SELFCHK'
import pathlib
need = ["kb/_inputs/v1/rag_chunks", "kb/_inputs/v23/chunks", "kb/_inputs/v23/chunk-manifest.jsonl"]
for n in need:
    assert pathlib.Path(n).exists(), f"빌더 입력 없음: {n} — 저장소만으로 재빌드 불가"
assert len(list(pathlib.Path("kb/_inputs/v1/rag_chunks").glob("*.md"))) == 47, "v1 입력 개수 불일치"
assert len(list(pathlib.Path("kb/_inputs/v23/chunks").glob("*.md"))) == 135, "v2.3 입력 개수 불일치"
SELFCHK

# 5. T-13이 실제로 결함을 잡는지 자기시험.
#    한 번도 발화한 적 없는 검사는 작동을 보장하지 않는다. 픽스처는 4종 결함을
#    일부러 담고 있으며, 감사가 FAIL(exit 1)을 내야 이 단계가 통과한다.
run "T-13 자기시험(픽스처가 FAIL을 유발)" bash -c \
  '! python3 tools/kb_audit.py tests/fixtures/t13_broken/chunks --repo-root . --quiet'

# 6. 벡터 DB 페이로드 검증 — 외부 패키지 없이 도는 부분만
run "업로드 어댑터 dry-run (6개 타깃)" bash -c \
  'for t in chromadb pinecone qdrant weaviate faiss jsonl; do
     python3 tools/upload_vectors.py --dry-run --target "$t" >/dev/null || exit 1
   done'

# 7. 골든셋 생성 가능 여부
run "골든셋 생성" python3 tools/make_golden.py kb/manifest.jsonl --stats

# 8. 도구 스크립트 문법
run "tools/*.py 컴파일" python3 -m compileall -q tools

# 9. T-14 검색 회귀 — 자동 qrels(본문 전용).
#    여기까지 이 게이트에는 검색 항목이 하나도 없었다. ci/gate.sh가 평가를 돌리긴
#    했지만 `|| true`라 아티팩트만 남고 아무것도 막지 못했다. Recall이 절반으로
#    떨어져도 CI는 초록이었다.
run "T-14 검색 회귀 (자동 qrels)" python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --qrels tests/qrels_auto.jsonl tests/qrels_adjudicated.jsonl --mode body \
  --baseline tests/baseline_retrieval.json --max-drop 0.02

# 10. T-14 검색 회귀 — held-out(실제 질의에 가까운 세트, 프로덕션 설정).
#     표본이 40건뿐이라 흔들림이 크므로 허용 낙폭을 넓게 잡는다.
run "T-14 검색 회귀 (held-out)" python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --views body,fields --fuse rrf --expand-hops 1 \
  --baseline tests/baseline_heldout.json --max-drop 0.05

echo
if [ "$fail" -eq 0 ]; then
  echo "결과: 통과 — 적재 가능"
else
  echo "결과: 실패 — 적재 차단"
fi
exit "$fail"
