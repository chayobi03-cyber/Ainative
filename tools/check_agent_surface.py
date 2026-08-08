#!/usr/bin/env python3
"""에이전트 표면 검증 — T-17.

무엇을 검사하는가
    1. SKILL.md가 agentskills.io 공개 규격을 지키는가
       프론트매터가 byte 0에서 시작, 허용 키만 사용, `name`은 소문자+하이픈 ≤64자로
       부모 폴더명과 일치, `description`은 ≤1024자.
       규격을 어기면 로드되지 않으므로, 이 검사가 없으면 "왜 스킬이 안 뜨는지"를
       사람이 매번 다시 알아내야 한다.

    2. 생성된 라우팅 색인이 manifest와 동기인가
       `kb/INDEX.md`와 `kb/llms.txt`는 생성물이다. 청크를 재빌드하고 색인 재생성을
       잊으면 에이전트가 없는 청크로 안내한다. 재생성 결과와 바이트 단위로 비교한다.

    3. AGENTS.md가 가리키는 경로가 실재하는가
       지침이 없는 파일을 가리키면 에이전트가 조용히 다른 판단을 한다.

사용법:
    python3 tools/check_agent_surface.py
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_index import load, render_index, render_llms_txt  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# agentskills.io 규격: 이 키 외에는 검증 실패다.
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESC_MAX = 1024


def check_skill(path: Path) -> list[str]:
    bad = []
    raw = path.read_text(encoding="utf-8")
    # 조기 반환하지 않는다 — 한 번에 위반을 전부 보여줘야 고치는 쪽이 한 번에 끝낸다.
    if not raw.startswith("---"):
        bad.append(f"{path}: 프론트매터가 파일 첫 바이트에서 시작하지 않습니다")
    start = raw.find("---")
    if start == -1:
        return bad + [f"{path}: 프론트매터가 없습니다"]
    end = raw.find("\n---", start + 3)
    if end == -1:
        return bad + [f"{path}: 프론트매터가 닫히지 않았습니다"]
    block = raw[start + 3 : end]

    # 최소 파서 — 최상위 `키: 값`만 본다. 값이 여러 줄이면 다음 최상위 키까지 잇는다.
    fields: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key and line.strip():
            fields[key] += " " + line.strip()

    unknown = set(fields) - ALLOWED_KEYS
    if unknown:
        bad.append(f"{path}: 허용되지 않은 프론트매터 키 {sorted(unknown)} "
                   f"(허용: {sorted(ALLOWED_KEYS)})")
    for required in ("name", "description"):
        if not fields.get(required):
            bad.append(f"{path}: 필수 키 `{required}`가 없거나 비어 있습니다")

    name = fields.get("name", "")
    if name:
        if len(name) > NAME_MAX:
            bad.append(f"{path}: name이 {len(name)}자로 상한 {NAME_MAX}자를 넘습니다")
        if not NAME_RE.match(name):
            bad.append(f"{path}: name '{name}'은 소문자·숫자·하이픈만 쓸 수 있고 "
                       f"하이픈으로 시작하거나 끝날 수 없습니다")
        if name != path.parent.name:
            bad.append(f"{path}: name '{name}'이 부모 폴더명 '{path.parent.name}'과 "
                       f"다릅니다 — 이러면 스킬이 로드되지 않습니다")

    desc = fields.get("description", "")
    if len(desc) > DESC_MAX:
        bad.append(f"{path}: description이 {len(desc)}자로 상한 {DESC_MAX}자를 넘습니다")
    return bad


def check_index_sync(manifest: Path, kb: Path) -> list[str]:
    rows = load(manifest)
    expected = {"INDEX.md": render_index(rows), "llms.txt": render_llms_txt(rows)}
    bad = []
    for name, want in expected.items():
        path = kb / name
        if not path.exists():
            bad.append(f"{path}: 없습니다 — `python3 tools/make_index.py`로 생성하십시오")
            continue
        if path.read_text(encoding="utf-8") != want:
            bad.append(f"{path}: manifest와 동기가 아닙니다 — "
                       f"`python3 tools/make_index.py`로 다시 만드십시오")
    return bad


def check_agents_md(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: 없습니다"]
    text = path.read_text(encoding="utf-8")
    bad = []
    # 백틱으로 감싼 저장소 경로만 본다. 명령줄·와일드카드는 대상이 아니다.
    for ref in sorted(set(re.findall(r"`([a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]+)`", text))):
        if ref.endswith("/**") or "*" in ref:
            ref = ref.split("*")[0].rstrip("/")
        if not ref or ref.startswith("-"):
            continue
        if not (REPO / ref).exists():
            bad.append(f"{path}: 존재하지 않는 경로를 가리킵니다 — {ref}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", type=Path, default=REPO / "skills")
    ap.add_argument("--manifest", type=Path, default=REPO / "kb/manifest.jsonl")
    ap.add_argument("--kb", type=Path, default=REPO / "kb")
    ap.add_argument("--agents", type=Path, default=REPO / "AGENTS.md")
    a = ap.parse_args()

    problems: list[str] = []

    skills = sorted(a.skills.glob("*/SKILL.md"))
    if not skills:
        problems.append(f"{a.skills}: SKILL.md를 찾지 못했습니다")
    for s in skills:
        found = check_skill(s)
        problems += found
        print(("  OK    " if not found else "  FAIL  ") + f"SKILL.md 규격  {s.parent.name}")

    for label, found in (("라우팅 색인 동기", check_index_sync(a.manifest, a.kb)),
                         ("AGENTS.md 경로", check_agents_md(a.agents))):
        problems += found
        print(("  OK    " if not found else "  FAIL  ") + label)

    if problems:
        print("\nT-17 에이전트 표면 실패:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
