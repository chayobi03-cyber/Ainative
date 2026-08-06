---
chunk_id: chunk.008
source_file: 01_concepts/02-skills.md
title: "Skills (스킬)"
section: "정의"
section_id: definition
category: concept
tags: [skills, skill-md, slash-command, workflow, on-demand]
---

# Skills (스킬) - 정의

Skill은 Claude Code가 **때때로 필요한 지식과 절차**를 온디맨드로 로드할 수 있게 하는 마크다운 파일입니다. `SKILL.md` 파일에 작성된 지침을 Claude가 관련 상황에서 자동으로 로드하거나, `/skill-name` 슬래시 명령으로 직접 호출할 수 있습니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 형식 | `.claude/skills/<name>/SKILL.md` 디렉토리 구조 |
| 로딩 방식 | 온디맨드 (관련 상황에서 자동 로드 또는 직접 호출) |
| 컨텍스트 비용 | 호출 시에만 로드되므로 CLAUDE.md를 가볍게 유지 |
| 슬래시 명령 | 디렉토리 이름이 자동으로 `/<skill-name>` 명령 생성 |
| 플러그인 번들 | `.claude-plugin/plugin.json` 추가 시 에이전트, 훅, MCP 서버 번들 가능 |

### Skills vs CLAUDE.md vs Subagents

| 질문 | 배치 위치 |
|------|-----------|
| 모든 세션에 필요한가? | CLAUDE.md |
| 때때로 필요한 지식인가? | Skills |
| 메인 컨텍스트를 채울 무거운 작업인가? | Subagents |
| 서브에이전트에 도메인 지식이 필요한가? | Subagents + Skills (`skills` 필드로 연결) |
