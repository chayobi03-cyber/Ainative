#!/usr/bin/env python3
"""재검토 기한 강제 — T-16.

왜 필요한가
    `kb/ingestion.yaml`의 `review` 절과 각 청크의 `review_by`는 기한을 적어 두지만,
    **YAML은 알림을 보내지 않는다.** `make_calendar.py`가 .ics를 만들고 `ci/gate.sh`가
    임박을 출력하긴 했으나 어느 쪽도 아무것도 막지 않았다. 기한이 지난 청크는
    그대로 검색되고, 사람은 그것이 최신인 줄 안다.

    가격·사양처럼 빨리 변하는 항목은 틀린 채로 검색되는 것이 검색되지 않는 것보다
    나쁘다. 그래서 기한 초과에는 유예를 두되 결국 차단한다.

판정
    기한까지 WARN_DAYS 이상 남음   →  통과
    기한 임박 (WARN_DAYS 이내)     →  WARN  (차단 안 함)
    기한 초과, 유예 GRACE_DAYS 이내 →  WARN  (차단 안 함)
    유예까지 지남                  →  FAIL  (차단)

    유예를 두는 이유: 기한 당일에 CI가 멈추면 재검토가 아니라 기한을 미루는 커밋이
    나온다. 2주는 사람이 실제로 확인할 시간이고, 그 뒤에도 방치됐다면 그건 잊힌 것이다.

사용법:
    python3 tools/check_freshness.py
    python3 tools/check_freshness.py --today 2026-09-20     # 게이트 동작 확인용
    python3 tools/check_freshness.py --warn-days 30 --grace-days 14
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_calendar import parse_review  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
WARN_DAYS = 30
GRACE_DAYS = 14


def collect(ingestion: Path, manifest: Path) -> list[dict]:
    """기한이 붙은 항목을 전부 모은다 — ingestion의 review 절 + 청크별 review_by."""
    items = [
        {"kind": "review", "date": e["date"], "label": e["title"]}
        for e in parse_review(ingestion)
    ]
    if manifest.exists():
        by_date: Counter = Counter()
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("review_by"):
                by_date[row["review_by"]] += 1
        for d, n in sorted(by_date.items()):
            items.append({"kind": "chunk", "date": d, "label": f"청크 {n}개의 review_by"})
    return items


def classify(items: list[dict], today: date, warn_days: int, grace_days: int) -> list[dict]:
    out = []
    for it in items:
        try:
            due = date.fromisoformat(it["date"])
        except ValueError:
            out.append({**it, "left": None, "verdict": "FAIL",
                        "note": "날짜 형식이 YYYY-MM-DD가 아닙니다"})
            continue
        left = (due - today).days
        if left > warn_days:
            verdict, note = "OK", f"{left}일 남음"
        elif left >= 0:
            verdict, note = "WARN", f"{left}일 남음 — 재검토 착수할 것"
        elif left >= -grace_days:
            verdict, note = "WARN", f"{-left}일 초과 (유예 {grace_days}일 이내)"
        else:
            verdict, note = "FAIL", f"{-left}일 초과 — 유예 {grace_days}일을 넘겼습니다"
        out.append({**it, "left": left, "verdict": verdict, "note": note})
    return sorted(out, key=lambda x: x["date"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingestion", type=Path, default=REPO / "kb/ingestion.yaml")
    ap.add_argument("--manifest", type=Path, default=REPO / "kb/manifest.jsonl")
    ap.add_argument("--today", type=date.fromisoformat, default=None,
                    help="기준일 고정 (게이트가 실제로 발화하는지 확인할 때 쓴다)")
    ap.add_argument("--warn-days", type=int, default=WARN_DAYS)
    ap.add_argument("--grace-days", type=int, default=GRACE_DAYS)
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args()

    today = a.today or date.today()
    rows = classify(collect(a.ingestion, a.manifest), today, a.warn_days, a.grace_days)
    if not rows:
        print("기한 항목이 없습니다 — ingestion.yaml의 review 절을 확인하십시오.")
        return 1

    print(f"기준일 {today.isoformat()}  (경고 {a.warn_days}일 전, 유예 {a.grace_days}일)")
    for r in rows:
        print(f"  {r['verdict']:4s}  {r['date']}  {r['label']}  — {r['note']}")

    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(
            json.dumps({"today": today.isoformat(), "items": rows},
                       ensure_ascii=False, indent=2), encoding="utf-8")

    failed = [r for r in rows if r["verdict"] == "FAIL"]
    if failed:
        print("\nT-16 실패 — 재검토 기한을 넘긴 항목이 있습니다:", file=sys.stderr)
        for r in failed:
            print(f"  {r['date']}  {r['label']} — {r['note']}", file=sys.stderr)
        print("  내용을 재확인하고 kb/corrections.yaml에 기록한 뒤 기한을 갱신하십시오.\n"
              "  기한만 미루는 것은 확인한 것이 아닙니다.", file=sys.stderr)
        return 1
    warned = [r for r in rows if r["verdict"] == "WARN"]
    print(f"\nT-16 통과 — 초과 0건" + (f", 임박/유예 {len(warned)}건" if warned else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
