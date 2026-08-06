---
chunk_id: chunk.016
source_file: 01_concepts/03-hooks.md
title: "Hooks (훅)"
section: "설정법"
section_id: setup
category: concept
tags: [hooks, automation, settings-json, pretooluse, posttooluse, guardrails]
---

# Hooks (훅) - 설정법

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
