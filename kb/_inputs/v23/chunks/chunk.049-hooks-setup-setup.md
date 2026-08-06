---
chunk_id: chunk.049
source_file: 02_setup/02-hooks-setup.md
title: "Hooks 설정법"
section: "설정법"
section_id: setup
category: setup
tags: [hooks, setup, configuration, settings-json]
---

# Hooks 설정법 - 설정법

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
