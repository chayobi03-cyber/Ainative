#!/usr/bin/env python3
"""manifest.jsonl의 retrieval_questions로 검색 골든셋을 만든다.

각 청크의 검색 질문이 곧 (질의, 정답 청크) 쌍이므로 별도 라벨링 없이 회귀셋을 얻는다.

한계 — 반드시 알고 쓸 것:
  자동 생성 질문은 본문 어휘를 그대로 쓰므로 Recall이 낙관적으로 나온다.
  실제 사용자 질의 로그 30건 이상을 별도 held-out 세트로 병행 측정해야 한다.
  `origin` 필드로 v1(사람 작성) / v2.3(템플릿 자동 생성)을 구분해 따로 집계하라.

사용법:
    python3 tools/make_golden.py kb/manifest.jsonl > tests/golden_retrieval.jsonl
    python3 tools/make_golden.py kb/manifest.jsonl --stats
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def build(manifest: Path):
    rows = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for r in rows:
        for q in r.get("retrieval_questions", []):
            out.append(
                {
                    "query": q,
                    "expected_chunk_id": r["chunk_id"],
                    "category": r.get("category"),
                    "audience": r.get("audience", []),
                    # v1 유래 질문은 사람이 쓴 것이라 신뢰도가 높다.
                    # v2.3 유래는 섹션 템플릿에서 기계 생성돼 어휘가 본문과 겹친다.
                    "question_origin": r.get("origin"),
                    "confidence": r.get("confidence"),
                }
            )
    return rows, out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    rows, golden = build(a.manifest)
    if a.stats:
        by_origin = Counter(g["question_origin"] for g in golden)
        dup = Counter(g["query"] for g in golden)
        ambiguous = {q: c for q, c in dup.items() if c > 1}
        print(f"청크 {len(rows)}개 → 골든 쌍 {len(golden)}개")
        print(f"청크당 평균 질문 {len(golden)/max(1,len(rows)):.2f}개")
        for k, v in by_origin.most_common():
            print(f"  출처 {k}: {v}개")
        print(f"중복 질의(정답이 여러 청크로 갈리는 모호 질의): {len(ambiguous)}개")
        for q, c in list(ambiguous.items())[:10]:
            print(f"    x{c}  {q}")
        return 0

    for g in golden:
        print(json.dumps(g, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
