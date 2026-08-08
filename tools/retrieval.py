#!/usr/bin/env python3
"""검색 원시 연산 — 토큰화·BM25·RRF·MMR·그래프 확장·순위 지표.

왜 별도 모듈인가
    `eval_retrieval.py`가 CLI·리포팅·검색 알고리즘·지표를 한 파일에 담고 있었다.
    같은 토크나이저를 `make_index.py`가, 같은 지표를 CI 회귀 게이트가 써야 한다.
    `eval_retrieval.py`가 `kb_audit.split_frontmatter`를 가져다 쓰는 것과 같은 패턴이다.

    이 모듈은 파일을 읽고 순위와 숫자를 낸다. **해석은 하지 않는다** —
    어떤 수치가 유효한지 판정하는 규칙은 `eval_retrieval.py`에 있다.

제약
    표준 라이브러리만 쓴다. 폐쇄망 CI에서 그대로 돌아야 하므로 이 제약을 깨지 말 것.

한국어 토큰화
    형태소 분석기 없이 어미 변화를 흡수하려고 한글은 문자 n-그램으로, ASCII는 단어로
    자른다. 색인과 질의에 같은 방식을 쓰므로 일관된다. `hangul_n`을 바꾸면 같은 본문에서
    **다른 어휘 뷰**가 나오고, 그 차이가 RRF 융합의 재료가 된다.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_audit import jaccard, shingles, split_frontmatter  # noqa: E402,F401

HANGUL_RUN = re.compile(r"[가-힣]+")
ASCII_TOK = re.compile(r"[A-Za-z][A-Za-z0-9_\-\.]*|\d+")

# 색인 가능한 어휘 뷰. 각 뷰는 같은 청크를 다른 텍스트로 본다.
VIEWS = ("body", "fields", "ngram", "context", "index")


# ─────────────────────────────────────────────────────────────
# 토큰화
# ─────────────────────────────────────────────────────────────
def tokenize(text: str, hangul_n: int = 2) -> list[str]:
    """ASCII는 단어로, 한글은 `hangul_n` 문자 n-그램으로 자른다.

    hangul_n=2 — 기본. '차단하는'/'차단을' 이 '차단' 을 공유한다.
    hangul_n=4 — 더 긴 문맥을 요구해 정밀도가 오르고 재현율이 떨어진다.
                 `ngram` 뷰가 이 값을 쓴다. bigram 뷰와 순위가 달라지는 것이 목적이다.
    """
    text = text.lower()
    toks = list(ASCII_TOK.findall(text))
    for run in HANGUL_RUN.findall(text):
        if len(run) < hangul_n:
            toks.append(run)
        else:
            toks += [run[i : i + hangul_n] for i in range(len(run) - hangul_n + 1)]
    return toks


# ─────────────────────────────────────────────────────────────
# BM25
# ─────────────────────────────────────────────────────────────
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
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        self.postings = defaultdict(list)
        for i, t in docs.items():
            for w in set(t):
                self.postings[w].append(i)

    def search(self, query: str, k: int = 10, hangul_n: int = 2) -> list[tuple[str, float]]:
        q = tokenize(query, hangul_n)
        scores: dict[str, float] = defaultdict(float)
        for w in q:
            if w not in self.idf:
                continue
            idf = self.idf[w]
            for i in self.postings[w]:
                f = self.tf[i][w]
                denom = f + self.k1 * (1 - self.b + self.b * self.len[i] / (self.avg or 1))
                scores[i] += idf * f * (self.k1 + 1) / denom
        return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:k]


# ─────────────────────────────────────────────────────────────
# 뷰 구성
# ─────────────────────────────────────────────────────────────
def load_manifest(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def deterministic_context_header(row: dict, siblings: dict[str, list[dict]]) -> str:
    """Contextual Retrieval용 상황 헤더를 **LLM 없이** 만든다.

    Anthropic의 Contextual Retrieval은 임베딩 전에 청크를 문서 안에 위치시키는
    50~100 토큰 헤더를 앞에 붙인다. 보통 LLM으로 생성하지만, 이 KB에는
    `source_documents`·`section_path`·`category`·`audience`·`use_cases`가 이미 있어
    **결정론적으로 조립할 수 있다.** 폐쇄망에서 돌고 재현 가능하다는 것이 요점이다.

    실측 결과는 `docs/TEST-RESULTS.md` §12.7에 있다 — **채택하지 않았다.**
    held-out 40건에서 nDCG@10이 0.3730 → 0.3880으로 올랐지만 질의 단위로는
    11건 개선 / 8건 악화라 잡음과 구분되지 않는다. 실제 사용자 질의 세트가 들어오면
    이 함수로 다시 재 볼 것.
    """
    doc = (row.get("source_documents") or ["?"])[0]
    peers = [p["title"] for p in siblings.get(doc, [])
             if p["chunk_id"] != row["chunk_id"]][:3]
    parts = [
        f"{doc} 문서의 {row.get('section_path', '')} 맥락에서 "
        f"{row.get('title', '')}을(를) 다룬다.",
        f"분류 {row.get('category', '')}.",
        f"대상 {' '.join(row.get('audience') or [])}.",
        f"용도 {' '.join(row.get('use_cases') or [])}.",
    ]
    if peers:
        parts.append(f"같은 문서의 {', '.join(peers)}와 이어진다.")
    return " ".join(parts)


def sibling_map(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        out[(r.get("source_documents") or ["?"])[0]].append(r)
    return out


def view_text(row: dict, root: Path, view: str, siblings: dict | None = None) -> str:
    """청크 하나를 지정한 뷰의 텍스트로 만든다."""
    if view == "fields":
        # ingestion.yaml의 bm25_fields 설정과 같다: 제목·태그·질문.
        # retrieval_questions를 색인하므로 자동 골든셋에 대해서는 누출이다.
        return " ".join(
            [str(row.get("title", "")), " ".join(row.get("tags", [])),
             " ".join(row.get("retrieval_questions", []))]
        )
    if view == "context":
        # frontmatter에 `context_header`가 있으면 그것을 쓰고, 없으면 결정론적으로
        # 조립한다. 슬롯을 채우지 않은 상태에서도 이 뷰를 측정할 수 있어야
        # "채울 가치가 있는가"를 재빌드 전에 판단할 수 있다.
        stored = str(row.get("context_header", "") or "")
        if stored:
            return stored
        return deterministic_context_header(row, siblings if siblings is not None else {})
    if view == "index":
        # 에이전트가 grep으로 훑는 라우팅 표면. INDEX.md 한 행에 해당한다.
        return " ".join(
            [str(row.get("chunk_id", "")), str(row.get("title", "")),
             str(row.get("category", "")), " ".join(row.get("tags", [])),
             " ".join(row.get("use_cases", []) or [])]
        )
    # body / ngram — 둘 다 본문이며 토큰화만 다르다.
    return split_frontmatter((root / row["file_path"]).read_text(encoding="utf-8"))[1]


def build_view(rows: list[dict], root: Path, view: str) -> dict[str, list[str]]:
    hangul_n = 4 if view == "ngram" else 2
    sibs = sibling_map(rows) if view == "context" else None
    return {r["chunk_id"]: tokenize(view_text(r, root, view, sibs), hangul_n) for r in rows}


def related_map(rows: list[dict]) -> dict[str, list[str]]:
    return {r["chunk_id"]: list(r.get("related_chunks") or []) for r in rows}


# ─────────────────────────────────────────────────────────────
# 융합 · 재순위 · 확장
# ─────────────────────────────────────────────────────────────
def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion — 점수가 아니라 **순위만** 쓴다.

    RRF(d) = Σ 1/(k + rank_r(d))

    점수 정규화가 필요 없다는 것이 요점이다. BM25 점수와 코사인 유사도는 스케일이
    달라 가중합이 임의적인데, 순위는 비교 가능하다. k=60은 관례적 기본값으로
    상위 순위의 영향을 완만하게 만든다.
    """
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for pos, cid in enumerate(ranking, start=1):
            scores[cid] += 1.0 / (k + pos)
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


