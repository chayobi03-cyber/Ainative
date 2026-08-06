#!/usr/bin/env python3
"""OWNERS.yaml 담당자 지정 상태를 점검한다.

**빌드를 막지 않는다.** 인수인계 전에는 비어 있는 게 정상이고, 조직 형태에 따라
채우는 방식도 다르기 때문이다. 대신 게이트가 매번 무엇이 비었는지 알려준다.

`--require` 를 주면 미지정 시 exit 1 — 사내 CI에서 인수인계 완료 후 켜면 된다.

사용법:
    python3 tools/check_owners.py            # 경고만
    python3 tools/check_owners.py --require  # 미지정이면 실패
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

def yaml_scalar(raw: str) -> str:
    """YAML 스칼라 값 하나를 읽는다.

    `name: ""   # 예: 홍길동` 같은 줄에서, 따옴표 뒤 주석을 값으로 오인하면
    빈 항목이 기입된 것처럼 보인다(실제로 담당자 미기입을 놓쳤던 버그).
    따옴표가 있으면 닫는 따옴표까지만 값이고 나머지는 버린다.
    """
    raw = raw.strip()
    m = re.match(r"^([\"'])(.*?)\1", raw)
    if m:
        return m.group(2)
    return raw.split("#", 1)[0].strip()


# PyYAML 의존을 피한다(폐쇄망에서 설치가 막힐 수 있음). 필요한 깊이가 2단계뿐이라
# 최소 파서로 충분하다.
def parse_nested(text: str) -> dict:
    root: dict = {}
    stack = [(0, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        m = re.match(r"^\s*([A-Za-z_][\w\-]*)\s*:\s*(.*)$", raw)
        if not m:
            continue
        key, tail = m.group(1), m.group(2).strip()
        has_value = tail != "" and not tail.startswith("#")
        rawval = yaml_scalar(tail) if has_value else ""
        while stack and indent <= stack[-1][0] and len(stack) > 1:
            stack.pop()
        parent = stack[-1][1]
        # `key:`(값 자체가 없음)만 중첩 시작이다. `key: ""`는 **명시적 빈 스칼라**라서
        # 중첩으로 오인하면 미기입 항목을 놓친다.
        if not has_value or rawval == "|":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = rawval
    return root


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, default=Path("OWNERS.yaml"))
    ap.add_argument("--require", action="store_true", help="미지정 시 exit 1")
    a = ap.parse_args()

    if not a.file.exists():
        print(f"{a.file} 없음")
        return 1 if a.require else 0

    data = parse_nested(a.file.read_text(encoding="utf-8"))
    roles = data.get("roles", {}) or {}
    reviews = data.get("review_assignments", {}) or {}

    missing = []
    for role in ("kb_owner", "retrieval_owner"):
        r = roles.get(role) or {}
        if not (r.get("name") or "").strip():
            missing.append(f"roles.{role}.name")
    for k, v in reviews.items():
        if isinstance(v, str) and not v.strip():
            missing.append(f"review_assignments.{k}")

    if not missing:
        kb = (roles.get("kb_owner") or {}).get("name", "")
        rt = (roles.get("retrieval_owner") or {}).get("name", "")
        print(f"담당자 지정 완료 — KB: {kb} / 검색: {rt}")
        return 0

    print(f"담당자 미지정 {len(missing)}건 (인수인계 전이면 정상):")
    for m in missing:
        print(f"  - {m}")
    print("  → OWNERS.yaml 을 채우고 tools/make_calendar.py 로 일정을 등록하십시오.")
    return 1 if a.require else 0


if __name__ == "__main__":
    sys.exit(main())
