#!/usr/bin/env python3
"""저장소 정합성 검사 — 산출물·설정·문서가 서로 어긋나지 않는지 본다.

왜 파일로 뺐는가
    이 검사들은 `tests/run_checks.sh` 안의 인라인 heredoc이었다. 문법 검사도
    단위 시험도 자기시험도 받지 못하는 자리이고, 실제로 `python3 -m compileall tools`
    대상에서 빠져 있었다. 게이트가 자기 검사 코드를 검사하지 못하는 상태였다.

검사 항목
    manifest      manifest ↔ 청크 파일 ↔ embeddings 3자 정합
    ingestion     ingestion.yaml의 exclude 경로가 실재하는가
    inputs        빌더 입력이 저장소 안에 있는가 (재빌드 가능성)
    policy        confidence 필터 정책이 문서 3곳에서 일치하는가
    corrections   정정 원장이 질문에만 걸리는 경우에도 적용되는가 (회귀 시험)

사용법:
    python3 tools/check_consistency.py            # 전부
    python3 tools/check_consistency.py --only policy
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

REPO = pathlib.Path(__file__).resolve().parent.parent

# 정본은 kb/ingestion.yaml이다. 나머지 문서는 여기에 맞춘다.
POLICY_SOURCE = "kb/ingestion.yaml"


def check_manifest() -> list[str]:
    """manifest·청크 파일·embeddings 세 목록이 정확히 같은가."""
    bad = []
    man = [json.loads(l) for l in (REPO / "kb/manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    emb = [json.loads(l) for l in (REPO / "kb/embeddings.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    files = sorted(p.stem for p in (REPO / "kb/chunks").glob("*.md"))
    ids = sorted(m["chunk_id"] for m in man)
    if ids != files:
        bad.append(f"manifest {len(ids)}개 vs 청크 파일 {len(files)}개 — 차집합 {set(ids) ^ set(files)}")
    if sorted(e["chunk_id"] for e in emb) != ids:
        bad.append("embeddings.jsonl의 chunk_id 목록이 manifest와 다릅니다")
    for m in man:
        if not (REPO / "kb" / m["file_path"]).exists():
            bad.append(f"file_path 깨짐: {m['file_path']}")
    return bad


def check_ingestion() -> list[str]:
    """색인 대상 분리 — 원본이 색인에 섞이면 같은 내용이 두 번 히트한다."""
    bad = []
    for d in ("kb/docs", "kb/sources", "kb/authored"):
        if not (REPO / d).is_dir():
            bad.append(f"{d} 없음 — ingestion.yaml의 exclude와 불일치")
    if list((REPO / "kb/chunks").glob("**/sources/*")):
        bad.append("kb/chunks 안에 원본이 혼입돼 있습니다")
    return bad


def check_inputs() -> list[str]:
    """빌더 입력 자족성 — 없으면 청크를 영영 재빌드할 수 없다 (docs/HANDOVER.md §A-1)."""
    bad = []
    expect = {
        "kb/_inputs/v1/rag_chunks": 47,
        "kb/_inputs/v23/chunks": 135,
    }
    for path, count in expect.items():
        p = REPO / path
        if not p.exists():
            bad.append(f"빌더 입력 없음: {path} — 저장소만으로 재빌드 불가")
            continue
        got = len(list(p.glob("*.md")))
        if got != count:
            bad.append(f"{path}: 입력 개수 불일치 (기대 {count}, 실제 {got})")
    if not (REPO / "kb/_inputs/v23/chunk-manifest.jsonl").exists():
        bad.append("빌더 입력 없음: kb/_inputs/v23/chunk-manifest.jsonl")
    return bad


def _policy_from_ingestion() -> dict[str, set[str]]:
    text = (REPO / POLICY_SOURCE).read_text(encoding="utf-8")
    out = {}
    for name in ("production_default", "strict"):
        m = re.search(rf"{name}:\s*\n\s*confidence:\s*\[([^\]]*)\]", text)
        if m:
            out[name] = {v.strip().strip('"\'') for v in m.group(1).split(",") if v.strip()}
    return out


def check_policy() -> list[str]:
    """confidence 필터 정책이 문서 사이에서 일치하는가.

    같은 정책이 kb/schema.md, kb/ingestion.yaml, docs/RAG-AGENT-SPEC.md 세 곳에
    적혀 있었고 서로 달랐다. 어느 문서를 읽었느냐에 따라 12개 청크(mixed 5 + draft 7)의
    노출 여부가 달라진다. 정본을 ingestion.yaml로 정하고 나머지가 따라오는지 본다.
    """
    bad = []
    policy = _policy_from_ingestion()
    if "production_default" not in policy or "strict" not in policy:
        return [f"{POLICY_SOURCE}에서 confidence 필터를 읽지 못했습니다"]

    known = {"verified", "mixed", "auto-merged", "draft"}
    for name, vals in policy.items():
        unknown = vals - known
        if unknown:
            bad.append(f"{POLICY_SOURCE}: 알 수 없는 confidence 값 {sorted(unknown)}")
    if not policy["strict"] <= policy["production_default"]:
        bad.append("strict 필터가 production_default의 부분집합이 아닙니다 — 더 엄격해야 합니다")

    # 문서마다 표의 마지막 열이 무엇을 뜻하는지 다르다 — kb/schema.md는 strict를,
    # docs/RAG-AGENT-SPEC.md는 프로덕션을 서술한다. 열 제목을 읽지 않고 대조하면
    # 정상인 문서를 불일치로 잡는다.
    table = re.compile(
        r"^\|\s*값\s*\|[^|]*\|\s*(?P<header>[^|]+?)\s*\|\s*$"
        r"(?P<rows>(?:\n\|.*)+)",
        re.M,
    )
    for doc in ("kb/schema.md", "docs/RAG-AGENT-SPEC.md"):
        text = (REPO / doc).read_text(encoding="utf-8")
        m = table.search(text)
        if not m:
            bad.append(f"{doc}: confidence 표를 찾지 못했습니다")
            continue
        header = m.group("header")
        which = "strict" if "strict" in header else "production_default"
        allowed = policy[which]
        for line in m.group("rows").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            value = cells[0].strip("`")
            if value not in known:
                continue
            # 'strict 모드에서 제외' 같은 단서절은 이 표의 열이 뜻하는 바가 아니다.
            verdict = re.sub(r"\(.*?\)", "", cells[-1])
            says_included = "포함" in verdict
            should = value in allowed
            if says_included != should:
                bad.append(
                    f"{doc}: `{value}`가 '{header}'에 "
                    f"{'포함' if says_included else '제외'}로 적혀 있으나 "
                    f"{POLICY_SOURCE}의 {which}는 "
                    f"{'포함' if should else '제외'}합니다"
                )
    return bad


def check_corrections() -> list[str]:
    """정정 원장 회귀 시험 — 질문에만 걸리는 정정이 적용되는가.

    build_v3.apply_corrections가 retrieval_questions를 먼저 치환한 뒤 원문 문자열을
    찾아 hit을 판정했기 때문에, 본문에 없고 질문에만 있는 정정은 적용 횟수가 0으로
    집계돼 빌드를 중단시켰다. 정정 원장의 한 경로가 통째로 막혀 있었다.
    """
    import tempfile

    from build_v3 import apply_corrections

    ledger = """corrections:
  - id: C-TEST
    verified_source: "https://example.invalid/"
    replace:
      - from: "옛이름"
        to: "새이름"

