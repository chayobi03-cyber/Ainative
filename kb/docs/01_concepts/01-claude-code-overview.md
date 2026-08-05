---
id: concept.claude-code-overview
title: Claude Code 개요
category: concepts
tags: [claude-code, overview, architecture, agent]
source_urls:
  - https://code.claude.com/docs/en/mcp-quickstart
  - https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/
  - https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/
last_reviewed: 2026-08-05
chunking_policy: whole-document
---

# Claude Code 개요

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

## 예외 사례

### Claude Code가 아닌 것

- 챗봇이 아님 — 도구를 실행하는 에이전트
- 자동완성이 아님 — 전체 코드베이스에 접근하여 작업 수행
- IDE 플러그인이 아님 — 터미널에서 독립 실행

### Plan Mode (계획 모드)

복잡한 작업에서 실행 전 계획을 수립하는 모드:

| 작업 유형 | Plan Mode 권장 |
|-----------|---------------|
| 단순 버그 수정 (1-2 파일) | 선택적 |
| 3+ 파일에 걸친 기능 | 권장 |
| 리팩토링/아키텍처 변경 | 권장 |
| DB 마이그레이션 | 항상 권장 |
| 보안 관련 변경 | 항상 권장 |

진입 방법: `claude --plan`, `/plan` 슬래시 명령, 또는 `Shift + Tab`

## 보안 고려사항

- MCP 서버 추가 시 비밀키는 환경 변수로 관리, JSON에 평문 금지
- 프로젝트 스코프 서버는 저장소 클론 시 자동 실행되지 않음 — 승인 프롬프트 필요
- `permissions.deny` 배열을 통해 특정 도구/파일 접근 차단 가능
- Hooks를 통한 사전 커밋 검증으로 민감 파일 유출 방지

## 관련 문서

- [Skills (스킬)](./02-skills.md)
- [Hooks (훅)](./03-hooks.md)
- [MCP (Model Context Protocol)](./04-mcp.md)
- [CLAUDE.md 메모리 시스템](./05-claude-md-memory.md)
- [Subagents (서브에이전트)](./06-subagents.md)

## 출처

- [Claude Code 공식 문서 - MCP 퀵스타트](https://code.claude.com/docs/en/mcp-quickstart)
- [My Claude Code Setup After 4 Months of Daily Use (2026) — Daniil Okhlopkov](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)
- [Claude Code Documentation: 2026 Working Guide — Petronella Tech](https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/)
- [Claude Code Best Practices 2026 — Creeta News](https://news.creeta.com/en/claude-code-best-practices-2026/)
