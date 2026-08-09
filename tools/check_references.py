#!/usr/bin/env python3
"""청크 참조 무결성과 평가 커버리지 — T-20.

## 왜 이 검사가 업데이트 이식의 핵심인가

`chunk_id`는 저장소 곳곳에서 참조된다 — 정정 원장, 판정 원장, held-out qrels,
벤더 행렬, 문서의 인용. 지금 210여 곳이다. 그런데 청크는 **빌더 출력**이라
다음 버전에서 이름이 바뀌거나 사라질 수 있다.

    참조가 깨지면 조용히 깨진다. 정정이 적용 대상을 잃고, 판정이 사라진 청크를
    가리키고, 문서가 없는 것을 안내한다. 아무도 즉시 알아채지 못한다.

이 검사가 그걸 막는다. 그리고 **막기만 하지 않는다** — 빌더가 남기는
`supersedes`(구 ID → 신 ID) 매핑으로 **무엇을 무엇으로 바꿔야 하는지 알려준다.**
업데이트를 이식할 때 이 출력이 곧 마이그레이션 지시서다.

## 평가 커버리지도 함께 본다

`docs/TEST-RESULTS.md` §12.9에서 실제로 겪은 일 — 청크를 추가하고 평가 세트를
그대로 두면 점수가 내려간다. 새 청크는 방해물로만 집계되고 정답으로는 집계되지
않기 때문이다. 그래서 **커버리지 비율에 바닥을 둔다.** 코퍼스만 키우면 게이트가
막고, 평가 세트를 같이 키우면 통과한다.

사용법:
    python3 tools/check_references.py
    python3 tools/check_references.py --write-baseline   # 커버리지 기준선 갱신
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASELINE = REPO / "tests/baseline_coverage.json"

# 참조를 찾을 곳과 그 파일에서 chunk_id가 나타나는 형태.
# 새 참조처를 만들면 여기에 등록한다 — 등록하지 않으면 지켜지지 않는다.
SOURCES: dict[str, str] = {
    "kb/corrections.yaml": r'"(v3-[a-z0-9\-]+)"',
    "kb/vendors.yaml": r'`(v3-[a-z0-9\-]+)`',
    "kb/schema.md": r'`(v3-[a-z0-9\-]+)`',
    "tests/qrels_adjudicated.jsonl": r'"(v3-[a-z0-9\-]+)"',
    "tests/heldout_queries.jsonl": r'"(v3-[a-z0-9\-]+)"',
    "docs/TEST-RESULTS.md": r'`(v3-[a-z0-9\-]+)`',
    "docs/TEST-PLAN.md": r'`(v3-[a-z0-9\-]+)`',
    "docs/SYSTEM-DESIGN.md": r'`(v3-[a-z0-9\-]+)`',
    "docs/OPTIMIZATION-LOOP.md": r'`(v3-[a-z0-9\-]+)`',
    "docs/HANDOVER.md": r'`(v3-[a-z0-9\-]+)`',
    "docs/INTERNAL-FILL-INS.md": r'`(v3-[a-z0-9\-]+)`',
    "skills/ainative-kb/SKILL.md": r'`(v3-[a-z0-9\-]+)`',
}

EVAL_SETS = ("tests/qrels_auto.jsonl", "tests/qrels_adjudicated.jsonl",
             "tests/heldout_queries.jsonl")
# 커버리지가 기준선보다 이만큼 넘게 떨어지면 막는다.
COVERAGE_TOLERANCE = 0.02


def load_corpus(manifest: Path) -> tuple[set[str], dict[str, str]]:
    """현재 chunk_id 집합과 구 ID → 신 ID 매핑."""
    ids, supersedes = set(), {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        ids.add(row["chunk_id"])
        for old in row.get("supersedes") or []:
            supersedes[old] = row["chunk_id"]
    return ids, supersedes


def collect_refs(root: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for rel, pattern in SOURCES.items():
        path = root / rel
        if not path.exists():
            continue
        out[rel] = set(re.findall(pattern, path.read_text(encoding="utf-8")))
    return out


def gold_chunks(root: Path, only: tuple[str, ...] | None = None) -> set[str]:
    covered = set()
    for rel in (only or EVAL_SETS):
        path = root / rel
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if "qrel" in row:
                covered |= {c for c, g in (row["qrel"] or {}).items() if g > 0}
            elif row.get("expected_chunk_id"):
                covered.add(row["expected_chunk_id"])
    return covered


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=REPO / "kb/manifest.jsonl")
    ap.add_argument("--root", type=Path, default=REPO)
    ap.add_argument("--baseline", type=Path, default=BASELINE)
    ap.add_argument("--write-baseline", action="store_true")
    a = ap.parse_args()

    ids, supersedes = load_corpus(a.manifest)
    problems: list[str] = []
    migratable: list[str] = []

    # ── 1. 참조 무결성
    total = 0
    for rel, refs in collect_refs(a.root).items():
        total += len(refs)
        for ref in sorted(refs - ids):
            if ref in supersedes:
                migratable.append(f"{rel}: `{ref}` → `{supersedes[ref]}` (supersedes 매핑)")
            else:
                problems.append(f"{rel}: `{ref}`가 존재하지 않고 supersedes 매핑도 없습니다")

    # ── 2. 평가 커버리지
    held = gold_chunks(a.root, ("tests/heldout_queries.jsonl",))
    allsets = gold_chunks(a.root)
    cov = {
        "chunks": len(ids),
        "covered_any": len(allsets & ids),
        "covered_heldout": len(held & ids),
        "ratio_any": round(len(allsets & ids) / len(ids), 4) if ids else 0.0,
        "ratio_heldout": round(len(held & ids) / len(ids), 4) if ids else 0.0,
    }

    if a.write_baseline:
        a.baseline.write_text(
            json.dumps({**cov, "note":
                        "T-20 커버리지 기준선. 청크를 추가하면 평가 세트도 늘려야 "
                        "이 비율이 유지된다 — docs/TEST-RESULTS.md §12.9."},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"커버리지 기준선 기록: {a.baseline}")

    print(f"참조 {total}개 / 청크 {cov['chunks']}개")
    print(f"  평가 커버리지 — 전체 세트 {cov['ratio_any']:.0%}, "
          f"held-out {cov['ratio_heldout']:.0%}")
    uncovered = sorted(ids - held)
    if uncovered:
        print(f"  held-out 미커버 {len(uncovered)}개 (현실적 질의로 시험되지 않음): "
              f"{', '.join(uncovered[:4])}{' …' if len(uncovered) > 4 else ''}")

    if not a.write_baseline and a.baseline.exists():
        base = json.loads(a.baseline.read_text(encoding="utf-8"))
        for key in ("ratio_any", "ratio_heldout"):
            drop = base.get(key, 0.0) - cov[key]
            if drop > COVERAGE_TOLERANCE:
                problems.append(
                    f"평가 커버리지 {key}: {base[key]:.4f} → {cov[key]:.4f} "
                    f"(낙폭 {drop:.4f} > 허용 {COVERAGE_TOLERANCE}). "
                    f"청크를 늘렸으면 평가 세트도 늘리십시오 — 새 청크는 방해물로만 "
                    f"집계되고 정답으로는 집계되지 않습니다"
                )

    if migratable:
        print("\n이관 가능한 참조 — supersedes로 대상을 찾았습니다:")
        for m in migratable:
            print(f"  {m}")
        print("  위 대응대로 바꾸면 됩니다. 이것이 업데이트 이식의 마이그레이션 지시서입니다.")
        problems += [f"이관 필요: {m}" for m in migratable]

    if problems:
        print("\nT-20 실패:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print("  OK    참조 무결성 · 평가 커버리지")
    return 0


if __name__ == "__main__":
    sys.exit(main())
