#!/usr/bin/env python3
"""게이트 자기시험 — 차단 검사가 실제로 발화하는지 확인한다 (T-18).

왜 필요한가
    `docs/LESSONS-LEARNED.md` §9: **한 번도 발화한 적 없는 검사는 작동을 보장하지
    않는다.** T-13에만 이 원칙이 적용돼 있었다(`tests/fixtures/t13_broken/`).
    나머지 차단 검사 T-03/04/05/08은 지금까지 통과하는 입력만 봤으므로, 리팩터링이나
    파서 변경으로 조용히 무력화돼도 아무도 모른다.

무엇을 확인하는가
    픽스처마다 **정확히 어느 게이트가 FAIL이어야 하는지**를 적어두고 대조한다.
    "하나라도 FAIL이면 통과"로 만들면 엉뚱한 검사가 대신 발화해도 넘어간다 —
    그러면 무엇이 잡았는지 모르는 채로 안심하게 된다.

    T-04 픽스처가 T-03도 함께 발화하는 것은 결함이 아니라 실제 동작이다.
    `retrieval_questions: []`는 "질문 없음"이면서 동시에 "필수 필드 비어 있음"이다.
    숨기지 않고 기대값에 적어 두면, 그 동작이 바뀔 때 이 시험이 알려준다.

사용법:
    python3 tools/check_gate_selftest.py
    python3 tools/check_gate_selftest.py --fixtures tests/fixtures
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# 픽스처 → 반드시 FAIL이어야 하는 게이트 집합 (정확히 일치해야 한다)
EXPECTED: dict[str, set[str]] = {
    "t13_broken": {"T-13"},
    "gate_mutations/missing_required": {"T-03"},
    "gate_mutations/no_questions": {"T-03", "T-04"},
    "gate_mutations/dangling_ref": {"T-05"},
    "gate_mutations/bad_fence": {"T-08"},
}


def run_audit(chunks: Path, repo_root: Path) -> tuple[int, dict]:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        out = Path(tf.name)
    try:
        proc = subprocess.run(
            [sys.executable, "tools/kb_audit.py", str(chunks),
             "--repo-root", str(repo_root), "--json", str(out), "--quiet"],
            cwd=repo_root, capture_output=True, text=True,
        )
        report = json.loads(out.read_text(encoding="utf-8")) if out.stat().st_size else {}
        return proc.returncode, report
    finally:
        out.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", type=Path, default=Path("tests/fixtures"))
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    a = ap.parse_args()

    repo_root = a.repo_root.resolve()
    problems: list[str] = []

    for name, expected in EXPECTED.items():
        chunks = (a.fixtures / name / "chunks").resolve()
        if not chunks.is_dir():
            problems.append(f"{name}: 픽스처가 없습니다 ({chunks})")
            continue
        code, report = run_audit(chunks, repo_root)
        fired = {t["id"] for t in report.get("tests", []) if t.get("verdict") == "FAIL"}
        found: list[str] = []
        if code == 0:
            found.append(f"{name}: 감사가 통과했습니다 — 결함 픽스처인데 아무것도 잡지 못했습니다")
        if fired != expected:
            found.append(
                f"{name}: FAIL 게이트가 기대와 다릅니다 — "
                f"기대 {sorted(expected)}, 실제 {sorted(fired)}"
            )
        problems += found
        if not found:
            print(f"  OK  {name}  →  FAIL {sorted(fired)}")

    if problems:
        print("\n게이트 자기시험 실패:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print(f"\n차단 게이트 {len(EXPECTED)}종이 모두 의도한 결함에서 발화했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