def mmr(
    ranked: list[tuple[str, float]],
    doc_shingles: dict[str, set],
    lam: float = 0.7,
    k: int = 10,
) -> list[tuple[str, float]]:
    """Maximal Marginal Relevance — 관련성과 다양성을 lam으로 섞는다.

    왜 여기 있는가
        크로스인코더 재순위는 모델이 필요해 폐쇄망에서 못 돈다. MMR은 문서 간
        유사도 함수만 있으면 되고, `kb_audit`의 shingle Jaccard가 이미 그 함수다.

    무엇을 노리는가
        다주제 어트랙터(`v3-faq` 등)는 많은 질의에 얕게 매칭돼 상위를 채운다.
        MMR은 이미 뽑힌 문서와 비슷한 문서의 순위를 낮추므로 어트랙터의 자리를 줄인다.

    한계 — 반드시 알고 쓸 것
        MMR은 **질의-문서 관련성을 다시 보지 않는다.** 크로스인코더 재순위의
        대체재가 아니라 다양성 항만 추가한 것이다. 이 수치를 rerank 성능이라고
        보고하지 말 것.
    """
    if not ranked:
        return []
    pool = list(ranked)
    best_score = pool[0][1] or 1.0
    selected: list[tuple[str, float]] = []
    while pool and len(selected) < k:
        best_i, best_val = 0, None
        for i, (cid, score) in enumerate(pool):
            rel = score / best_score
            div = max(
                (jaccard(doc_shingles.get(cid, set()), doc_shingles.get(s, set()))
                 for s, _ in selected),
                default=0.0,
            )
            val = lam * rel - (1 - lam) * div
            if best_val is None or val > best_val:
                best_i, best_val = i, val
        selected.append(pool.pop(best_i))
    return selected