verified_no_change: []
"""
    chunk = {
        "chunk_id": "fx",
        "title": "제목",
        "section_path": "",
        "_body": "본문에는 그 문자열이 없다.",
        "retrieval_questions": ["옛이름은 무엇인가?"],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(ledger)
        path = pathlib.Path(tf.name)
    try:
        try:
            apply_corrections([chunk], path)
        except SystemExit as e:
            return [f"질문에만 걸리는 정정이 적용되지 않았습니다 (applies=0으로 빌드 중단): {e}"]
        if chunk["retrieval_questions"] != ["새이름은 무엇인가?"]:
            return [f"질문 치환 결과가 예상과 다릅니다: {chunk['retrieval_questions']}"]
        if "C-TEST" not in chunk.get("_corrections", []):
            return ["정정이 적용됐으나 _corrections에 기록되지 않았습니다"]
    finally:
        path.unlink(missing_ok=True)
    return []


CHECKS = {
    "manifest": check_manifest,
    "ingestion": check_ingestion,
    "inputs": check_inputs,
    "policy": check_policy,
    "corrections": check_corrections,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=sorted(CHECKS), default=None)
    a = ap.parse_args()

    names = [a.only] if a.only else list(CHECKS)
    failed = 0
    for name in names:
        problems = CHECKS[name]()
        if problems:
            failed = 1
            print(f"  FAIL  {name}")
            for p in problems:
                print(f"        {p}")
        else:
            print(f"  OK    {name}")
    return failed


if __name__ == "__main__":
    sys.exit(main())
