---
chunk_id: "v3-03-hooks-02"
title: "Hooks (훅) — 설정법"
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
retrieval_questions: ["Hooks (훅)는 어떻게 설정하는가?", "Hooks (훅) 초기 구성 절차는?", "Hooks (훅)의 프로젝트 설정 파일 생성은 무엇인가?", "Hooks (훅)의 자동 포맷팅 훅 (PostToolUse)은 무엇인가?", "Hooks (훅)의 위험 명령 차단 훅 (PreToolUse)은 무엇인가?"]
related_chunks: ["v3-03-hooks-01", "v3-03-hooks-03"]
supersedes: ["chunk.016"]
---

# Hooks (훅) (2/3)

> **범위**: 설정법 · **출처 문서**: `01_concepts/03-hooks.md`

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
