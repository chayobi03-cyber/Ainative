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

# 4. 골든셋 생성 가능 여부
run "골든셋 생성" python3 tools/make_golden.py kb/manifest.jsonl --stats

# 5. 도구 스크립트 문법
run "tools/*.py 컴파일" python3 -m compileall -q tools

echo
if [ "$fail" -eq 0 ]; then
  echo "결과: 통과 — 적재 가능"
else
  echo "결과: 실패 — 적재 차단"
fi
exit "$fail"
