#!/usr/bin/env python3
"""벤더 역량 행렬 검증 — T-19.

무엇을 강제하는가
    1. 모든 (기능 × 벤더) 셀에 `support`와 `verified`가 있다
    2. 값이 정해진 어휘 안에 있다
    3. `verified`가 `primary`나 `internal-test`가 아니면 `note`가 있다
    4. 선언된 벤더와 행렬의 벤더가 일치한다

왜 검사가 필요한가
    이 파일의 가치는 **`unknown`을 정직하게 남기는 것**이다. 그런데 빈칸을 두거나
    `support: yes`만 적고 근거를 안 적으면 다음 사람은 그게 확인된 줄 안다.
    한 벤더에서 확인한 절차를 다른 벤더에 그대로 적용하는 사고가 그렇게 난다.

    `unknown` 자체는 실패가 아니다. **근거 없는 `yes`가 실패다.**

사용법:
    python3 tools/check_vendor_matrix.py
    python3 tools/check_vendor_matrix.py --report   # unknown 현황 요약
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SUPPORT = {"yes", "partial", "no", "unknown"}
VERIFIED = {"primary", "secondary", "internal-test", "unknown"}


def needs_note(support: str | None, verified: str | None) -> str | None:
    """note를 요구할 셀인지, 요구한다면 왜인지.

    `unknown` + `unknown`은 요구하지 않는다 — "확인하지 않았다"가 그 자체로 완결된
    서술이고, 거기에 note를 강제하면 상투어만 늘어난다.
    **문제는 근거 없이 무언가를 주장하는 셀이다.**
    """
    if verified == "secondary":
        return "2차 출처다. 정확히 무엇이 미확인인지 적으십시오"
    if support == "partial":
        return "일부 지원이면 어느 부분이 되고 어느 부분이 안 되는지 적으십시오"
    if support in {"yes", "no"} and verified == "unknown":
        return f"확인하지 않았는데 support={support}로 단정했습니다. 근거를 적으십시오"
    return None


def parse(path: Path) -> tuple[list[str], list[dict]]:
    """벤더 목록과 기능별 행렬을 읽는다 (PyYAML 없이 최소 파싱).

    구조가 고정돼 있으므로 들여쓰기 깊이로 구분한다. 일반 YAML 파서가 아니다 —
    이 파일 형식이 바뀌면 여기도 같이 바꿔야 한다.
    """
    text = path.read_text(encoding="utf-8")

    vend_block = re.search(r"^vendors:\s*$(.*?)(?=^\S|\Z)", text, re.M | re.S)
    vendors = re.findall(r"^  ([a-z0-9-]+):\s*$", vend_block.group(1), re.M) if vend_block else []

    cap_block = re.search(r"^capabilities:\s*$(.*?)(?=^\S|\Z)", text, re.M | re.S)
    caps: list[dict] = []
    if cap_block:
        for chunk in re.split(r"\n  - id: ", cap_block.group(1))[1:]:
            cap_id = chunk.splitlines()[0].strip()
            matrix: dict[str, dict] = {}
            mblock = re.search(r"^    matrix:\s*$(.*)", chunk, re.M | re.S)
            if mblock:
                for cell in re.split(r"\n      (?=[a-z0-9-]+:)", mblock.group(1)):
                    m = re.match(r"\s*([a-z0-9-]+):", cell)
                    if not m:
                        continue
                    entry = {}
                    for key in ("support", "verified"):
                        v = re.search(rf"^\s+{key}:\s*(\S+)\s*$", cell, re.M)
                        if v:
                            entry[key] = v.group(1).strip().strip('"')
                    entry["note"] = bool(re.search(r"^\s+note:", cell, re.M))
                    matrix[m.group(1)] = entry
            caps.append({"id": cap_id, "matrix": matrix})
    return vendors, caps


def check(vendors: list[str], caps: list[dict]) -> list[str]:
    bad = []
    if not vendors:
        bad.append("vendors 절을 읽지 못했습니다")
    if not caps:
        bad.append("capabilities 절을 읽지 못했습니다")
    for cap in caps:
        missing = set(vendors) - set(cap["matrix"])
        if missing:
            bad.append(f"{cap['id']}: 벤더 누락 {sorted(missing)} — "
                       f"모르면 unknown으로 적으십시오. 빈칸은 확인된 것처럼 읽힙니다")
        extra = set(cap["matrix"]) - set(vendors)
        if extra:
            bad.append(f"{cap['id']}: 선언되지 않은 벤더 {sorted(extra)}")
        for vendor, cell in cap["matrix"].items():
            for key, allowed in (("support", SUPPORT), ("verified", VERIFIED)):
                val = cell.get(key)
                if val is None:
                    bad.append(f"{cap['id']}/{vendor}: `{key}`가 없습니다")
                elif val not in allowed:
                    bad.append(f"{cap['id']}/{vendor}: {key}={val!r}는 허용되지 않습니다 "
                               f"({sorted(allowed)})")
            why = needs_note(cell.get("support"), cell.get("verified"))
            if why and not cell["note"]:
                bad.append(f"{cap['id']}/{vendor}: {why}")
    return bad


def report(vendors: list[str], caps: list[dict]) -> None:
    total = unknown = secondary = 0
    per_vendor: dict[str, int] = {v: 0 for v in vendors}
    for cap in caps:
        for vendor, cell in cap["matrix"].items():
            total += 1
            if cell.get("verified") == "unknown":
                unknown += 1
                per_vendor[vendor] = per_vendor.get(vendor, 0) + 1
            elif cell.get("verified") == "secondary":
                secondary += 1
    print(f"셀 {total}개 — 미확인 {unknown}, 2차 출처 {secondary}, "
          f"확인됨 {total - unknown - secondary}")
    print("벤더별 미확인:")
    for v, n in sorted(per_vendor.items(), key=lambda kv: -kv[1]):
        print(f"  {v:14s} {n}")
    print("\n미확인이 많은 것 자체는 결함이 아닙니다. 근거 없이 지원한다고 적는 것이 결함입니다.")
    print("확인 우선순위는 kb/vendors.yaml의 next_verification 절에 있습니다.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, default=REPO / "kb/vendors.yaml")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    vendors, caps = parse(a.file)
    problems = check(vendors, caps)
    if a.report and not problems:
        report(vendors, caps)
        return 0
    if problems:
        print("T-19 벤더 행렬 실패:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print(f"  OK    벤더 행렬 — 벤더 {len(vendors)} × 기능 {len(caps)}, 모든 셀에 근거 표기")
    return 0


if __name__ == "__main__":
    sys.exit(main())
