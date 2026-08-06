---
chunk_id: chunk.003
source_file: 01_concepts/01-claude-code-overview.md
title: "Claude Code 개요"
section: "운영 가이드"
section_id: operations
category: concept
tags: [claude-code, overview, architecture, agent]
---

# Claude Code 개요 - 운영 가이드

### 일상 워크플로우

- 프로젝트 디렉토리에서 `claude` 명령으로 세션 시작
- `CLAUDE.md`는 에이전트가 시작할 때 가장 먼저 읽는 파일 — 에이전트의 "운영체제" 역할
- 긴 세션에서는 `/compact`를 사용하여 컨텍스트 압축
- 작업 경계에서 컴팩션 수행 시 내구성 있는 규칙은 `CLAUDE.md`에 유지

### 결정 트리: 어느 계층에 무엇을 넣을까

| 조건 | 배치 위치 |
|------|-----------|
| 모든 세션에 적용되어야 하는 규칙 | CLAUDE.md |
| 때때로 필요한 지식/절차 | Skills (.claude/skills/) |
| 자동으로 실행되어야 하는 스크립트 | Hooks (settings.json) |
| 메인 컨텍스트를 오염시킬 무거운 작업 | Subagents (.claude/agents/) |
