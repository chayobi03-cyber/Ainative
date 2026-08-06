---
chunk_id: chunk.029
source_file: 01_concepts/05-claude-md-memory.md
title: "CLAUDE.md 메모리 시스템"
section: "정의"
section_id: definition
category: concept
tags: [claude-md, memory, project-rules, context, configuration]
---

# CLAUDE.md 메모리 시스템 - 정의

`CLAUDE.md`는 Claude Code 세션이 시작될 때 가장 먼저 읽는 파일로, 에이전트의 "운영체제" 역할을 합니다. 프로젝트 규칙, 아키텍처 결정, 코딩 표준, 메모리 라우팅을 포함하며, 항상 활성화되는(always-on) 컨텍스트를 제공합니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 위치 | 프로젝트 루트 또는 `~/.claude/` (사용자 글로벌) |
| 로딩 | 세션 시작 시 자동 로드 (항상 활성) |
| 역할 | 프로젝트 구조, 네이밍 컨벤션, 접근 불가 영역, 워크플로우 규칙 |
| 2026년 발전 | 5개 프리미티브(Rules, Skills, Subagents, Hooks, Output Styles)와 병행 |

### 2026년 3계층 지침 분할

`CLAUDE.md`를 가볍게 유지하고, 스코프별 지침은 분산 배치:

| 계층 | 위치 | 로딩 방식 | 용도 |
|------|------|-----------|------|
| CLAUDE.md | 프로젝트 루트 | 항상 로드 | 안정적인 전역 규칙 |
| Path-scoped Rules | `.claude/rules/*.md` | 매칭 파일 접근 시만 로드 | 특정 경로 규칙 |
| Skills | `.claude/skills/<name>/SKILL.md` | 온디맨드 | 반복되는 워크플로우 |