def expand_graph(
    ranked: list[tuple[str, float]],
    neighbors: dict[str, list[str]],
    hops: int = 1,
    penalty: float = 0.5,
    seed_n: int = 5,
) -> list[tuple[str, float]]:
    """related_chunks를 따라 이웃을 후보에 끌어온다 (`ingestion.yaml: max_hops`).

    상위 `seed_n`개를 씨앗으로 1홉씩 퍼뜨리며 점수에 `penalty`를 곱한다.
    이미 있는 후보는 더 높은 점수를 유지한다. 홉이 늘수록 정밀도가 떨어지므로
    `ingestion.yaml`이 2홉을 상한으로 선언해 두었다 — 이 함수는 그 선언을
    **측정 가능하게** 만드는 것이 목적이다.
    """
    if hops <= 0:
        return ranked
    scores = dict(ranked)
    frontier = [cid for cid, _ in ranked[:seed_n]]
    for hop in range(1, hops + 1):
        nxt = []
        for cid in frontier:
            base = scores.get(cid, 0.0)
            for nb in neighbors.get(cid, []):
                cand = base * (penalty ** hop)
                if cand > scores.get(nb, 0.0):
                    scores[nb] = cand
                    nxt.append(nb)
        frontier = nxt
        if not frontier:
            break
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


# ─────────────────────────────────────────────────────────────
# 순위 지표
# ─────────────────────────────────────────────────────────────
def recall_at_k(ranked: list[str], qrel: dict[str, int], k: int) -> float:
    """정답 중 상위 k에 든 비율. 단일 정답이면 success@k와 같다."""
    rel = {c for c, g in qrel.items() if g > 0}
    if not rel:
        return 0.0
    return len(rel & set(ranked[:k])) / len(rel)


def success_at_k(ranked: list[str], qrel: dict[str, int], k: int) -> float:
    """정답이 하나라도 상위 k에 들었는가 (hit rate)."""
    rel = {c for c, g in qrel.items() if g > 0}
    return 1.0 if rel & set(ranked[:k]) else 0.0


def mrr_at_k(ranked: list[str], qrel: dict[str, int], k: int) -> float:
    for pos, cid in enumerate(ranked[:k], start=1):
        if qrel.get(cid, 0) > 0:
            return 1.0 / pos
    return 0.0


def ndcg_at_k(ranked: list[str], qrel: dict[str, int], k: int) -> float:
    """등급 relevance를 반영한 순위 품질.

    복수 정답을 도입하면 Recall/MRR만으로는 부족하다 — '정답 2개가 1·2위'와
    '정답 2개가 1·10위'를 구분하지 못하기 때문이다. nDCG는 구분한다.
    """
    rel = {c: g for c, g in qrel.items() if g > 0}
    if not rel:
        return 0.0
    dcg = sum(
        rel.get(cid, 0) / math.log2(pos + 1)
        for pos, cid in enumerate(ranked[:k], start=1)
    )
    ideal = sorted(rel.values(), reverse=True)[:k]
    idcg = sum(g / math.log2(pos + 1) for pos, g in enumerate(ideal, start=1))
    return dcg / idcg if idcg else 0.0


# ─────────────────────────────────────────────────────────────
# qrels
# ─────────────────────────────────────────────────────────────
def load_qrels(paths: list[Path]) -> tuple[dict[str, dict[str, int]], dict[str, dict]]:
    """등급 qrels 파일 여러 개를 병합한다.

    한 줄 형식:
        {"query": ..., "qrel": {"<chunk_id>": <grade>}, "grade_source": {...}, ...}

    뒤에 오는 파일이 앞 파일의 같은 (query, chunk_id) 등급을 덮어쓴다.
    자동 생성분을 먼저, 사람 판정분을 나중에 두는 순서를 전제한다 —
    사람 판정이 자동 등급을 이기는 것이 의도된 동작이다.
    """
    qrels: dict[str, dict[str, int]] = {}
    meta: dict[str, dict] = {}
    for p in paths:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            q = row["query"]
            qrels.setdefault(q, {}).update(
                {c: int(g) for c, g in (row.get("qrel") or {}).items()}
            )
            m = meta.setdefault(q, {})
            for key in ("question_origin", "category", "audience", "confidence", "origin"):
                if row.get(key) is not None:
                    m[key] = row[key]
            if row.get("grade_source"):
                m.setdefault("grade_source", {}).update(row["grade_source"])
    return qrels, meta


def pairs_to_qrels(path: Path) -> tuple[dict[str, dict[str, int]], dict[str, dict]]:
    """구형 golden_retrieval.jsonl(단일 정답)을 등급 3 qrels로 올린다.

    같은 질의가 여러 청크에 걸려 있으면 전부 등급 3이 된다 — 단일 라벨 편향을
    없애는 최소한의 조치이며, `docs/TEST-RESULTS.md` §9가 지적한 문제다.
    """
    qrels: dict[str, dict[str, int]] = {}
    meta: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        q = row["query"]
        qrels.setdefault(q, {})[row["expected_chunk_id"]] = 3
        m = meta.setdefault(q, {})
        for key in ("question_origin", "category", "audience", "confidence"):
            if row.get(key) is not None:
                m[key] = row[key]
    return qrels, meta
