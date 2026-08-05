---
chunk_id: "v3-03-hooks-01"
title: "Hooks (훅) — 정의"
category: "concept"
section_path: "01_concepts > Hooks (훅)"
audience: ["개발자", "신규입사자"]
tags: ["automation", "guardrails", "hooks", "posttooluse", "pretooluse", "settings-json"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/03-hooks.md"]
source_urls: ["https://code.claude.com/docs/en/hooks", "https://code.claude.com/docs/en/hooks-guide", "https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/", "https://www.heyuan110.com/posts/ai/2026-02-28-claude-code-hooks-guide/", "https://www.morphllm.com/claude-code-hooks"]
retrieval_questions: ["Hooks (훅)란 무엇인가?", "Hooks (훅)의 핵심 개념은?"]
related_chunks: ["v3-03-hooks-02", "v3-03-hooks-03"]
supersedes: ["chunk.015"]
---

# Hooks (훅) (1/3)

> **범위**: 정의 · **출처 문서**: `01_concepts/03-hooks.md`

## 정의

Hooks는 Claude Code의 특정 이벤트가 발생할 때 자동으로 실행되는 셸 명령(또는 HTTP/MCP 도구 호출)입니다. 에이전트 코드를 수정하지 않고도 결정론적 검사, 로깅, 알림, 안전 규칙을 구현할 수 있습니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 설정 위치 | `.claude/settings.json` (프로젝트), `~/.claude/settings.json` (사용자) |
| 구조 | 3단계 중첩: 이벤트 → 매처 그룹 → 핸들러 |
| 핸들러 타입 | `command` (셸), `http` (HTTP 호출), `mcp_tool` (MCP 도구), `prompt` (프롬프트), `agent` (에이전트) |
| 병렬 실행 | 동일 이벤트의 매칭된 모든 훅은 병렬 실행 |
| 자동 중복 제거 | 동일한 훅 명령은 자동으로 중복 제거 |

### 이벤트 라이프사이클 (2026년 기준)

이벤트는 3가지 케이던스로 분류됩니다:

**세션당 1회:**

| 이벤트 | 발생 시점 |
|--------|----------|
| `SessionStart` | 세션 시작 또는 재개 |
| `SessionEnd` | 세션 종료 |
| `Setup` | `--init-only`, `--init`, 또는 `-p` 모드의 `--maintenance` 실행 시 |

**턴당 1회:**

| 이벤트 | 발생 시점 |
|--------|----------|
| `UserPromptSubmit` | 프롬프트 제출 시 (Claude 처리 전) |
| `UserPromptExpansion` | 사용자 명령이 프롬프트로 확장될 때 (차단 가능) |
| `Stop` | Claude가 작업을 완료했을 때 |
| `StopFailure` | Claude가 정지에 실패했을 때 |
| `PreCompact` | 컨텍스트 압축 전 |
| `PostCompact` | 컨텍스트 압축 후 |
| `TaskCreated` | 새 작업 생성 시 |
| `TaskCompleted` | 작업 완료 시 |
| `SubagentStop` | 서브에이전트 완료 시 |
| `SubagentStart` | 서브에이전트 시작 시 |
| `TeammateIdle` | 팀메이트 유휴 상태 시 |

**도구 호출당:**

| 이벤트 | 발생 시점 | 매처 필드 |
|--------|----------|-----------|
| `PreToolUse` | 도구 실행 전 (차단 가능) | 도구 이름 |
| `PostToolUse` | 도구 호출 성공 후 | 도구 이름 |
| `PostToolUseFailure` | 도구 호출 실패 후 | 도구 이름 |
| `PostToolBatch` | 병렬 도구 배치 완료 후 | 없음 |
| `PermissionRequest` | 권한 다이얼로그 표시 시 | 도구 이름 |
| `PermissionDenied` | 자동 모드 분류기가 도구 호출 거부 시 | 도구 이름 |

**독립 비동기 이벤트:**

| 이벤트 | 발생 시점 |
|--------|----------|
| `Notification` | Claude가 알림을 보낼 때 |
| `ConfigChange` | 설정 파일이 세션 중 변경될 때 |
| `CwdChanged` | 작업 디렉토리 변경 시 (예: `cd` 명령) |
| `FileChanged` | 감시 중인 파일이 디스크에서 변경될 때 |
| `InstructionsLoaded` | CLAUDE.md 또는 `.claude/rules/*.md` 로드 시 |
| `WorktreeCreate` | 워크트리 생성 시 |
| `WorktreeRemove` | 워크트리 제거 시 |
| `Elicitation` | MCP 도구 실행 내 추가 입력 요청 시 |
| `ElicitationResult` | 입력 요청 결과 |
