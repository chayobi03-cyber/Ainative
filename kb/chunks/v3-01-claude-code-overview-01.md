---
chunk_id: "v3-01-claude-code-overview-01"
title: "Claude Code 개요 — 정의"
category: "concept"
section_path: "01_concepts > Claude Code 개요"
audience: ["개발자", "신규입사자"]
tags: ["agent", "architecture", "claude-code", "overview"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/01-claude-code-overview.md"]
source_urls: ["https://code.claude.com/docs/en/mcp-quickstart", "https://news.creeta.com/en/claude-code-best-practices-2026/", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/"]
retrieval_questions: ["Claude Code 개요란 무엇인가?", "Claude Code 개요의 핵심 개념은?", "Claude Code 개요는 어떻게 설정하는가?", "Claude Code 개요 초기 구성 절차는?", "Claude Code 개요 운영 시 주의점은?"]
related_chunks: ["v3-01-claude-code-overview-02", "v3-claude-code-guide", "v3-cli-registration"]
supersedes: ["chunk.001", "chunk.002", "chunk.003"]
---

# Claude Code 개요 (1/2)

> **범위**: 정의, 설정법, 운영 가이드 · **출처 문서**: `01_concepts/01-claude-code-overview.md`

## 정의

Claude Code는 Anthropic이 제공하는 터미널 기반 AI 에이전트입니다. 파일 읽기, 셸 명령 실행, 웹 검색, API 호출을 수행하며, 사용자가 목표를 입력하면 에이전트가 도구를 선택하고 실행하는 `while True` 루프 구조로 동작합니다. IDE가 아닌 터미널에서 직접 코드베이스 전체에 접근할 수 있습니다.

Claude Code의 아키텍처는 5개 계층으로 구성됩니다:

| 계층 | 위치 | 용도 |
|------|------|------|
| CLAUDE.md | 프로젝트 루트 또는 `~/.claude/` | 영구 프로젝트 규칙, 아키텍처 결정, 코딩 표준 |
| MCP 서버 | `.mcp.json`, user/project/server 관리 | 외부 도구 연결: GitHub, DB, Sentry, Slack 등 |
| Skills | `.claude/skills/<name>/SKILL.md` | 재사용 가능한 워크플로우: 코드 리뷰, 배포 체크리스트 등 |
| Hooks | `settings.json` 또는 프로젝트 설정 | 이벤트 기반 자동화: 세션 시작, 도구 사용, 프롬프트 제출 등 |
| Subagents | `.claude/agents/` | 분리된 컨텍스트 창에서 연구, 리뷰, 디버깅 수행 |

## 설정법

### 설치 (2026년 네이티브 설치 권장)

**macOS / Linux / WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**npm을 통한 설치 (대체):**
```bash
npm install -g @anthropic-ai/claude-code
```

### 검증

```bash
claude --version
claude doctor
```

### 최소 구성 시작점

1. 짧은 `CLAUDE.md` 작성 (안정적인 규칙만 포함)
2. 하나의 MCP 서버 연결 (가장 큰 컨텍스트 스위칭을 해결하는 서버)
3. 하나의 결정론적 Hook 추가
4. 반복되는 워크플로우를 하나의 Skill로 이동
5. Subagent는 연구/리뷰 컨텍스트 분리가 필요할 때만 추가

## 운영 가이드

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
