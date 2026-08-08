#!/usr/bin/env python3
"""검색 평가 — T-12의 실행 가능한 부분과 T-14/T-15 게이트.

이 파일이 하는 일은 **해석**이다. 순위와 지표 계산은 `tools/retrieval.py`에 있다.
여기서는 "어느 수치가 유효한가"를 판정하고, 무효한 조합은 실행을 거부한다.

왜 어휘 검색만 하는가
    dense 검색은 임베딩 모델과 벡터 DB가 필요하고 폐쇄망·CI에서 못 돌린다. 반면
    BM25는 순수 파이썬으로 되고, 이 코퍼스는 영어 식별자(`PreToolUse`, `RFC 8707`)
    비중이 높아 어휘 검색이 실제로 하이브리드의 한 축이다.
    **여기서 나온 수치는 하이브리드 성능의 하한이다.**

    진짜 하이브리드를 재려면 `--dense-runs`를 쓴다. 외부에서 벡터 DB로 뽑은 순위
    파일을 받아 BM25와 RRF 융합한다. 이 저장소에 임베딩 의존성을 넣지 않고도
    T-12의 나머지 절반을 열 수 있다. 포맷은 `docs/TEST-PLAN.md` §3 참조.

누출 방지 — 이 도구의 핵심 규칙
    `retrieval_questions`로 골든셋을 만들었으므로, 그 질문을 색인한 뷰(`fields`)로
    평가하면 정답을 색인해 두고 찾는 셈이다(실측 Recall@10 = 1.000, 순수 누출).
    이 도구는 그것을 하드코딩된 뷰 이름으로 막지 않고 **실측한다** —
    질의 문자열이 정답 문서의 뷰 텍스트에 그대로 들어 있는 비율을 재고,
    임계값을 넘으면 실행을 거부한다. 측정으로 판정하는 것이 이 저장소의 규칙이다.

사용법:
    # 자동 골든셋 — 본문 전용만 유효
    python3 tools/eval_retrieval.py kb/manifest.jsonl tests/golden_retrieval.jsonl --mode body

    # 등급 qrels (복수 정답)
    python3 tools/eval_retrieval.py kb/manifest.jsonl \\
        --qrels tests/qrels_auto.jsonl tests/qrels_adjudicated.jsonl

    # held-out — 융합·재순위·확장이 유효한 유일한 세트
    python3 tools/eval_retrieval.py kb/manifest.jsonl \\
        --heldout tests/heldout_queries.jsonl --negatives tests/negative_queries.jsonl \\
        --views body,fields --fuse rrf --rerank mmr --expand-hops 1

    # CI 회귀 게이트 (T-14)
    python3 tools/eval_retrieval.py kb/manifest.jsonl --qrels tests/qrels_auto.jsonl \\
        --baseline tests/baseline_retrieval.json --max-drop 0.02
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from retrieval import (  # noqa: E402
    BM25,
    build_view,
    expand_graph,
    load_manifest,
    load_qrels,
    mmr,
    mrr_at_k,
    ndcg_at_k,
    pairs_to_qrels,
    recall_at_k,
    related_map,
    rrf,
    shingles,
    success_at_k,
    view_text,
)

KS = (1, 3, 5, 10)
# 질의가 정답 문서의 뷰 텍스트에 그대로 들어 있는 비율이 이 값을 넘으면 누출로 본다.
# 실측 근거: `fields` 뷰는 retrieval_questions를 통째로 색인하므로 1.0에 가깝고,
# `body` 뷰는 질문이 본문 어휘에서 파생됐어도 문장 단위로는 거의 일치하지 않는다.
LEAKAGE_THRESHOLD = 0.10


# ─────────────────────────────────────────────────────────────
# 누출 측정
# ─────────────────────────────────────────────────────────────
def leakage_rate(rows: list[dict], root: Path, view: str, qrels: dict) -> float:
    """질의가 정답 문서의 뷰 텍스트에 축자적으로 등장하는 비율."""
    texts = {r["chunk_id"]: view_text(r, root, view).lower() for r in rows}
    hit = total = 0
    for q, qrel in qrels.items():
        gold = [c for c, g in qrel.items() if g > 0]
        if not gold:
            continue
        total += 1
        if any(q.lower().strip() in texts.get(c, "") for c in gold):
            hit += 1
    return hit / total if total else 0.0


# ─────────────────────────────────────────────────────────────
# 순위 생성
# ─────────────────────────────────────────────────────────────
def load_dense_runs(path: Path) -> dict[str, list[str]]:
    """외부에서 생성한 dense 순위 파일.

    한 줄 형식: {"query": ..., "ranking": ["<chunk_id>", ...], "model": "..."}
    """
    runs = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        runs[row["query"]] = list(row["ranking"])
    return runs


def make_ranker(rows, root, views, dense, fuse, rrf_k, rerank, mmr_lambda,
                hops, penalty, candidates, topk):
    lexical = [v for v in views if v != "dense"]
    indexes = {v: BM25(build_view(rows, root, v)) for v in lexical}
    doc_sh = {r["chunk_id"]: shingles(view_text(r, root, "body")) for r in rows} \
        if rerank == "mmr" else {}
    rel = related_map(rows) if hops else {}

    def rank(query: str):
        rankings, primary = [], []
        for v in views:
            if v == "dense":
                rankings.append((dense.get(query) or [])[:candidates])
                continue
            res = indexes[v].search(query, k=candidates, hangul_n=4 if v == "ngram" else 2)
            rankings.append([c for c, _ in res])
            if not primary:
                primary = res
        if len(rankings) == 1 and fuse == "none":
            ranked = primary if primary else [(c, 1.0) for c in rankings[0]]
        else:
            ranked = rrf(rankings, rrf_k)
        if hops:
            ranked = expand_graph(ranked, rel, hops, penalty)
        if rerank == "mmr":
            ranked = mmr(ranked, doc_sh, mmr_lambda, k=topk)
        # 점수 하한(기권) 판정은 융합 점수가 아니라 1차 어휘 점수로 한다.
        # RRF 점수는 1/60 스케일이라 절대 임계값의 의미가 없다.
        top_lex = primary[0][1] if primary else 0.0
        return ranked[:topk], top_lex

    return rank


# ─────────────────────────────────────────────────────────────
# 평가
# ─────────────────────────────────────────────────────────────
def evaluate(rank, qrels: dict, meta: dict) -> dict:
    n = 0
    acc = {f"recall@{k}": 0.0 for k in KS}
    acc.update({f"success@{k}": 0.0 for k in KS})
    acc["mrr@10"] = 0.0
    acc["ndcg@10"] = 0.0
    misses: Counter = Counter()
    hijack: Counter = Counter()
    own: Counter = Counter()
    by_origin: dict[str, list] = defaultdict(list)

    for q, qrel in qrels.items():
        if not any(g > 0 for g in qrel.values()):
            continue
        ranked, _ = rank(q)
        ids = [c for c, _ in ranked]
        n += 1
        row = {f"recall@{k}": recall_at_k(ids, qrel, k) for k in KS}
        row.update({f"success@{k}": success_at_k(ids, qrel, k) for k in KS})
        row["mrr@10"] = mrr_at_k(ids, qrel, 10)
        row["ndcg@10"] = ndcg_at_k(ids, qrel, 10)
        for key, val in row.items():
            acc[key] += val
        if row["success@10"] == 0.0:
            for c, g in qrel.items():
                if g > 0:
                    misses[c] += 1
        # T-15 어트랙터 — 정답이 아닌데 1위를 차지한 청크
        if ids and qrel.get(ids[0], 0) == 0:
            hijack[ids[0]] += 1
        for c, g in qrel.items():
            if g > 0:
                own[c] += 1
        by_origin[meta.get(q, {}).get("question_origin") or "?"].append(row)

    out = {"n": n}
    out.update({k: round(v / n, 4) if n else 0.0 for k, v in acc.items()})
    out["miss_rate"] = round(1.0 - (acc["success@10"] / n), 4) if n else 0.0
    out["unfindable"] = misses.most_common(15)
    out["attractor"] = [
        {"chunk_id": c, "hijack": h, "own_questions": own.get(c, 0),
         "ratio": round(h / max(1, own.get(c, 0)), 2)}
        for c, h in hijack.most_common(10)
    ]
    out["by_origin"] = {}
    for origin, xs in sorted(by_origin.items()):
        m = len(xs)
        out["by_origin"][origin] = {
            "n": m,
            "recall@10": round(sum(x["recall@10"] for x in xs) / m, 4),
            "ndcg@10": round(sum(x["ndcg@10"] for x in xs) / m, 4),
            "mrr@10": round(sum(x["mrr@10"] for x in xs) / m, 4),
        }
    return out


def auc(pos: list[float], neg: list[float]) -> float:
    """무작위 범위-안 질의가 무작위 범위-밖 질의보다 높은 점수를 받을 확률.

    Mann-Whitney U 통계다. 0.5면 점수에 신호가 전혀 없다는 뜻이고,
    1.0이면 완전히 분리된다는 뜻이다. 임의의 하한 하나를 고르는 것보다
    **하한이라는 것이 가능하기는 한가**를 먼저 답하는 지표다.
    """
    if not pos or not neg:
        return 0.0
    wins = sum(
        1.0 if p > n else 0.5 if p == n else 0.0
        for p in pos for n in neg
    )
    return wins / (len(pos) * len(neg))


def evaluate_negatives(rank, queries: list[str], in_scope: list[float],
                       floors=(4, 6, 8, 10, 12, 14, 16, 20)) -> dict:
    """KB 범위 밖 질의에 무언가를 답해버리는 정도.

    어트랙터 청크는 정의상 관련 없는 질의에도 반응하므로 이 지표가 T-15의
    두 번째 각도다.

    단일 하한에서의 오응답률만 내지 않는 이유
        하한을 하나 고르면 그 값이 정당한지 알 수 없다. 범위 안 질의를 함께 받아
        분리도(AUC)와 하한별 맞교환표를 낸다. 분리도가 0.5 근처면 **어떤 하한도
        작동하지 않는다**는 뜻이고, 그때 하한을 설정에 적어두면 작동하지 않는
        통제를 작동한다고 적는 셈이 된다.
    """
    top: Counter = Counter()
    scores = []
    for q in queries:
        ranked, lex = rank(q)
        scores.append(round(lex, 3))
        if ranked:
            top[ranked[0][0]] += 1
    n = len(queries)
    tradeoff = [
        {
            "floor": f,
            "false_answer_rate": round(sum(1 for x in scores if x >= f) / n, 4) if n else 0.0,
            "in_scope_abstain_rate": round(
                sum(1 for x in in_scope if x < f) / len(in_scope), 4) if in_scope else 0.0,
        }
        for f in floors
    ]
    srt = sorted(scores)
    return {
        "n": n,
        "separability_auc": round(auc(in_scope, scores), 4),
        "top_score_p50": srt[n // 2] if n else 0.0,
        "top_score_max": max(scores) if scores else 0.0,
        "in_scope_p50": round(sorted(in_scope)[len(in_scope) // 2], 3) if in_scope else 0.0,
        "floor_tradeoff": tradeoff,
        "most_attracted": top.most_common(5),
    }


# ─────────────────────────────────────────────────────────────
# 기준선 회귀 (T-14)
# ─────────────────────────────────────────────────────────────
GATE_KEYS = ("ndcg@10", "recall@10")


CONFIG_KEYS = ("views", "fuse", "rerank", "expand_hops")


def check_baseline(report: dict, baseline: dict, max_drop: float) -> list[str]:
    """기준선 대비 낙폭을 본다.

    먼저 **설정이 같은지** 확인한다. 뷰나 융합 방식이 다르면 두 수치는 애초에
    비교 대상이 아니며, 그걸 모른 채 비교하면 게이트가 엉뚱한 것을 통과시키거나
    막는다. 설정이 달라졌다면 기준선을 다시 만들어야 한다.
    """
    bad = []
    for key in CONFIG_KEYS:
        if key in baseline and baseline[key] != report.get(key):
            bad.append(
                f"설정 불일치 {key}: 기준선 {baseline[key]!r} vs 이번 실행 "
                f"{report.get(key)!r} — 같은 조건이 아니므로 비교할 수 없습니다"
            )
    if bad:
        return bad
    for set_name, base in (baseline.get("sets") or {}).items():
        cur = (report.get("sets") or {}).get(set_name)
        if not cur:
            bad.append(f"{set_name}: 기준선에 있으나 이번 실행에 없음 — 세트가 사라졌는가?")
            continue
        for key in GATE_KEYS:
            if key not in base:
                continue
            drop = base[key] - cur.get(key, 0.0)
            if drop > max_drop:
                bad.append(
                    f"{set_name}.{key}: {base[key]:.4f} → {cur.get(key, 0.0):.4f} "
                    f"(낙폭 {drop:.4f} > 허용 {max_drop:.4f})"
                )
    return bad


# ─────────────────────────────────────────────────────────────
# 출력
# ─────────────────────────────────────────────────────────────
def print_set(name: str, res: dict, note: str = "") -> None:
    print(f"[{name}]  n={res['n']}{('  ' + note) if note else ''}")
    print(f"  Recall@1={res['recall@1']}  @3={res['recall@3']}  @5={res['recall@5']}  "
          f"@10={res['recall@10']}")
    print(f"  nDCG@10={res['ndcg@10']}  MRR@10={res['mrr@10']}  "
          f"Success@10={res['success@10']}  검색 실패율={res['miss_rate']}")
    if res["by_origin"]:
        print("  출처별:")
        for origin, r in res["by_origin"].items():
            print(f"    {origin:14s} n={r['n']:3d}  Recall@10={r['recall@10']:.4f}  "
                  f"nDCG@10={r['ndcg@10']:.4f}  MRR@10={r['mrr@10']:.4f}")
    if res["unfindable"]:
        print("  자기 질문으로도 못 찾은 청크:")
        for cid, c in res["unfindable"][:8]:
            print(f"    {c}회 실패  {cid}")
    if res["attractor"]:
        print("  T-15 어트랙터 (정답이 아닌데 1위를 차지한 횟수):")
        for a in res["attractor"][:5]:
            print(f"    {a['hijack']:3d}회  {a['chunk_id']:38s} "
                  f"(자기 질문 {a['own_questions']}개, 비율 {a['ratio']})")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("golden", type=Path, nargs="?", default=None,
                    help="구형 단일정답 골든셋 (tests/golden_retrieval.jsonl)")
    ap.add_argument("--qrels", type=Path, nargs="*", default=None,
                    help="등급 qrels. 여러 개면 뒤 파일이 앞을 덮어쓴다")
    ap.add_argument("--heldout", type=Path, default=None)
    ap.add_argument("--negatives", type=Path, default=None)
    ap.add_argument("--dense-runs", type=Path, default=None)
    ap.add_argument("--mode", choices=["body", "fields", "ngram", "all"], default="body",
                    help="단일 뷰 지정. --views의 축약형")
    ap.add_argument("--views", default=None,
                    help="쉼표 구분. 예: body,fields,dense")
    ap.add_argument("--compare-modes", action="store_true")
    ap.add_argument("--fuse", choices=["none", "rrf"], default="rrf")
    ap.add_argument("--rrf-k", type=int, default=60)
    ap.add_argument("--rerank", choices=["none", "mmr"], default="none")
    ap.add_argument("--mmr-lambda", type=float, default=0.7)
    ap.add_argument("--expand-hops", type=int, default=0, choices=[0, 1, 2])
    ap.add_argument("--expand-penalty", type=float, default=0.5)
    ap.add_argument("--candidates", type=int, default=24)
    ap.add_argument("--topk", type=int, default=10)
    ap.add_argument("--baseline", type=Path, default=None)
    ap.add_argument("--write-baseline", type=Path, default=None,
                    help="현재 수치를 기준선으로 기록한다. 갱신은 반드시 커밋에 포함할 것")
    ap.add_argument("--max-drop", type=float, default=0.02)
    ap.add_argument("--allow-leakage", action="store_true",
                    help="누출 가드를 끈다. 진단 목적으로만 쓰고 수치를 보고하지 말 것")
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args()

    rows = load_manifest(a.manifest)
    root = a.manifest.parent

    # ── 질의 세트 구성
    sets: dict[str, tuple[dict, dict]] = {}
    if a.qrels:
        sets["auto"] = load_qrels(a.qrels)
    elif a.golden:
        sets["auto"] = pairs_to_qrels(a.golden)
    if a.heldout:
        held_q, held_m = load_qrels([a.heldout])
        for origin in sorted({(held_m.get(q, {}).get("origin") or "heldout") for q in held_q}):
            sub = {q: v for q, v in held_q.items()
                   if (held_m.get(q, {}).get("origin") or "heldout") == origin}
            # held-out은 출처별로 반드시 분리 집계한다. 합산 점수는 내지 않는다.
            sets[f"heldout:{origin}"] = (sub, held_m)
    if not sets and not a.negatives:
        ap.error("평가할 질의 세트가 없습니다 (golden / --qrels / --heldout / --negatives 중 하나 필요)")

    views = [v.strip() for v in a.views.split(",")] if a.views else \
        (["body", "fields", "ngram"] if a.mode == "all" else [a.mode])
    if a.dense_runs and "dense" not in views:
        views.append("dense")
    dense = load_dense_runs(a.dense_runs) if a.dense_runs else {}

    report = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "views": views, "fuse": a.fuse, "rerank": a.rerank,
        "expand_hops": a.expand_hops, "candidates": a.candidates,
        "sets": {}, "leakage": {},
    }

    modes = ["body", "fields", "ngram"] if a.compare_modes else None

    # ── 누출 가드: 하드코딩이 아니라 실측으로 판정한다.
    #    --compare-modes가 훑을 뷰까지 미리 재 둔다. 재지 않은 뷰를 "누출 아님"으로
    #    기본값 처리하면 가드가 조용히 뚫린다.
    measured = list(dict.fromkeys([v for v in views if v != "dense"] + (modes or [])))
    for set_name, (qrels, _) in sets.items():
        for v in measured:
            rate = leakage_rate(rows, root, v, qrels)
            report["leakage"][f"{set_name}/{v}"] = round(rate, 4)
            if v not in views:
                continue  # --compare-modes 전용 뷰는 기록만 하고 아래에서 건너뛴다
            if rate > LEAKAGE_THRESHOLD and not a.allow_leakage:
                print(
                    f"중단: 세트 '{set_name}'의 질의 {rate:.1%}가 뷰 '{v}'의 정답 문서 "
                    f"텍스트에 그대로 들어 있습니다 (임계 {LEAKAGE_THRESHOLD:.0%}).\n"
                    f"       정답을 색인해 두고 그것으로 찾는 것이므로 이 수치는 "
                    f"성능이 아니라 누출입니다.\n"
                    f"       본문 전용(--mode body)으로 재는 것이 유효한 측정이며, "
                    f"융합·재순위는 held-out 세트에서만 의미가 있습니다.",
                    file=sys.stderr,
                )
                return 2

    rank = make_ranker(rows, root, views, dense, a.fuse, a.rrf_k, a.rerank,
                       a.mmr_lambda, a.expand_hops, a.expand_penalty,
                       a.candidates, a.topk)

    if modes:
        # 진단 모드 — 뷰별 단독 성능 비교. 누출 가드에 걸리는 뷰는 건너뛴다.
        for m in modes:
            if any(report["leakage"].get(f"{s}/{m}", 0.0) > LEAKAGE_THRESHOLD for s in sets):
                print(f"[뷰 {m}] 건너뜀 — 누출 (위 가드 참조)\n")
                continue
            r = make_ranker(rows, root, [m], {}, "none", a.rrf_k, "none",
                            a.mmr_lambda, 0, a.expand_penalty, a.candidates, a.topk)
            for set_name, (qrels, meta) in sets.items():
                print_set(f"{set_name} / 뷰 {m}", evaluate(r, qrels, meta))
        return 0

    for set_name, (qrels, meta) in sets.items():
        res = evaluate(rank, qrels, meta)
        report["sets"][set_name] = res
        print_set(set_name, res, note=f"뷰={'+'.join(views)} 융합={a.fuse} 재순위={a.rerank}")

    if a.negatives:
        neg = [json.loads(l)["query"]
               for l in a.negatives.read_text(encoding="utf-8").splitlines() if l.strip()]
        # 분리도를 재려면 범위 안 질의의 점수 분포가 필요하다.
        in_scope = [rank(q)[1] for qrels, _ in sets.values() for q in qrels]
        res = evaluate_negatives(rank, neg, in_scope)
        report["negatives"] = res
        print(f"[음성 질의 — KB 범위 밖]  n={res['n']}")
        print(f"  분리도 AUC={res['separability_auc']}  "
              f"(0.5 = 점수에 신호 없음 → 어떤 하한도 작동하지 않음)")
        print(f"  1위 점수 중앙값: 범위 안={res['in_scope_p50']}  "
              f"범위 밖={res['top_score_p50']}  (범위 밖 최대={res['top_score_max']})")
        print("  하한   범위밖 오응답   범위안 기권(손실)")
        for t in res["floor_tradeoff"]:
            print(f"  {t['floor']:4.0f}       {t['false_answer_rate']:.2f}"
                  f"            {t['in_scope_abstain_rate']:.2f}")
        if res["most_attracted"]:
            print("  범위 밖 질의를 가장 많이 끌어간 청크:")
            for cid, c in res["most_attracted"]:
                print(f"    {c}회  {cid}")
        print()

    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if a.write_baseline:
        snap = {k: report[k] for k in CONFIG_KEYS}
        snap["generated"] = report["generated"]
        snap["note"] = ("T-14 회귀 기준선. 갱신은 명시적으로 커밋에 포함해야 한다 — "
                        "그래야 열화가 조용히 지나가지 않는다.")
        snap["sets"] = {
            name: {k: res[k] for k in GATE_KEYS} for name, res in report["sets"].items()
        }
        a.write_baseline.write_text(
            json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"기준선 기록: {a.write_baseline}")

    if a.baseline:
        if not a.baseline.exists():
            print(f"중단: 기준선 파일이 없습니다: {a.baseline}", file=sys.stderr)
            return 2
        bad = check_baseline(report, json.loads(a.baseline.read_text(encoding="utf-8")),
                             a.max_drop)
        if bad:
            print("T-14 검색 회귀 게이트 실패:", file=sys.stderr)
            for b in bad:
                print(f"  {b}", file=sys.stderr)
            print("  수치가 내려간 것이 의도한 결과라면 --write-baseline으로 기준선을 "
                  "갱신해 같은 커밋에 포함하십시오.", file=sys.stderr)
            return 1
        print(f"T-14 통과 — 기준선 대비 낙폭 {a.max_drop} 이내")
    return 0


if __name__ == "__main__":
    sys.exit(main())
