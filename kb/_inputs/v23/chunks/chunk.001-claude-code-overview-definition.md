---
chunk_id: chunk.001
source_file: 01_concepts/01-claude-code-overview.md
title: "Claude Code 개요"
section: "정의"
section_id: definition
category: concept
tags: [claude-code, overview, architecture, agent]
---

# Claude Code 개요 - 정의

Claude Code는 Anthropic이 제공하는 터미널 기반 AI 에이전트입니다. 파일 읽기, 셸 명령 실행, 웹 검색, API 호출을 수행하며, 사용자가 목표를 입력하면 에이전트가 도구를 선택하고 실행하는 `while True` 루프 구조로 동작합니다. IDE가 아닌 터미널에서 직접 코드베이스 전체에 접근할 수 있습니다.

Claude Code의 아키텍처는 5개 계층으로 구성됩니다:

| 계층 | 위치 | 용도 |
|------|------|------|
| CLAUDE.md | 프로젝트 루트 또는 `~/.claude/` | 영구 프로젝트 규칙, 아키텍처 결정, 코딩 표준 |
| MCP 서버 | `.mcp.json`, user/project/server 관리 | 외부 도구 연결: GitHub, DB, Sentry, Slack 등 |
| Skills | `.claude/skills/<name>/SKILL.md` | 재사용 가능한 워크플로우: 코드 리뷰, 배포 체크리스트 등 |
| Hooks | `settings.json` 또는 프로젝트 설정 | 이벤트 기반 자동화: 세션 시작, 도구 사용, 프롬프트 제출 등 |
| Subagents | `.claude/agents/` | 분리된 컨텍스트 창에서 연구, 리뷰, 디버깅 수행 |
