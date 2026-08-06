---
chunk_id: chunk.069
source_file: 03_operations/03-observability.md
title: "관측성 및 유지보수"
section: "설정법"
section_id: setup
category: operations
tags: [observability, logging, monitoring, maintenance, debugging]
---

# 관측성 및 유지보수 - 설정법

### 1. 세션 로깅 (Stop 훅)

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

### 2. MCP 서버 상태 모니터링

```bash
# 서버 목록 및 상태
claude mcp list

# 세션 내에서
/mcp
```

### 3. 컨텍스트 사용량 확인

```bash
/context  # 토큰 사용량 분석
```

### 4. 도구 호출 로깅 (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date): tool used - $(jq -r '.tool_name')\" >> ~/claude-tools.log"
          }
        ]
      }
    ]
  }
}
```
