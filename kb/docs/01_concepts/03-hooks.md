---
id: concept.hooks
title: Hooks (훅)
category: concepts
tags: [hooks, automation, settings-json, pretooluse, posttooluse, guardrails]
source_urls:
  - https://code.claude.com/docs/en/hooks-guide
  - https://code.claude.com/docs/en/hooks
  - https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/
  - https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/
last_reviewed: 2026-08-05
chunking_policy: section-based
---

# Hooks (훅)

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

## 설정법

### 1. 프로젝트 설정 파일 생성

`.claude/settings.json` 파일을 생성하거나 편집:

### 2. 자동 포맷팅 훅 (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

### 3. 위험 명령 차단 훅 (PreToolUse)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|DROP TABLE' && exit 2 || exit 0"
          }
        ]
      }
    ]
  }
}
```

### 4. 민감 파일 보호 훅

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

`protect-files.sh` 스크립트 예:
```bash
#!/bin/bash
# .claude/hooks/protect-files.sh
if git diff --cached --name-only | grep -qE '\.(env|key|pem)$|creds\.md'; then
  echo "BLOCKED: Attempting to commit sensitive files"
  exit 1
fi
```

### 5. 세션 종료 로깅 (Stop)

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date): session completed\" >> ~/claude-work.log",
            "async": true
          }
        ]
      }
    ]
  }
}
```

### 6. 알림 훅 (Notification)

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### 7. MCP 도구 호출 훅 (2026년 신기능)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__.*",
        "hooks": [
          {
            "type": "mcp_tool",
            "command": "log-mcp-usage"
          }
        ]
      }
    ]
  }
}
```

### 설정 스코프

| 스코프 | 파일 경로 | 적용 범위 |
|--------|----------|-----------|
| 프로젝트 | `.claude/settings.json` (저장소 내) | 이 프로젝트만 — Git 커밋하여 팀 공유 |
| 사용자 | `~/.claude/settings.json` | 모든 프로젝트 |
| 엔터프라이즈 | 관리자가 관리 | 조직 내 모든 사용자 |

## 운영 가이드

### Hook 핸들러 필드

| 필드 | 설명 |
|------|------|
| `type` | `command`, `http`, `mcp_tool`, `prompt`, `agent` 중 하나 |
| `command` | `type: "command"`일 때 실행할 셸 명령 |
| `timeout` | 타임아웃 (초 단위, 기본값: 30) |
| `async` | `true` 시 비동기 실행 (결과 대기 안 함) |

### 매처 패턴

매처는 도구 이름을 정규식으로 매칭:

| 매처 패턴 | 매칭 도구 |
|-----------|-----------|
| `Bash` | Bash 도구만 |
| `Edit\|Write` | Edit 또는 Write 도구 |
| `mcp__.*` | 모든 MCP 도구 |
| (빈 문자열) | 모든 도구 |

### Exit 코드 동작

| Exit 코드 | 의미 |
|-----------|------|
| `0` | 정상 완료, 계속 진행 |
| `2` | PreToolUse에서 도구 실행 차단 |
| 기타 0이 아닌 값 | 에러, Claude에게 피드백 전달 |

### 무인 운영을 위한 필수 훅

- **사전 커밋 보호**: 민감 파일(`.env`, `.key`, `.pem`) 커밋 차단
- **위험 명령 차단**: `rm -rf`, `DROP TABLE` 등 실행 전 차단
- **자동 포맷팅**: 편집 후 Prettier/ESLint 자동 실행
- **세션 로깅**: 작업 완료 시 로그 파일에 기록

## 예외 사례

### 훅이 실행되지 않는 경우

- `settings.json` 문법 오류 시 해당 항목 스킵 (경고는 `/hooks` 명령으로 확인)
- 매처 패턴이 도구 이름과 불일치 시 실행 안 됨
- 비동기 훅(`async: true`)은 결과를 기다리지 않으므로 실패해도 세션 계속

### .mcp.json 변경 사항이 반영되지 않는 경우

- Claude Code는 세션 시작 시 `.mcp.json`을 읽으므로, 파일 편집 후 세션 재시작 필요
- 이전에 서버를 거부한 경우: `claude mcp reset-project-choices` 실행

### 권한 충돌

- `permissions.deny` 배열과 PreToolUse 훅이 모두 설정된 경우, deny가 우선 적용
- PermissionDenied 이벤트에서 `{retry: true}` 반환 시 모델이 재시도 가능

### 2026년 "MCP Hooks" 오해

"MCP hooks"라는 용어가 검색되지만, MCP 서버와 Claude Code Hooks는 별개의 계층입니다:
- MCP 서버: 외부 도구와 데이터를 노출
- Claude Code Hooks: 이벤트 주변에서 결정론적 명령 실행

## 보안 고여사항

- 훅 스크립트는 `$CLAUDE_PROJECT_DIR` 환경 변수를 사용하여 경로 해석
- 훅 명령에 사용자 입력이 포함될 수 있으므로 인젝션 방지 필요
- `permissions.deny` 배열로 파일 접근 차단:
  ```json
  {
    "permissions": {
      "deny": [
        "Read(./.env)",
        "Read(./.env.*)",
        "Read(./secrets/**)",
        "Bash(cat ./.env *)"
      ]
    }
  }
  ```
- 무인 운영 시 사전 커밋 훅 필수 — 민감 파일 유출 방지

## 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [Skills (스킬)](./02-skills.md)
- [MCP (Model Context Protocol)](./04-mcp.md)
- [Hooks 설정법 (상세)](../02_setup/02-hooks-setup.md)
- [보안 및 거버넌스](../03_operations/01-security-governance.md)

## 출처

- [Claude Code 공식 문서 - Hooks 가이드](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code 공식 문서 - Hooks 레퍼런스](https://code.claude.com/docs/en/hooks)
- [My Claude Code Setup After 4 Months of Daily Use (2026)](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)
- [Claude Code Hooks Complete Guide — SmartScope Blog](https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/)
- [Claude Code Hooks: PreToolUse, PostToolUse — Heyuan110](https://www.heyuan110.com/posts/ai/2026-02-28-claude-code-hooks-guide/)
- [Claude Code Hooks Complete Guide — Hidekazu Konishi](https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html)
- [Claude Code Hooks (2026) — MorphLLM](https://www.morphllm.com/claude-code-hooks)


---

## 신규 관련 문서 (2026-08-05 보강)

- [툴 생성 에이전트](./07-tool-generation-agent.md) — Hooks를 "프롬프트로 부탁"에서 "쉘로 강제"로 바꾸는 장치로 다룸. PostToolUse/PreToolUse/SessionStart 실전 패턴 포함
- [컨텍스트 엔지니어링](./08-context-engineering.md) — SessionStart hook으로 사내 정책·컨벤션 자동 주입 패턴
- [품질 평가 및 CI](../03_operations/04-quality-evaluation-ci.md) — PostToolUse hook과 pre-commit 결합으로 이중 게이트 구성
- [배포·채택·거버넌스](../03_operations/06-deployment-adoption-governance.md) — PreToolUse hook으로 위험 명령·보호 경로 차단, managed hooks 거버넌스
