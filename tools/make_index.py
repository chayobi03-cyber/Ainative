#!/usr/bin/env python3
"""에이전트가 벡터 DB 없이 KB를 훑을 수 있게 라우팅 색인을 만든다.

왜 필요한가
    이 KB는 벡터 DB에 적재되는 것을 전제로 만들어졌다. 그런데 실제 소비자는
    Claude Code / Gemini CLI이고, 2026년의 이들은 색인을 조회하는 대신 파일을
    직접 훑는다. `docs/RAG-AGENT-SPEC.md` §0이 이미 "이 저장소의 고유 자산을
    Claude Code Skill로 감싸라"고 적어 두었지만 그 표면이 없었다.

    벡터 DB가 준비되지 않은 팀, 폐쇄망, 또는 그냥 저장소를 clone한 에이전트가
    KB를 쓸 수 있어야 한다. 그 최소 조건은 **한 줄에 한 청크**로 grep이 걸리는
    라우팅 표면이다.

산출물 두 가지 — 둘 다 생성물이므로 직접 고치지 말 것
    kb/INDEX.md   사람과 에이전트가 함께 읽는다. 한 줄에 한 청크, grep 친화적.
    kb/llms.txt   llms.txt 관례를 따른 압축 색인. 제목 + 요약 + 섹션별 링크.

progressive disclosure의 2단계에 해당한다.
    1단계 discovery  skills/ainative-kb/SKILL.md 의 name/description
    2단계 activation 이 색인 — 어느 청크를 열지 고른다
    3단계 execution  kb/chunks/<id>.md 전문

사용법:
    python3 tools/make_index.py                       # kb/ 아래에 생성
    python3 tools/make_index.py --out /tmp/check      # 동기 확인용
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

GENERATED_WARNING = (
    "<!-- 생성물입니다. 직접 고치지 마십시오. "
    "`python3 tools/make_index.py`로 다시 만듭니다. 내용을 바꾸려면 "
    "kb/authored/ 또는 빌더를 고치고 재빌드하십시오. -->"
)

CATEGORY_ORDER = [
    "concept", "specification", "architecture", "development", "reference",
    "operations", "quality", "security", "governance", "cost", "best-practices",
]


def load(manifest: Path) -> list[dict]:
    return [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]


def by_category(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r.get("category") or "(none)"].append(r)
    ordered = [c for c in CATEGORY_ORDER if c in groups]
    ordered += sorted(c for c in groups if c not in CATEGORY_ORDER)
    return [(c, sorted(groups[c], key=lambda r: r["chunk_id"])) for c in ordered]


def render_index(rows: list[dict]) -> str:
    out = [
        "# Ainative 지식 베이스 색인",
        "",
        GENERATED_WARNING,
        "",
        f"청크 {len(rows)}개. 한 줄에 한 청크이므로 `grep`으로 바로 찾을 수 있습니다.",
        "",
        "```bash",
        "grep -i 'hook' kb/INDEX.md          # 주제로 찾기",
        "grep -i 'verified' kb/INDEX.md      # 검증된 것만",
        "```",
        "",
        "`confidence`가 `mixed` 또는 `draft`인 청크는 프로덕션 검색에서 제외됩니다",
        "(정본: `kb/ingestion.yaml`의 `retrieval.filters`). 사실 확인이 필요한 질문에는",
        "`verified`만 쓰십시오.",
        "",
    ]
    for category, group in by_category(rows):
        out.append(f"## {category} ({len(group)})")
        out.append("")
        for r in group:
            tags = ", ".join(r.get("tags") or [])
            q = (r.get("retrieval_questions") or [""])[0]
            out.append(
                f"- `{r['chunk_id']}` — {r['title']} "
                f"[{r.get('confidence', '?')}] "
                f"→ `{r['file_path']}`  \n"
                f"  태그: {tags}  \n"
                f"  예시 질문: {q}"
            )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_llms_txt(rows: list[dict]) -> str:
    out = [
        "# Ainative",
        "",
        "> 사내 AI 협업(Claude Code / Gemini CLI / MCP / Skills) 지식 베이스. "
        f"청크 {len(rows)}개를 주제별로 나눠 두었습니다. 각 링크는 저장소 안의 "
        "마크다운 파일이며 그 자체로 완결된 문서입니다.",
        "",
        "생성물입니다. `python3 tools/make_index.py`로 다시 만듭니다.",
        "",
        "확신도(`confidence`)가 `mixed`·`draft`인 항목은 검증되지 않은 벤더 주장이나 "
        "미기입 사내 정보를 담고 있으므로 사실 확인용으로 인용하지 마십시오.",
        "",
    ]
    for category, group in by_category(rows):
        out.append(f"## {category}")
        out.append("")
        for r in group:
            q = (r.get("retrieval_questions") or [""])[0]
            out.append(f"- [{r['title']}]({r['file_path']}): {q} ({r.get('confidence', '?')})")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=REPO / "kb/manifest.jsonl")
    ap.add_argument("--out", type=Path, default=REPO / "kb")
    a = ap.parse_args()

    rows = load(a.manifest)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "INDEX.md").write_text(render_index(rows), encoding="utf-8")
    (a.out / "llms.txt").write_text(render_llms_txt(rows), encoding="utf-8")
    print(f"청크 {len(rows)}개 → {a.out / 'INDEX.md'}, {a.out / 'llms.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
