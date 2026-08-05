---
id: setup.hooks
title: Hooks 설정법
category: setup
tags: [hooks, setup, configuration, settings-json]
source_urls:
  - https://code.claude.com/docs/en/hooks-guide
  - https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/
  - https://www.morphllm.com/claude-code-hooks
last_reviewed: 2026-08-05
chunking_policy: whole-document
---

# Hooks 설정법

## 정의

Hooks 설정은 `.claude/settings.json`에 이벤트-매처-핸들러 구조의 JSON을 작성하여 Claude Code의 라이프사이클 이벤트에 자동화를 연결하는 과정입니다.

## 설정법

### 1. 설정 파일 위치

| 스코프 | 파일 경로 | 적용 범위 |
|--------|----------|-----------|
| 프로젝트 | `.claude/settings.json` | 이 프로젝트만, Git 커밋하여 팀 공유 |
| 사용자 | `~/.claude/settings.json` | 모든 프로젝트 |
| 엔터프라이즈 | 관리자 관리 | 조직 전체 |

### 2. 자동 포맷팅 (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
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

### 3. 위험 명령 차단 (PreToolUse)

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

### 4. 파일 보호 스크립트 연결

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### 5. 권한 설정

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

### 6. 핸들러 타입별 설정

| 타입 | 용도 | 예시 |
|------|------|------|
| `command` | 셸 명령 실행 | `"command": "npx prettier --write"` |
| `http` | HTTP 요청 | URL 및 헤더 지정 |
| `mcp_tool` | MCP 도구 호출 | 2026년 신기능 |
| `prompt` | 프롬프트 주입 | 컨텍스트에 지침 추가 |
| `agent` | 에이전트 실행 | 서브에이전트 호출 |

## 운영 가이드

- `$CLAUDE_PROJECT_DIR` 환경 변수로 경로 해석
- 매처는 정규식: `Edit|Write`, `mcp__.*`, `Bash` 등
- Exit 코드 0: 정상, 2: 차단, 기타: 에러 피드백
- 비동기 훅(`async: true`)은 결과 대기 없음
- 프로젝트 훅이 가장 일반적, Git에 커밋하여 팀 공유

## 예외 사례

- `settings.json` 문법 오류 시 해당 항목 스킵, `/hooks` 명령으로 경고 확인
- 매처 불일치 시 훅 실행 안 됨
- `.mcp.json` 변경 후 세션 재시작 필요

## 출처

- [Claude Code 공식 문서 - Hooks 가이드](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code Hooks Complete Guide — SmartScope Blog](https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/)
- [Claude Code Hooks (2026) — MorphLLM](https://www.morphllm.com/claude-code-hooks)
