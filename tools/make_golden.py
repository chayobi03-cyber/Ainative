#!/usr/bin/env python3
"""manifest.jsonl의 retrieval_questions로 검색 골든셋을 만든다.

각 청크의 검색 질문이 곧 (질의, 정답 청크) 쌍이므로 별도 라벨링 없이 회귀셋을 얻는다.

한계 — 반드시 알고 쓸 것:
  자동 생성 질문은 본문 어휘를 그대로 쓰므로 Recall이 낙관적으로 나온다.
  실제 사용자 질의 로그 30건 이상을 별도 held-out 세트로 병행 측정해야 한다.
  `origin` 필드로 v1(사람 작성) / v2.3(템플릿 자동 생성)을 구분해 따로 집계하라.

출력 형식 두 가지:
  pairs — 구형. 한 줄에 (질의, 정답 청크 1개). 단일 라벨 편향이 있다.
  qrels — 등급 relevance. 한 질의에 정답이 여럿일 수 있고 등급을 갖는다.

  `docs/TEST-RESULTS.md` §9가 단일 라벨 편향을 지적했다 — 실패로 집계된 사례
  상당수가 오답이 아니라 **똑같이 옳은 다른 청크**였다. qrels 형식이 그 편향을 없앤다.

  자동으로 얻을 수 있는 등급은 두 가지뿐이다(등급 3, 아래 GRADE_* 참조).
  등급 2(부분 정답)는 자동으로 판정할 수 없다. 사람이 `tests/qrels_adjudicated.jsonl`에
  판정 근거와 함께 적고, 평가 시 두 파일을 순서대로 넘긴다. 자동 등급과 사람 등급을
  섞어 한 파일에 두지 않는 이유는 `confidence` 필드가 청크에서 하는 일과 같다 —
  다음 사람이 어느 쪽을 의심해야 할지 알 수 있어야 한다.

사용법:
    python3 tools/make_golden.py kb/manifest.jsonl > tests/golden_retrieval.jsonl
    python3 tools/make_golden.py kb/manifest.jsonl --format qrels > tests/qrels_auto.jsonl
    python3 tools/make_golden.py kb/manifest.jsonl --stats
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# 자동으로 판정 가능한 등급. 등급 2는 사람 판정 전용이다.
GRADE_SOURCE_CHUNK = 3      # 질문이 유래한 청크
GRADE_DUPLICATE = 3         # 완전히 같은 질의를 가진 다른 청크


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


def build_qrels(pairs: list[dict]) -> list[dict]:
    """(질의, 정답 1개) 쌍들을 질의 단위 등급 qrels로 접는다.

    같은 질의가 여러 청크에 걸려 있으면 전부 등급 3이 된다. 자동으로 판정할 수 있는
    복수 정답은 이것뿐이며 현재 코퍼스에서는 2건이다 — 나머지는 사람 판정이 필요하다.
    """
    merged: dict[str, dict] = {}
    for p in pairs:
        q = p["query"]
        row = merged.setdefault(
            q,
            {
                "query": q,
                "qrel": {},
                "grade_source": {},
                "category": p.get("category"),
                "audience": p.get("audience", []),
                "question_origin": p.get("question_origin"),
                "confidence": p.get("confidence"),
            },
        )
        row["qrel"][p["expected_chunk_id"]] = GRADE_SOURCE_CHUNK
    for row in merged.values():
        dup = len(row["qrel"]) > 1
        for cid in row["qrel"]:
            row["grade_source"][cid] = "auto:duplicate-question" if dup else "auto:source-chunk"
    return list(merged.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--format", choices=["pairs", "qrels"], default="pairs")
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
        qrels = build_qrels(golden)
        multi = sum(1 for r in qrels if len(r["qrel"]) > 1)
        print(f"qrels 형식: 질의 {len(qrels)}개 (복수 정답 {multi}개)")
        print("  등급 2(부분 정답)는 자동 판정 불가 — tests/qrels_adjudicated.jsonl 참조")
        return 0

    for g in (build_qrels(golden) if a.format == "qrels" else golden):
        print(json.dumps(g, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
