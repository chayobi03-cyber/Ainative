#!/usr/bin/env python3
"""BM25 어휘 검색 평가 — T-12의 실행 가능한 절반.

왜 BM25만 하는가
    dense 검색은 임베딩 모델과 벡터 DB가 필요하고 폐쇄망·CI에서 못 돌린다.
    반면 BM25는 순수 파이썬으로 되고, 이 코퍼스는 영어 식별자(`PreToolUse`,
    `RFC 8707`) 비중이 높아 어휘 검색이 실제로 하이브리드의 한 축이다.
    여기서 나온 수치는 하이브리드 성능의 **하한**이다.

한국어 토큰화
    형태소 분석기 없이 어미 변화를 흡수하려고 한글은 문자 바이그램으로,
    ASCII는 단어로 자른다. 검색·색인에 같은 방식을 쓰므로 일관된다.

읽을 때 주의
    골든셋 질문이 청크 본문에서 파생됐으므로 점수는 낙관적이다. 절대값을 목표
    달성으로 읽지 말고, **어느 청크가 자기 질문으로도 안 찾아지는가**를 보라.
    그게 실제로 고쳐야 할 곳이다.

사용법:
    python3 tools/eval_retrieval.py kb/manifest.jsonl tests/golden_retrieval.jsonl
    python3 tools/eval_retrieval.py ... --field-weights   # 필드 가중 비교
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_audit import split_frontmatter  # noqa: E402

HANGUL_RUN = re.compile(r"[가-힣]+")
ASCII_TOK = re.compile(r"[A-Za-z][A-Za-z0-9_\-\.]*|\d+")


def tokenize(text: str) -> list[str]:
    text = text.lower()
    toks = [t for t in ASCII_TOK.findall(text)]
    for run in HANGUL_RUN.findall(text):
        if len(run) == 1:
            toks.append(run)
        else:
            # 문자 바이그램: '차단하는'/'차단을' 이 '차단' 을 공유하게 만든다
            toks += [run[i : i + 2] for i in range(len(run) - 1)]
    return toks


class BM25:
    def __init__(self, docs: dict[str, list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.ids = list(docs)
        self.tf = {i: Counter(t) for i, t in docs.items()}
        self.len = {i: len(t) for i, t in docs.items()}
        self.avg = (sum(self.len.values()) / len(self.len)) if self.len else 0.0
        df: Counter = Counter()
        for t in docs.values():
            df.update(set(t))
        n = len(docs)
        self.idf = {
            w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()
        }
        self.postings = defaultdict(list)
        for i, t in docs.items():
            for w in set(t):
                self.postings[w].append(i)

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        q = tokenize(query)
        scores: dict[str, float] = defaultdict(float)
        for w in q:
            if w not in self.idf:
                continue
            idf = self.idf[w]
            for i in self.postings[w]:
                f = self.tf[i][w]
                denom = f + self.k1 * (1 - self.b + self.b * self.len[i] / (self.avg or 1))
                scores[i] += idf * f * (self.k1 + 1) / denom
        return sorted(scores.items(), key=lambda x: -x[1])[:k]


def build_docs(manifest: Path, mode: str) -> dict[str, list[str]]:
    rows = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
    root = manifest.parent
    docs = {}
    for r in rows:
        body = split_frontmatter((root / r["file_path"]).read_text(encoding="utf-8"))[1]
        title = r["title"]
        tags = " ".join(r.get("tags", []))
        qs = " ".join(r.get("retrieval_questions", []))
        if mode == "body":
            text = body
        elif mode == "fields":
            # ingestion.yaml의 기본 설정: 제목·태그·질문에만 BM25를 건다
            text = f"{title} {tags} {qs}"
        else:  # all
            # 제목·태그·질문을 3회 반복해 가중치를 준다
            text = " ".join([title, tags, qs] * 3 + [body])
        docs[r["chunk_id"]] = tokenize(text)
    return docs


def evaluate(bm25: BM25, golden: list[dict], ks=(1, 3, 5, 10)):
    hits = {k: 0 for k in ks}
    rr = 0.0
    misses = Counter()
    n = 0
    for g in golden:
        res = bm25.search(g["query"], k=max(ks))
        ranked = [i for i, _ in res]
        gold = g["expected_chunk_id"]
        n += 1
        if gold in ranked:
            pos = ranked.index(gold) + 1
            rr += 1.0 / pos
            for k in ks:
                if pos <= k:
                    hits[k] += 1
        else:
            misses[gold] += 1
    return {
        "n": n,
        "recall": {f"@{k}": round(hits[k] / n, 4) for k in ks},
        "mrr": round(rr / n, 4),
        "miss_rate": round(sum(misses.values()) / n, 4),
        "worst_chunks": misses.most_common(15),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("golden", type=Path)
    ap.add_argument("--mode", choices=["all", "body", "fields"], default="all")
    ap.add_argument("--compare-modes", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args()

    golden = [json.loads(l) for l in a.golden.read_text(encoding="utf-8").splitlines() if l.strip()]
    modes = ["all", "fields", "body"] if a.compare_modes else [a.mode]

    report = {"golden_pairs": len(golden), "modes": {}}
    for m in modes:
        bm = BM25(build_docs(a.manifest, m))
        res = evaluate(bm, golden)
        report["modes"][m] = res
        print(f"[색인 대상: {m}]  n={res['n']}")
        print(f"  Recall@1={res['recall']['@1']}  @3={res['recall']['@3']}  "
              f"@5={res['recall']['@5']}  @10={res['recall']['@10']}  MRR={res['mrr']}")
        print(f"  검색 실패율={res['miss_rate']}")
        if res["worst_chunks"]:
            print("  자기 질문으로도 못 찾은 청크:")
            for cid, c in res["worst_chunks"][:8]:
                print(f"    {c}회 실패  {cid}")
        print()

    # 출처별 분해 — 자동 생성 질문은 본문 어휘와 겹쳐 점수가 높게 나온다
    bm = BM25(build_docs(a.manifest, modes[0]))
    by_origin = defaultdict(list)
    for g in golden:
        by_origin[g.get("question_origin", "?")].append(g)
    print(f"[질문 출처별 분해 — 색인 대상 {modes[0]}]")
    for origin, gs in sorted(by_origin.items()):
        r = evaluate(bm, gs)
        print(f"  {origin:9s} n={r['n']:3d}  Recall@10={r['recall']['@10']:.4f}  MRR={r['mrr']:.4f}")
        report["modes"][modes[0]].setdefault("by_origin", {})[origin] = r

    if a.json:
        a.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
