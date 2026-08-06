#!/usr/bin/env python3
"""RAG 청크 세트 감사 하네스.

`docs/TEST-PLAN.md`의 T-01 ~ T-08 시험 항목을 실행하고 JSON 리포트를 낸다.
외부 네트워크·API 키가 필요 없으므로 폐쇄망과 CI에서 그대로 돌아간다.

사용법:
    python3 tools/kb_audit.py kb/chunks --json out.json
    python3 tools/kb_audit.py <dir> --compare <other-dir>   # 두 세트 중복도 비교
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# 토큰 추정
#
# cl100k_base 실물 토크나이저는 BPE 파일 다운로드가 필요해 폐쇄망에서 못 쓴다.
# 대신 문자 클래스별 가중합으로 추정한다. 가중치 근거는 docs/TEST-PLAN.md의
# "T-01 토큰 추정 방법" 절에 기록했다. 추정이므로 ±20% 밴드를 함께 보고한다.
# ─────────────────────────────────────────────────────────────
HANGUL = re.compile(r"[가-힣]")
CJK = re.compile(r"[぀-ヿ一-鿿]")
ASCII_WORD = re.compile(r"[A-Za-z0-9_]+")

TOK_PER_HANGUL = 1.45
TOK_PER_CJK = 1.0
TOK_PER_ASCII_WORD = 1.3
TOK_PER_OTHER_CHAR = 0.45
ESTIMATE_BAND = 0.20


def estimate_tokens(text: str) -> int:
    hangul = len(HANGUL.findall(text))
    cjk = len(CJK.findall(text))
    words = ASCII_WORD.findall(text)
    ascii_chars = sum(len(w) for w in words)
    other = max(0, len(text) - hangul - cjk - ascii_chars)
    total = (
        hangul * TOK_PER_HANGUL
        + cjk * TOK_PER_CJK
        + len(words) * TOK_PER_ASCII_WORD
        + other * TOK_PER_OTHER_CHAR
    )
    return int(round(total))


# ─────────────────────────────────────────────────────────────
# frontmatter 파싱 (PyYAML 없이 동작하도록 최소 구현)
# ─────────────────────────────────────────────────────────────
def split_frontmatter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    head = raw[3:end].strip("\n")
    body = raw[end + 4 :].lstrip("\n")
    return parse_simple_yaml(head), body


def parse_simple_yaml(text: str) -> dict:
    out: dict = {}
    key = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and key and line.lstrip().startswith("- "):
            out.setdefault(key, [])
            if isinstance(out[key], list):
                out[key].append(_scalar(line.lstrip()[2:]))
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # source_anchor / assets 는 중첩 구조라 인라인 JSON으로 싣는다.
        # YAML flow 스타일이 곧 JSON이라 파서를 늘리지 않고 정확히 읽을 수 있다.
        if val.startswith("{") or val.startswith("[{"):
            try:
                out[key] = json.loads(val)
                continue
            except ValueError:
                pass
        out[key] = _list(val) if val.startswith("[") else (_scalar(val) if val else [])
    return out


def _scalar(v: str):
    v = v.strip().strip("'\"")
    return v


def _list(v: str) -> list:
    inner = v.strip()[1:-1].strip()
    if not inner:
        return []
    parts, buf, quote = [], "", None
    for ch in inner:
        if quote:
            if ch == quote:
                quote = None
            else:
                buf += ch
        elif ch in "'\"":
            quote = ch
        elif ch == ",":
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return [p for p in parts if p]


def as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    if ";" in s:
        return [p.strip() for p in s.split(";") if p.strip()]
    if "|" in s:
        return [p.strip() for p in s.split("|") if p.strip()]
    return [s]


# ─────────────────────────────────────────────────────────────
# 청크 모델
# ─────────────────────────────────────────────────────────────
REQUIRED_FIELDS = ["chunk_id", "title", "category", "tags", "retrieval_questions"]
RECOMMENDED_FIELDS = ["priority", "confidence", "freshness", "related_chunks", "audience"]

CODE_FENCE = re.compile(r"```")


@dataclass
class Chunk:
    path: str
    chunk_id: str
    title: str
    category: str
    meta: dict
    body: str
    tokens: int = 0
    shingles: set = field(default_factory=set, repr=False)

    @property
    def unbalanced_fence(self) -> bool:
        return len(CODE_FENCE.findall(self.body)) % 2 != 0


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"[^\w가-힣]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def shingles(text: str, n: int = 5) -> set:
    toks = normalize(text).split()
    if len(toks) < n:
        return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_chunks(root: Path) -> list[Chunk]:
    out = []
    for p in sorted(root.rglob("*.md")):
        raw = p.read_text(encoding="utf-8")
        meta, body = split_frontmatter(raw)
        cid = str(meta.get("chunk_id") or p.stem)
        out.append(
            Chunk(
                path=str(p),
                chunk_id=cid,
                title=str(meta.get("title") or ""),
                category=str(meta.get("category") or "(none)"),
                meta=meta,
                body=body,
                tokens=estimate_tokens(body),
                shingles=shingles(body),
            )
        )
    return out


# ─────────────────────────────────────────────────────────────
# 시험 항목
# ─────────────────────────────────────────────────────────────
def t01_size(chunks, lo=800, hi=1500):
    small = [(c.chunk_id, c.tokens) for c in chunks if c.tokens < lo]
    large = [(c.chunk_id, c.tokens) for c in chunks if c.tokens > hi]
    toks = sorted(c.tokens for c in chunks)
    n = len(toks) or 1
    return {
        "id": "T-01",
        "name": "청크 크기 분포",
        "target": f"{lo}~{hi} 토큰(추정)",
        "count": len(chunks),
        "min": toks[0] if toks else 0,
        "p50": toks[n // 2] if toks else 0,
        "p90": toks[int(n * 0.9) - 1] if toks else 0,
        "max": toks[-1] if toks else 0,
        "mean": round(sum(toks) / n, 1),
        "under": len(small),
        "over": len(large),
        "in_range_pct": round(100 * (n - len(small) - len(large)) / n, 1),
        "estimate_band_pct": int(ESTIMATE_BAND * 100),
        "under_samples": small[:10],
        "over_samples": large[:10],
        "verdict": "PASS" if (len(small) + len(large)) / n < 0.25 else "WARN",
    }


def t02_autonomy(chunks):
    """자율성: 선행 청크를 가리키는 지시 표현이 본문에 있으면 독립성 위반 소지."""
    pat = re.compile(r"(앞 문서|위에서 설명|이전 청크|앞서 언급|상기 내용|아래 표 참조|위 표)")
    hits = []
    for c in chunks:
        found = pat.findall(c.body)
        if found:
            hits.append({"chunk_id": c.chunk_id, "markers": sorted(set(found))})
    return {
        "id": "T-02",
        "name": "청크 자율성(문맥 의존 표현)",
        "flagged": len(hits),
        "total": len(chunks),
        "samples": hits[:15],
        "verdict": "PASS" if len(hits) / max(1, len(chunks)) < 0.10 else "WARN",
    }


def t03_metadata(chunks):
    missing_req = defaultdict(list)
    missing_rec = defaultdict(list)
    for c in chunks:
        for f in REQUIRED_FIELDS:
            if not as_list(c.meta.get(f)):
                missing_req[f].append(c.chunk_id)
        for f in RECOMMENDED_FIELDS:
            if not as_list(c.meta.get(f)):
                missing_rec[f].append(c.chunk_id)
    total_missing = sum(len(v) for v in missing_req.values())
    return {
        "id": "T-03",
        "name": "메타데이터 완전성",
        "required_fields": REQUIRED_FIELDS,
        "missing_required": {k: {"count": len(v), "samples": v[:5]} for k, v in missing_req.items()},
        "missing_recommended": {k: len(v) for k, v in missing_rec.items()},
        "verdict": "PASS" if total_missing == 0 else "FAIL",
    }


def t04_retrieval_questions(chunks):
    counts, empty, short = [], [], []
    for c in chunks:
        qs = as_list(c.meta.get("retrieval_questions"))
        counts.append(len(qs))
        if not qs:
            empty.append(c.chunk_id)
        for q in qs:
            if len(q) < 8:
                short.append((c.chunk_id, q))
    n = len(chunks) or 1
    return {
        "id": "T-04",
        "name": "retrieval_questions 커버리지",
        "mean_per_chunk": round(sum(counts) / n, 2),
        "chunks_without": len(empty),
        "without_samples": empty[:10],
        "too_short": short[:10],
        "verdict": "PASS" if not empty else "FAIL",
    }


def t05_related(chunks):
    ids = {c.chunk_id for c in chunks}
    dangling, selfref, isolated = [], [], []
    for c in chunks:
        rel = as_list(c.meta.get("related_chunks"))
        if not rel:
            isolated.append(c.chunk_id)
        for r in rel:
            if r == c.chunk_id:
                selfref.append(c.chunk_id)
            elif r not in ids:
                dangling.append((c.chunk_id, r))
    return {
        "id": "T-05",
        "name": "related_chunks 무결성",
        "dangling": len(dangling),
        "dangling_samples": dangling[:10],
        "self_reference": len(selfref),
        "isolated": len(isolated),
        "isolated_samples": isolated[:10],
        "verdict": "PASS" if not dangling and not selfref else "FAIL",
    }


def t06_duplication(chunks, threshold=0.45):
    pairs = []
    for i, a in enumerate(chunks):
        for b in chunks[i + 1 :]:
            j = jaccard(a.shingles, b.shingles)
            if j >= threshold:
                pairs.append({"a": a.chunk_id, "b": b.chunk_id, "jaccard": round(j, 3)})
    pairs.sort(key=lambda x: -x["jaccard"])
    return {
        "id": "T-06",
        "name": "청크 간 중복(5-gram Jaccard)",
        "threshold": threshold,
        "pairs_over_threshold": len(pairs),
        "samples": pairs[:15],
        "verdict": "PASS" if not pairs else "WARN",
    }


def t07_category_balance(chunks):
    counts = Counter(c.category for c in chunks)
    n = len(chunks) or 1
    top = counts.most_common(1)[0] if counts else ("", 0)
    share = top[1] / n
    return {
        "id": "T-07",
        "name": "카테고리 균형",
        "categories": len(counts),
        "distribution": dict(counts.most_common()),
        "largest": {"category": top[0], "count": top[1], "share_pct": round(share * 100, 1)},
        "singletons": [k for k, v in counts.items() if v == 1],
        "verdict": "PASS" if share <= 0.35 else "WARN",
    }


def t08_format(chunks):
    bad_fence = [c.chunk_id for c in chunks if c.unbalanced_fence]
    no_h1 = [c.chunk_id for c in chunks if not re.search(r"^#\s+", c.body, re.M)]
    no_summary = [
        c.chunk_id
        for c in chunks
        if not re.search(r"(한 줄 요약|## 요약|^>\s)", c.body, re.M)
    ]
    return {
        "id": "T-08",
        "name": "포맷 일관성",
        "unbalanced_code_fence": {"count": len(bad_fence), "samples": bad_fence[:10]},
        "missing_h1": {"count": len(no_h1), "samples": no_h1[:10]},
        "missing_summary_block": {"count": len(no_summary), "samples": no_summary[:10]},
        "verdict": "PASS" if not bad_fence and not no_h1 else "FAIL",
    }


def t13_assets(chunks: list[Chunk], repo_root: Path, assets_dir: Path):
    """에셋·원문 앵커 무결성.

    현재 청크는 전부 텍스트 소스 유래라 에셋이 0개다. 그래도 지금 넣어 두는 이유는,
    이미지 소스가 들어온 뒤에 검사를 붙이면 이미 깨진 참조가 섞인 상태에서 시작하기
    때문이다. 검사가 먼저 있어야 처음부터 깨끗하다.

    검사 항목은 kb/schema.md의 T-13 절과 일치한다.
    """
    broken, missing_meta, unscreened, bad_anchor = [], [], [], []
    referenced: set[str] = set()
    total_assets = 0

    for c in chunks:
        for a in c.meta.get("assets") or []:
            if not isinstance(a, dict):
                missing_meta.append({"chunk_id": c.chunk_id, "issue": "assets 항목이 객체가 아님"})
                continue
            total_assets += 1
            path = str(a.get("path") or "")
            if not path:
                missing_meta.append({"chunk_id": c.chunk_id, "issue": "path 누락"})
                continue
            referenced.add(path)
            if Path(path).is_absolute():
                broken.append({"chunk_id": c.chunk_id, "path": path, "issue": "절대경로"})
            elif not (repo_root / path).exists():
                broken.append({"chunk_id": c.chunk_id, "path": path, "issue": "파일 없음"})
            for f in ("caption", "description_by"):
                if not str(a.get(f) or "").strip():
                    missing_meta.append({"chunk_id": c.chunk_id, "path": path, "issue": f"{f} 누락"})
            if a.get("screened") is not True:
                unscreened.append({"chunk_id": c.chunk_id, "path": path})

        anchor = c.meta.get("source_anchor")
        if isinstance(anchor, dict) and anchor:
            f = str(anchor.get("file") or "")
            if not f:
                bad_anchor.append({"chunk_id": c.chunk_id, "issue": "file 누락"})
            elif Path(f).is_absolute():
                bad_anchor.append({"chunk_id": c.chunk_id, "file": f, "issue": "절대경로"})
            elif not (repo_root / f).exists():
                bad_anchor.append({"chunk_id": c.chunk_id, "file": f, "issue": "파일 없음"})

    orphans = []
    if assets_dir.is_dir():
        for p in sorted(assets_dir.rglob("*")):
            if not p.is_file() or p.name.lower() in ("readme.md", ".gitkeep"):
                continue
            rel = str(p.relative_to(repo_root))
            if rel not in referenced:
                orphans.append(rel)

    fail = bool(broken or missing_meta or unscreened or bad_anchor)
    return {
        "id": "T-13",
        "name": "에셋·원문 앵커 무결성",
        "assets_declared": total_assets,
        "broken_paths": {"count": len(broken), "samples": broken[:10]},
        "missing_metadata": {"count": len(missing_meta), "samples": missing_meta[:10]},
        "unscreened": {"count": len(unscreened), "samples": unscreened[:10]},
        "bad_source_anchor": {"count": len(bad_anchor), "samples": bad_anchor[:10]},
        "orphan_assets": {"count": len(orphans), "samples": orphans[:10]},
        "verdict": "FAIL" if fail else ("WARN" if orphans else "PASS"),
    }


def cross_set_overlap(a: list[Chunk], b: list[Chunk], threshold=0.30):
    matches = []
    for ca in a:
        best, score = None, 0.0
        for cb in b:
            j = jaccard(ca.shingles, cb.shingles)
            if j > score:
                best, score = cb, j
        if best and score >= threshold:
            matches.append({"a": ca.chunk_id, "b": best.chunk_id, "jaccard": round(score, 3)})
    covered = {m["a"] for m in matches}
    return {
        "id": "T-09",
        "name": "두 세트 간 주제 중복",
        "threshold": threshold,
        "set_a_size": len(a),
        "set_b_size": len(b),
        "a_covered_by_b": len(covered),
        "a_unique": [c.chunk_id for c in a if c.chunk_id not in covered],
        "matches": sorted(matches, key=lambda x: -x["jaccard"])[:25],
    }


def run(root: Path, compare: Path | None = None, repo_root: Path | None = None) -> dict:
    chunks = load_chunks(root)
    # 에셋 경로는 저장소 루트 기준 상대경로다. 기본값은 kb/chunks 의 두 단계 위.
    root_for_assets = repo_root or root.resolve().parent.parent
    if not chunks:
        raise SystemExit(f"청크를 찾지 못했습니다: {root}")
    results = [
        t01_size(chunks),
        t02_autonomy(chunks),
        t03_metadata(chunks),
        t04_retrieval_questions(chunks),
        t05_related(chunks),
        t06_duplication(chunks),
        t07_category_balance(chunks),
        t08_format(chunks),
        t13_assets(chunks, root_for_assets, root_for_assets / "kb" / "assets"),
    ]
    report = {
        "source": str(root),
        "chunk_count": len(chunks),
        "total_tokens_est": sum(c.tokens for c in chunks),
        "tests": results,
        "summary": Counter(r["verdict"] for r in results if "verdict" in r),
    }
    if compare:
        report["cross_set"] = cross_set_overlap(chunks, load_chunks(compare))
    report["summary"] = dict(report["summary"])
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="RAG 청크 세트 감사")
    ap.add_argument("root", type=Path)
    ap.add_argument("--compare", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    rep = run(a.root, a.compare, a.repo_root)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    if not a.quiet:
        print(f"[{rep['source']}] 청크 {rep['chunk_count']}개 / 추정 {rep['total_tokens_est']:,} 토큰")
        for t in rep["tests"]:
            print(f"  {t['id']} {t.get('verdict','-'):5s} {t['name']}")
        if "cross_set" in rep:
            cs = rep["cross_set"]
            print(f"  T-09 -     주제중복: A {cs['set_a_size']}개 중 {cs['a_covered_by_b']}개가 B에 존재")
    fails = [t for t in rep["tests"] if t.get("verdict") == "FAIL"]
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
