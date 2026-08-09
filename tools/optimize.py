#!/usr/bin/env python3
"""검색 산출물 최적화 하네스 — OPRO/GEPA 루프의 고정점.

## 이 하네스가 LLM을 호출하지 않는 이유

호출하면 벤더가 하나로 고정되고 `tools/`에 의존성이 생긴다. 대신 **역할을 나눈다.**

    하네스   무엇을 고칠지 고르고, 실패를 진단해 성찰 요청을 만들고,
             후보를 채점하고, Pareto 프런티어를 관리하고, 감사 기록을 남긴다.
    LLM      성찰 요청을 읽고 후보를 쓴다. Claude Code / Gemini CLI / GPT /
             로컬 모델 무엇이든 된다. 하네스는 어느 쪽이 썼는지 신경 쓰지 않는다.

    "하네스가 불변이고 모델이 교체 가능하다"가 이 설계의 요점이다.
    사내에 벤더가 여럿이고 앞으로 더 바뀔 것이므로 그 축을 밖으로 뺀다.

## 왜 GEPA 형태인가

OPRO는 (프롬프트, 점수) 궤적을 보여주고 더 높은 점수를 내라고 시킨다.
GEPA(ICLR 2026)는 **실패 궤적을 자연어로 성찰**하게 하고 Pareto 프런티어에서
서로 다른 강점을 조합한다. 후자가 MIPROv2를 10% 이상 앞선다고 보고됐다.

여기서는 성찰 재료로 "이 청크가 정답인데 못 찾은 질의 + 대신 1위를 가져간 청크"를
넘긴다. 점수만 넘기는 것보다 고칠 지점이 분명해진다.

## 안전장치 — 이게 도구의 절반이다

1. **test split은 읽지 않는다.** 최적화에 노출된 세트로는 성능을 주장할 수 없다.
   `docs/TEST-RESULTS.md` §12.8이 이 저장소가 이미 한 번 밟은 함정이다.
2. **누출 검사.** 후보 질문이 dev 질의를 베끼면 점수가 오른다. 그건 개선이 아니라
   정답을 색인하는 것이다. `eval_retrieval.leakage_rate`와 같은 기준으로 막는다.
3. **부수 피해 측정.** 청크 하나의 질문을 고치면 그 청크가 다른 질의의 1위를
   뺏을 수 있다. 대상 질의 점수와 **전체 점수를 따로** 보고 둘 다 프런티어에 넣는다.
4. **생성물에 쓰지 않는다.** 채택은 `kb/authored/`(빌더 입력)에만 반영한다.
5. **출처 표기.** 채택된 질문에는 `questions_origin: optimized:<run>`가 붙는다.
   `confidence`가 청크에서 하는 일과 같다 — 기계가 만든 것은 그렇게 적는다.

## 사용법

    # 1) 가장 못 찾는 청크를 고르고 성찰 요청을 만든다
    python3 tools/optimize.py propose --run R-001 --top 3

    # 2) 요청을 아무 LLM에나 준다 (벤더 무관). 후보를 JSONL로 받는다.
    #    형식: {"run","chunk_id","candidate_id","retrieval_questions","rationale"}

    # 3) 채점한다. 누출·부수 피해를 함께 본다
    python3 tools/optimize.py score --run R-001 --candidates cands.jsonl

    # 4) 프런티어를 보고 채택한다 (kb/authored/ 에만 쓴다)
    python3 tools/optimize.py apply --run R-001 --candidate c2
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from retrieval import (  # noqa: E402
    BM25,
    build_view,
    expand_graph,
    load_manifest,
    load_qrels,
    ndcg_at_k,
    recall_at_k,
    related_map,
    rrf,
    tokenize,
)

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "tests/optimization"

# 프로덕션 검색 설정. kb/ingestion.yaml의 retrieval.lexical과 같아야 한다 —
# 다른 설정으로 최적화하면 실제로 쓰지 않는 구성을 개선하게 된다.
VIEWS = ["body", "fields", "index"]
HOPS = 1
CANDIDATES = 24

# 후보 질문이 dev 질의를 이만큼 베끼면 거부한다. 0에 가깝게 잡는 이유는
# 질문을 새로 쓰는 일에 질의문을 그대로 옮길 정당한 이유가 없기 때문이다.
LEAK_LIMIT = 0.05
# 한 질문이 어떤 dev 질의와 이만큼 겹치면 근사 복사로 본다.
NEAR_COPY_JACCARD = 0.6


# ─────────────────────────────────────────────────────────────
# 세트 적재 — test는 읽지 않는다
# ─────────────────────────────────────────────────────────────
def load_dev(heldout: Path) -> tuple[dict, dict]:
    """dev split만 돌려준다.

    test split이 파일에 있어도 **읽지 않고 버린다.** 최적화가 한 번이라도 본 질의는
    그 뒤로 편향 없는 추정치를 내지 못한다. 이 함수가 그 경계다.
    """
    qrels, meta = load_qrels([heldout])
    dev = {q: v for q, v in qrels.items() if (meta.get(q, {}).get("split") or "") == "dev"}
    skipped = len(qrels) - len(dev)
    if skipped:
        print(f"  test split {skipped}건은 읽지 않았습니다 (게이트 전용).", file=sys.stderr)
    if not dev:
        raise SystemExit(
            "dev split 질의가 없습니다. 최적화는 dev에서만 합니다 — "
            "test로 최적화하면 게이트가 의미를 잃습니다."
        )
    return dev, meta


# ─────────────────────────────────────────────────────────────
# 채점
# ─────────────────────────────────────────────────────────────
def make_ranker(rows: list[dict]):
    bms = {v: BM25(build_view(rows, REPO / "kb", v)) for v in VIEWS}
    rel = related_map(rows)

    def rank(query: str) -> list[str]:
        fused = rrf([[c for c, _ in bms[v].search(query, k=CANDIDATES)] for v in VIEWS])
        return [c for c, _ in expand_graph(fused, rel, HOPS)][:10]

    return rank


def score(rows: list[dict], dev: dict, target: str | None = None) -> dict:
    """전체 점수와 대상 청크 관련 질의의 점수를 따로 낸다.

    둘을 나누는 이유: 청크 하나의 질문을 고치면 그 청크는 잘 찾히는데 다른 질의의
    1위를 뺏을 수 있다. 평균만 보면 그 맞교환이 안 보인다.
    """
    rank = make_ranker(rows)
    g_nd = g_rc = 0.0
    l_nd = l_n = 0
    local_nd = 0.0
    for q, qrel in dev.items():
        ids = rank(q)
        nd = ndcg_at_k(ids, qrel, 10)
        g_nd += nd
        g_rc += recall_at_k(ids, qrel, 10)
        if target and qrel.get(target, 0) > 0:
            local_nd += nd
            l_n += 1
    n = len(dev)
    return {
        "global_ndcg@10": round(g_nd / n, 4),
        "global_recall@10": round(g_rc / n, 4),
        "local_ndcg@10": round(local_nd / l_n, 4) if l_n else None,
        "local_n": l_n,
    }


def leakage(candidate_questions: list[str], dev: dict) -> float:
    """후보 질문이 dev 질의를 베낀 비율.

    축자 포함만 보면 어미 한두 개만 바꿔도 통과한다. 토큰 Jaccard로 근사 복사까지 잡는다.

    **이 검사의 한계를 분명히 해 둔다.** 의미가 같고 표현만 다른 질문은 막지 못하고,
    막아서도 안 된다 — 실제 질의와 비슷한 질문을 쓰는 것이 이 작업의 목적이기 때문이다.
    축자 복사와 의미 유사의 경계는 통계로 정할 수 없다.
    **진짜 방어선은 이 검사가 아니라 test split이다.**
    """
    if not candidate_questions:
        return 0.0
    dev_toks = [set(tokenize(q)) for q in dev]
    hits = 0
    for cq in candidate_questions:
        ct = set(tokenize(cq))
        if not ct:
            continue
        best = max((len(ct & d) / len(ct | d) for d in dev_toks if d), default=0.0)
        if best >= NEAR_COPY_JACCARD:
            hits += 1
    return hits / len(candidate_questions)


def substitute(rows: list[dict], chunk_id: str, questions: list[str]) -> list[dict]:
    """후보를 반영한 rows 사본. **재빌드하지 않는다** — 질문은 manifest에만 있고
    `fields` 뷰가 그것을 읽으므로, 사본 하나로 후보를 채점할 수 있다."""
    out = copy.deepcopy(rows)
    for r in out:
        if r["chunk_id"] == chunk_id:
            r["retrieval_questions"] = list(questions)
    return out


# ─────────────────────────────────────────────────────────────
# 성찰 요청 (GEPA의 입력)
# ─────────────────────────────────────────────────────────────
def lost_gain(pos: int | None) -> float:
    """정답이 1위가 아니어서 잃은 nDCG 비율.

    실패 **건수**로 순위를 매기면 10위인 청크와 2위인 청크가 같아진다.
    상위 노출까지의 거리를 반영해야 어디를 고칠지 정해진다.
    상위 10에 없으면 전부 잃은 것으로 본다.
    """
    if pos is None:
        return 1.0
    import math
    return 1.0 - 1.0 / math.log2(pos + 1)


def diagnose(rows: list[dict], dev: dict, top: int) -> list[dict]:
    """dev에서 가장 손해가 큰 청크를 고르고 실패 사례를 붙인다."""
    rank = make_ranker(rows)
    by_id = {r["chunk_id"]: r for r in rows}
    failures: dict[str, list[dict]] = {}
    loss: dict[str, float] = {}
    for q, qrel in dev.items():
        ids = rank(q)
        for cid, grade in qrel.items():
            if grade < 3:
                continue
            pos = ids.index(cid) + 1 if cid in ids else None
            if pos == 1:
                continue
            loss[cid] = loss.get(cid, 0.0) + lost_gain(pos)
            failures.setdefault(cid, []).append({
                "query": q,
                "gold_rank": pos,
                "lost_gain": round(lost_gain(pos), 3),
                "won_instead": [
                    {"chunk_id": c, "title": by_id.get(c, {}).get("title", "")}
                    for c in ids[:3]
                ],
            })
    ranked = sorted(failures.items(), key=lambda kv: -loss[kv[0]])[:top]
    out = []
    for cid, fails in ranked:
        r = by_id[cid]
        body = (REPO / "kb" / r["file_path"]).read_text(encoding="utf-8")
        out.append({
            "chunk_id": cid,
            "title": r["title"],
            "section_path": r.get("section_path", ""),
            "category": r.get("category", ""),
            "tags": r.get("tags", []),
            "current_retrieval_questions": r.get("retrieval_questions", []),
            "body_excerpt": body.split("---", 2)[-1].strip()[:1200],
            "lost_gain_total": round(loss[cid], 3),
            "failures": fails,
        })
    return out


def build_request(rows: list[dict], dev: dict, run: str, top: int) -> dict:
    base = score(rows, dev)
    return {
        "run": run,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "objective": "dev 세트의 global_ndcg@10을 올린다. local만 올리고 global이 "
                     "내려가면 채택하지 않는다.",
        "baseline": base,
        "artifact": "retrieval_questions",
        "constraints": [
            "dev 질의 문장을 그대로 옮기지 말 것. 누출로 판정돼 자동 거부된다.",
            "청크 본문이 실제로 답하는 것만 질문으로 쓸 것. 본문에 없는 답을 "
            "약속하는 질문은 그 청크를 어트랙터로 만든다.",
            "영어 식별자(PreToolUse, RFC 8707 등)는 원문 그대로 둘 것.",
            "질문은 4~6개. 서로 다른 표현 층위를 섞을 것 — 정식 용어, 구어체, "
            "증상 서술, 역할 기반.",
        ],
        "output_format": {
            "file": "JSONL, 한 줄에 후보 하나",
            "fields": ["run", "chunk_id", "candidate_id", "retrieval_questions", "rationale"],
        },
        "targets": diagnose(rows, dev, top),
    }


# ─────────────────────────────────────────────────────────────
# Pareto 프런티어
# ─────────────────────────────────────────────────────────────
def pareto(entries: list[dict]) -> dict[str, list[str]]:
    """청크마다 (global, local) 두 목적에서 지배당하지 않는 후보의 id.

    **청크별로 나누는 것이 중요하다.** `local_ndcg@10`은 "그 청크가 정답인 질의들의
    점수"이므로 서로 다른 청크의 local을 한 프런티어에 놓으면 질의 난이도를 비교하는
    셈이 된다. 실제로 그렇게 만들었다가 청크가 다른 후보 넷 중 하나만 남았다.

    평균 하나로 줄이지 않는 이유는 GEPA의 요점 그대로다 — 서로 다른 강점을 가진
    후보를 남겨 두어야 다음 라운드에서 조합할 재료가 생긴다.
    """
    fronts: dict[str, list[str]] = {}
    by_chunk: dict[str, list[dict]] = {}
    for e in entries:
        by_chunk.setdefault(e["chunk_id"], []).append(e)

    def key(e):
        return (e["score"]["global_ndcg@10"], e["score"].get("local_ndcg@10") or 0.0)

    for chunk, group in by_chunk.items():
        front = []
        for e in group:
            g, l = key(e)
            if not any((key(o)[0] >= g and key(o)[1] >= l) and key(o) != (g, l)
                       for o in group):
                front.append(e["candidate_id"])
        fronts[chunk] = front
    return fronts


# ─────────────────────────────────────────────────────────────
# 명령
# ─────────────────────────────────────────────────────────────
def cmd_propose(a) -> int:
    rows = load_manifest(a.manifest)
    dev, _ = load_dev(a.heldout)
    req = build_request(rows, dev, a.run, a.top)
    RUNS.mkdir(parents=True, exist_ok=True)
    out = RUNS / f"{a.run}.request.json"
    out.write_text(json.dumps(req, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"성찰 요청: {out}")
    print(f"  기준선 global_ndcg@10={req['baseline']['global_ndcg@10']} "
          f"recall@10={req['baseline']['global_recall@10']}  (dev {len(dev)}건)")
    for t in req["targets"]:
        print(f"  대상 {t['chunk_id']:38s} 잃은 이득 {t['lost_gain_total']}  실패 {len(t['failures'])}건")
    print("\n이 파일을 아무 LLM에나 주고 후보 JSONL을 받으십시오 (벤더 무관).")
    return 0


def cmd_score(a) -> int:
    rows = load_manifest(a.manifest)
    dev, _ = load_dev(a.heldout)
    cands = [json.loads(l) for l in a.candidates.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    if not cands:
        raise SystemExit("후보가 없습니다.")

    entries = []
    for c in cands:
        cid, chunk = c["candidate_id"], c["chunk_id"]
        qs = c["retrieval_questions"]
        leak = leakage(qs, dev)
        base = score(rows, dev, target=chunk)
        if leak > LEAK_LIMIT:
            entries.append({
                "candidate_id": cid, "chunk_id": chunk, "rejected": "leakage",
                "leakage": round(leak, 4), "score": base,
            })
            continue
        s = score(substitute(rows, chunk, qs), dev, target=chunk)
        entries.append({
            "candidate_id": cid, "chunk_id": chunk, "leakage": round(leak, 4),
            "retrieval_questions": qs, "rationale": c.get("rationale", ""),
            "score": s,
            "delta_global": round(s["global_ndcg@10"] - base["global_ndcg@10"], 4),
            "delta_local": (round((s["local_ndcg@10"] or 0) - (base["local_ndcg@10"] or 0), 4)
                            if s.get("local_ndcg@10") is not None else None),
        })

    ok = [e for e in entries if "rejected" not in e]
    fronts = pareto(ok) if ok else {}

    # 청크별 최선을 **동시에** 적용하면 어떻게 되는가.
    # 개선이 더해진다는 보장이 없다 — 각 청크가 서로의 질의를 가져갈 수 있다.
    combined_ids, combined = [], None
    if ok:
        rows_all = rows
        for chunk, front in fronts.items():
            best = max((e for e in ok if e["candidate_id"] in front),
                       key=lambda e: e["delta_global"], default=None)
            if best and best["delta_global"] > 0:
                combined_ids.append(best["candidate_id"])
                rows_all = substitute(rows_all, chunk, best["retrieval_questions"])
        if combined_ids:
            combined = score(rows_all, dev)

    record = {
        "run": a.run,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dev_n": len(dev),
        "baseline": score(rows, dev),
        "views": VIEWS, "expand_hops": HOPS,
        "candidates": entries,
        "pareto_front_by_chunk": fronts,
        "combined": {"candidate_ids": combined_ids, "score": combined},
    }
    RUNS.mkdir(parents=True, exist_ok=True)
    out = RUNS / f"{a.run}.scored.json"
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"기준선 global_ndcg@10={record['baseline']['global_ndcg@10']}  (dev {len(dev)}건)")
    for e in entries:
        if "rejected" in e:
            print(f"  거부  {e['candidate_id']:6s} {e['chunk_id']:34s} "
                  f"누출 {e['leakage']} > {LEAK_LIMIT}")
            continue
        mark = "★" if e["candidate_id"] in fronts.get(e["chunk_id"], []) else " "
        print(f"  {mark}     {e['candidate_id']:6s} {e['chunk_id']:34s} "
              f"global {e['delta_global']:+.4f}  local {e['delta_local']}  "
              f"누출 {e['leakage']}")
    print("\n청크별 Pareto 프런티어:")
    for chunk, front in sorted(fronts.items()):
        print(f"  {chunk:34s} {front}")
    if combined:
        base_g = record["baseline"]["global_ndcg@10"]
        print(f"\n동시 적용 {combined_ids}: global_ndcg@10 {base_g} → "
              f"{combined['global_ndcg@10']} ({combined['global_ndcg@10'] - base_g:+.4f})")
        summed = sum(e["delta_global"] for e in ok if e["candidate_id"] in combined_ids)
        print(f"  개별 개선 합 {summed:+.4f} — 차이가 크면 후보끼리 서로의 질의를 "
              f"가져간 것입니다.")
    print(f"\n기록: {out}")
    if ok and max(e["delta_global"] for e in ok) <= 0:
        print("\n어떤 후보도 전체 점수를 올리지 못했습니다. 채택하지 마십시오.")
    return 0


def cmd_apply(a) -> int:
    rec = json.loads((RUNS / f"{a.run}.scored.json").read_text(encoding="utf-8"))
    match = [e for e in rec["candidates"] if e["candidate_id"] == a.candidate]
    if not match:
        raise SystemExit(f"후보 {a.candidate}를 {a.run}에서 찾지 못했습니다.")
    e = match[0]
    if "rejected" in e:
        raise SystemExit(f"후보 {a.candidate}는 {e['rejected']}로 거부됐습니다.")
    if e["delta_global"] <= 0 and not a.force:
        raise SystemExit(
            f"후보 {a.candidate}의 전체 점수 변화가 {e['delta_global']}입니다. "
            "개선이 아닌 것을 채택하려면 --force를 쓰고 이유를 커밋에 적으십시오."
        )

    src = REPO / "kb/authored" / f"{a.file}"
    if not src.exists():
        raise SystemExit(
            f"{src}가 없습니다. 이 청크는 빌더 입력이 kb/authored/에 없으므로 "
            "질문을 직접 바꿀 수 없습니다 — kb/corrections.yaml 경로를 쓰십시오."
        )
    print(f"채택 대상: {src}")
    print(f"  chunk_id  {e['chunk_id']}")
    print(f"  global    {e['delta_global']:+.4f}")
    print(f"  local     {e['delta_local']}")
    print("  새 retrieval_questions:")
    for q in e["retrieval_questions"]:
        print(f"    - {q}")
    print(f"\nfrontmatter의 retrieval_questions를 위 값으로 바꾸고 "
          f"`questions_origin: optimized:{a.run}`를 추가한 뒤 재빌드하십시오.")
    print("기계가 만든 것은 그렇게 표기합니다 — confidence가 하는 일과 같습니다.")
    return 0


def cmd_selftest(a) -> int:
    """안전장치가 실제로 발화하는지 확인한다 (T-18 원칙의 최적화 하네스판).

    이 하네스의 가치는 절반이 안전장치다. 발화한 적 없는 안전장치는
    작동을 보장하지 않는다.
    """
    import tempfile

    problems = []
    rows = load_manifest(a.manifest)
    dev, _ = load_dev(a.heldout)

    # 1) 누출 가드 — dev 질의를 그대로 옮긴 후보를 거부해야 한다
    a_query = next(iter(dev))
    if leakage([a_query], dev) <= LEAK_LIMIT:
        problems.append("누출 가드: dev 질의를 그대로 넣었는데 통과했습니다")
    if leakage(["전혀 관계없는 문장입니다 색인 어휘와 겹치지 않습니다"], dev) > LEAK_LIMIT:
        problems.append("누출 가드: 무관한 문장을 누출로 판정했습니다 (과탐)")

    # 2) test split 차단 — dev가 하나도 없으면 최적화를 거부해야 한다
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(json.dumps({"query": "테스트 전용 질의", "qrel": {"x": 3},
                             "origin": "user-log", "split": "test"},
                            ensure_ascii=False) + "\n")
        only_test = Path(tf.name)
    try:
        load_dev(only_test)
        problems.append("test 차단: test split만 있는 파일로 최적화가 시작됐습니다")
    except SystemExit:
        pass
    finally:
        only_test.unlink(missing_ok=True)

    # 3) 대입 채점이 원본을 건드리지 않아야 한다
    target = rows[0]["chunk_id"]
    before = list(rows[0]["retrieval_questions"])
    substitute(rows, target, ["바뀐 질문"])
    if rows[0]["retrieval_questions"] != before:
        problems.append("substitute가 원본 rows를 변경했습니다")

    # 4) Pareto가 청크별로 나뉘어야 한다
    fake = [
        {"candidate_id": "x", "chunk_id": "A",
         "score": {"global_ndcg@10": 0.5, "local_ndcg@10": 0.9}},
        {"candidate_id": "y", "chunk_id": "B",
         "score": {"global_ndcg@10": 0.4, "local_ndcg@10": 0.1}},
    ]
    fronts = pareto(fake)
    if set(fronts) != {"A", "B"} or fronts["B"] != ["y"]:
        problems.append(f"Pareto가 청크별로 나뉘지 않았습니다: {fronts}")

    for p in problems:
        print(f"  FAIL  {p}", file=sys.stderr)
    if problems:
        return 1
    print("  OK    최적화 하네스 안전장치 4종 (누출·test 차단·비파괴 대입·청크별 프런티어)")
    return 0


def cmd_status(a) -> int:
    if not RUNS.exists():
        print("최적화 기록이 없습니다.")
        return 0
    for f in sorted(RUNS.glob("*.scored.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        best = max((e["delta_global"] for e in rec["candidates"] if "rejected" not in e),
                   default=None)
        print(f"{rec['run']:8s} {rec['generated']}  후보 {len(rec['candidates'])}개  "
              f"프런티어 {rec['pareto_front']}  최대 개선 {best}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", type=Path, default=REPO / "kb/manifest.jsonl")
    ap.add_argument("--heldout", type=Path, default=REPO / "tests/heldout_queries.jsonl")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("propose", help="성찰 요청을 만든다")
    p.add_argument("--run", required=True)
    p.add_argument("--top", type=int, default=3)
    p.set_defaults(fn=cmd_propose)

    p = sub.add_parser("score", help="후보를 채점하고 프런티어를 낸다")
    p.add_argument("--run", required=True)
    p.add_argument("--candidates", type=Path, required=True)
    p.set_defaults(fn=cmd_score)

    p = sub.add_parser("apply", help="채택안을 보여준다 (kb/authored/ 에만 반영)")
    p.add_argument("--run", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--file", required=True, help="kb/authored/ 안의 파일명")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_apply)

    p = sub.add_parser("selftest", help="안전장치가 실제로 발화하는지 확인")
    p.set_defaults(fn=cmd_selftest)

    p = sub.add_parser("status", help="지금까지의 실행 요약")
    p.set_defaults(fn=cmd_status)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
