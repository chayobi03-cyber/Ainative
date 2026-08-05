#!/usr/bin/env python3
"""v1(47청크) + v2.3(135청크) → v3.0 통합 청크 세트 빌더.

설계 결정과 근거는 docs/TEST-RESULTS.md와 docs/LESSONS-LEARNED.md에 기록했다.
핵심 변환 3가지:

1. 스키마 통일 — v1의 리치 메타데이터(retrieval_questions/priority/confidence/
   freshness/audience)를 정본 스키마로 삼고, v2.3 청크에 역채움한다.
2. v2.3 섹션 청크 병합 — v2.3은 문서 1개를 definition/setup/operations/exceptions/
   security/related/sources 7조각으로 쪼개 중앙값 298토큰(추정)까지 잘게 나뉘었다.
   같은 source_file의 조각을 목표 크기로 재병합한다.
3. 출처 문서 분리 — sources/imported/ 원문은 청크와 내용이 겹치므로 색인 대상에서
   제외하고 ingestion.yaml에 명시한다.

사용법:
    python3 tools/build_v3.py --v1 <dir> --v23-chunks <dir> --v23-manifest <jsonl> --out kb
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_audit import as_list, estimate_tokens, split_frontmatter  # noqa: E402

RAG_ID_STRIP = re.compile(r"^rag-|-\d+$")
FILLER = re.compile(r"해당\s*없음|N/?A\s*$", re.M)

TARGET_LO, TARGET_HI = 800, 1500
BUILD_FRESHNESS = "2026-08"
REVIEW_BY = "2026-11-05"  # 분기 재검토. 가격/사양 변동 항목은 별도 조기 만료.

# v1/v2.3의 잡다한 카테고리를 8개로 수렴시킨다.
CATEGORY_MAP = {
    "specification": "specification",
    "configuration": "reference",
    "reference": "reference",
    "best-practices": "best-practices",
    "development": "development",
    "developer-experience": "development",
    "context-engineering": "development",
    "testing": "quality",
    "quality": "quality",
    "evaluation": "quality",
    "observability": "operations",
    "operations": "operations",
    "roadmap": "operations",
    "cost-optimization": "cost",
    "cost": "cost",
    "security": "security",
    "governance": "governance",
    "deployment": "governance",
    "case-study": "governance",
    "architecture": "architecture",
    "concept": "concept",
    "setup": "reference",
    "mcp-catalog": "reference",
    "catalog": "reference",
    "exceptions": "operations",
}

AUDIENCE_BY_CATEGORY = {
    "specification": ["개발자"],
    "development": ["개발자"],
    "quality": ["개발자", "QA"],
    "security": ["보안담당자", "운영자"],
    "governance": ["운영자", "관리자"],
    "operations": ["운영자"],
    "cost": ["운영자", "관리자"],
    "architecture": ["개발자", "아키텍트"],
    "concept": ["개발자", "신규입사자"],
    "best-practices": ["개발자"],
    "reference": ["개발자", "운영자"],
}

# v2.3 섹션 id → 검색 질문 템플릿. 자동 생성분은 confidence를 낮춰 표시한다.
QUESTION_TEMPLATES = {
    "definition": ["{t}란 무엇인가?", "{t}의 핵심 개념은?"],
    "setup": ["{t}는 어떻게 설정하는가?", "{t} 초기 구성 절차는?"],
    "operations": ["{t} 운영 시 주의점은?", "{t}의 모범 사례는?"],
    "exceptions": ["{t}에서 자주 발생하는 문제는?", "{t} 트러블슈팅 방법은?"],
    "security": ["{t}의 보안 고려사항은?", "{t} 권한 설정은 어떻게 하는가?"],
}


def merge_undersized(buckets: list[list[dict]]) -> list[list[dict]]:
    """목표 하한에 못 미치는 버킷을 인접 버킷에 흡수시킨다.

    꼬리 하나만 처리하던 초기 구현은 중간에 생긴 작은 버킷을 놓쳤다(채움 청크를
    제거하면 앞쪽 버킷이 홀로 남는다). 인접 후보 중 합쳐도 상한을 넘지 않는 쪽을
    고르고, 둘 다 넘으면 더 작은 쪽에 붙인다. 조각 유실을 막기 위해 리스트를
    새로 만들어 반환한다(제자리 수정 + 음수 인덱스 조합이 앞선 버그의 원인이었다).
    """
    def size(b):
        return sum(s["tokens"] for s in b)

    work = [list(b) for b in buckets]
    changed = True
    while changed and len(work) > 1:
        changed = False
        for i, b in enumerate(work):
            if size(b) >= TARGET_LO // 2:
                continue
            prev_i, next_i = i - 1, i + 1
            cands = [j for j in (prev_i, next_i) if 0 <= j < len(work)]
            if not cands:
                continue
            fits = [j for j in cands if size(work[j]) + size(b) <= TARGET_HI]
            j = min(fits or cands, key=lambda k: size(work[k]))
            merged = (work[j] + b) if j < i else (b + work[j])
            lo, hi = min(i, j), max(i, j)
            work = work[:lo] + [merged] + work[hi + 1 :]
            changed = True
            break
    return work


def slug(s: str) -> str:
    s = re.sub(r"[^\w가-힣\s-]", "", s).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")[:48] or "chunk"


def yaml_list(items) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(json.dumps(str(i), ensure_ascii=False) for i in items) + "]"


def emit(meta: dict, body: str) -> str:
    order = [
        "chunk_id", "title", "category", "section_path", "audience", "use_cases",
        "tags", "priority", "confidence", "freshness", "review_by",
        "source_documents", "source_urls", "retrieval_questions",
        "related_chunks", "supersedes",
    ]
    lines = ["---"]
    for k in order:
        v = meta.get(k)
        if v is None or v == "" or v == []:
            if k in ("use_cases", "source_urls", "related_chunks", "supersedes"):
                continue
        if isinstance(v, list):
            lines.append(f"{k}: {yaml_list(v)}")
        else:
            lines.append(f"{k}: {json.dumps(str(v), ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.strip() + "\n"


# ─────────────────────────────────────────────────────────────
# v1 → v3
# ─────────────────────────────────────────────────────────────
def convert_v1(root: Path) -> list[dict]:
    out = []
    for p in sorted(root.glob("*.md")):
        meta, body = split_frontmatter(p.read_text(encoding="utf-8"))
        old_id = str(meta.get("chunk_id") or p.stem)
        topic = RAG_ID_STRIP.sub("", old_id)
        cat = CATEGORY_MAP.get(str(meta.get("category", "")).strip(), "reference")
        new = {
            "chunk_id": f"v3-{topic}",
            "title": meta.get("title") or topic,
            "category": cat,
            "section_path": meta.get("section_path") or cat,
            "audience": as_list(meta.get("audience")) or AUDIENCE_BY_CATEGORY.get(cat, ["개발자"]),
            "use_cases": as_list(meta.get("use_cases")),
            "tags": as_list(meta.get("tags")),
            "priority": meta.get("priority") or "medium",
            "confidence": meta.get("confidence") or "verified",
            "freshness": meta.get("freshness") or BUILD_FRESHNESS,
            "review_by": REVIEW_BY,
            "source_documents": as_list(meta.get("source_documents")),
            "source_urls": [],
            "retrieval_questions": as_list(meta.get("retrieval_questions")),
            "related_chunks": [
                "v3-" + RAG_ID_STRIP.sub("", r) for r in as_list(meta.get("related_chunks"))
            ],
            "supersedes": [old_id],
            "_body": body,
            "_origin": "v1",
        }
        out.append(new)
    return out


# ─────────────────────────────────────────────────────────────
# v2.3 → v3 (섹션 병합)
# ─────────────────────────────────────────────────────────────
def convert_v23(chunks_dir: Path, manifest_path: Path) -> list[dict]:
    man = {}
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                e = json.loads(line)
                man[e["chunk_id"]] = e

    groups: dict[str, list] = defaultdict(list)
    for p in sorted(chunks_dir.glob("*.md")):
        meta, body = split_frontmatter(p.read_text(encoding="utf-8"))
        cid = str(meta.get("chunk_id") or p.stem)
        src = str(meta.get("source_file") or "unknown")
        groups[src].append(
            {
                "cid": cid,
                "section": str(meta.get("section") or ""),
                "section_id": str(meta.get("section_id") or ""),
                "title": str(meta.get("title") or ""),
                "category": str(meta.get("category") or "concept"),
                "tags": as_list(meta.get("tags")),
                "body": body,
                "tokens": estimate_tokens(body),
                "urls": man.get(cid, {}).get("source_urls", []) or [],
            }
        )

    out = []
    for src, parts in sorted(groups.items()):
        # sources/related 섹션은 본문 가치가 낮아 URL만 흡수하고 본문에서 제외한다.
        urls, keep = [], []
        for s in parts:
            urls += s["urls"]
            if s["section_id"] in ("sources", "related-docs", "related_docs"):
                urls += re.findall(r"https?://[^\s\)\]]+", s["body"])
                continue
            # 7섹션 고정 템플릿이 내용 없는 섹션에도 청크를 강제 생성했다
            # (예: "트러블슈팅 - 설정법: 해당 없음"). 검색을 오염시키므로 버린다.
            if FILLER.search(s["body"]) and s["tokens"] < 120:
                continue
            keep.append(s)
        if not keep:
            continue

        doc_title = keep[0]["title"] or Path(src).stem
        cat = CATEGORY_MAP.get(keep[0]["category"], "concept")
        base = slug(Path(src).stem)

        # 목표 크기까지 순서대로 누적 병합
        buckets, cur, cur_tok = [], [], 0
        for s in keep:
            if cur and cur_tok + s["tokens"] > TARGET_HI:
                buckets.append(cur)
                cur, cur_tok = [], 0
            cur.append(s)
            cur_tok += s["tokens"]
        if cur:
            buckets.append(cur)
        buckets = merge_undersized(buckets)

        # 보존 불변식: 입력 조각은 정확히 한 번씩만 출력 버킷에 나타나야 한다.
        flat = [s["cid"] for b in buckets for s in b]
        assert sorted(flat) == sorted(s["cid"] for s in keep), (
            f"{src}: 병합 중 조각 유실/중복 — 입력 {len(keep)}개, 출력 {len(flat)}개"
        )

        for i, bucket in enumerate(buckets, 1):
            cid = f"v3-{base}" if len(buckets) == 1 else f"v3-{base}-{i:02d}"
            secs = [s["section"] or s["section_id"] for s in bucket]
            tags = sorted({t for s in bucket for t in s["tags"]})
            body_parts = [f"# {doc_title}" + (f" ({i}/{len(buckets)})" if len(buckets) > 1 else "")]
            body_parts.append(
                f"> **범위**: {', '.join(x for x in secs if x)} · **출처 문서**: `{src}`"
            )
            for s in bucket:
                b = re.sub(r"^#\s+.*\n", "", s["body"], count=1).strip()
                head = s["section"] or s["section_id"] or ""
                body_parts.append(f"## {head}\n\n{b}" if head else b)

            qs = []
            for s in bucket:
                for tpl in QUESTION_TEMPLATES.get(s["section_id"], []):
                    qs.append(tpl.format(t=doc_title))
            if not qs:
                # 템플릿에 없는 섹션(카탈로그류)은 실제 소제목에서 질문을 만든다.
                heads = [
                    h.strip()
                    for s in bucket
                    for h in re.findall(r"^#{2,4}\s+(.+)$", s["body"], re.M)
                ]
                qs = [f"{h}에 대해 알려줘" for h in heads[:3]]
                qs.append(f"{doc_title}에는 무엇이 있는가?")
            qs = list(dict.fromkeys(qs))[:5]

            out.append(
                {
                    "chunk_id": cid,
                    "title": doc_title + (f" — {secs[0]}" if len(buckets) > 1 and secs else ""),
                    "category": cat,
                    "section_path": f"{Path(src).parent.name} > {doc_title}",
                    "audience": AUDIENCE_BY_CATEGORY.get(cat, ["개발자"]),
                    "use_cases": [],
                    "tags": tags,
                    "priority": "medium",
                    # 자동 병합·자동 생성 질문이므로 사람 검토 전까지 낮춰 표시한다.
                    "confidence": "auto-merged",
                    "freshness": BUILD_FRESHNESS,
                    "review_by": REVIEW_BY,
                    "source_documents": [src],
                    "source_urls": sorted(set(urls))[:12],
                    "retrieval_questions": qs,
                    "related_chunks": [],
                    "supersedes": [s["cid"] for s in bucket],
                    "_body": "\n\n".join(body_parts),
                    "_origin": "v2.3",
                }
            )

    # 같은 원본에서 나온 청크끼리 연결
    by_src = defaultdict(list)
    for c in out:
        by_src[c["source_documents"][0]].append(c["chunk_id"])
    for c in out:
        sib = [x for x in by_src[c["source_documents"][0]] if x != c["chunk_id"]]
        c["related_chunks"] = sib[:6]
    return out


def load_authored(root: Path) -> list[dict]:
    """갭 분석으로 새로 집필한 청크. frontmatter를 그대로 신뢰하되 필수 필드만 보강한다."""
    out = []
    for p in sorted(root.glob("*.md")):
        meta, body = split_frontmatter(p.read_text(encoding="utf-8"))
        cat = CATEGORY_MAP.get(str(meta.get("category", "")).strip(), meta.get("category", "reference"))
        out.append(
            {
                "chunk_id": str(meta.get("chunk_id") or f"v3-{slug(p.stem)}"),
                "title": meta.get("title") or p.stem,
                "category": cat,
                "section_path": meta.get("section_path") or cat,
                "audience": as_list(meta.get("audience")) or AUDIENCE_BY_CATEGORY.get(cat, ["개발자"]),
                "use_cases": as_list(meta.get("use_cases")),
                "tags": as_list(meta.get("tags")),
                "priority": meta.get("priority") or "medium",
                "confidence": meta.get("confidence") or "draft",
                "freshness": meta.get("freshness") or BUILD_FRESHNESS,
                "review_by": meta.get("review_by") or REVIEW_BY,
                "source_documents": as_list(meta.get("source_documents")),
                "source_urls": as_list(meta.get("source_urls")),
                "retrieval_questions": as_list(meta.get("retrieval_questions")),
                "related_chunks": as_list(meta.get("related_chunks")),
                "supersedes": [],
                "_body": body,
                "_origin": "authored",
            }
        )
    return out


def link_across(chunks: list[dict]) -> None:
    """태그 교집합이 큰 청크끼리 상호 연결을 보강한다."""
    ids = {c["chunk_id"] for c in chunks}
    for c in chunks:
        c["related_chunks"] = [r for r in c["related_chunks"] if r in ids and r != c["chunk_id"]]
    tagmap = defaultdict(list)
    for c in chunks:
        for t in c["tags"]:
            tagmap[t.lower()].append(c["chunk_id"])
    for c in chunks:
        if len(c["related_chunks"]) >= 2:
            continue
        score = defaultdict(int)
        for t in c["tags"]:
            for other in tagmap[t.lower()]:
                if other != c["chunk_id"]:
                    score[other] += 1
        best = [k for k, _ in sorted(score.items(), key=lambda x: -x[1])[:3]]
        c["related_chunks"] = list(dict.fromkeys(c["related_chunks"] + best))[:6]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1", type=Path, required=True)
    ap.add_argument("--v23-chunks", type=Path, required=True)
    ap.add_argument("--v23-manifest", type=Path, required=True)
    ap.add_argument("--authored", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    chunks = convert_v1(a.v1) + convert_v23(a.v23_chunks, a.v23_manifest)
    if a.authored and a.authored.exists():
        chunks += load_authored(a.authored)
    link_across(chunks)

    cdir = a.out / "chunks"
    cdir.mkdir(parents=True, exist_ok=True)
    for f in cdir.glob("*.md"):
        f.unlink()

    manifest, embeddings = [], []
    for c in chunks:
        body = c.pop("_body")
        origin = c.pop("_origin")
        (cdir / f"{c['chunk_id']}.md").write_text(emit(c, body), encoding="utf-8")
        rec = {k: v for k, v in c.items()}
        rec["origin"] = origin
        rec["file_path"] = f"chunks/{c['chunk_id']}.md"
        rec["tokens_est"] = estimate_tokens(body)
        manifest.append(rec)
        embeddings.append(
            {
                "chunk_id": c["chunk_id"],
                "embedding_text": "\n".join(
                    [c["title"], " ".join(c["tags"]), " ".join(c["retrieval_questions"]), body]
                ),
                "metadata": {
                    k: c[k] for k in ("category", "tags", "priority", "audience", "confidence", "freshness")
                },
            }
        )

    (a.out / "manifest.jsonl").write_text(
        "\n".join(json.dumps(m, ensure_ascii=False) for m in manifest) + "\n", encoding="utf-8"
    )
    (a.out / "embeddings.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in embeddings) + "\n", encoding="utf-8"
    )
    print(f"v3.0 청크 {len(chunks)}개 생성 → {cdir}")
    print(f"  v1 유래 {sum(1 for m in manifest if m['origin']=='v1')}개 / "
          f"v2.3 유래 {sum(1 for m in manifest if m['origin']=='v2.3')}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
