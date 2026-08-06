---
chunk_id: chunk.059
source_file: 03_operations/01-security-governance.md
title: "보안 및 거버넌스"
section: "설정법"
section_id: setup
category: operations
tags: [security, governance, permissions, secrets, deny-list]
---

# 보안 및 거버넌스 - 설정법

### 1. 파일 접근 차단

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

### 2. 사전 커밋 보호 훅

```bash
# .claude/hooks/pre-commit.sh
if git diff --cached --name-only | grep -qE '\.(env|key|pem)$|creds\.md'; then
  echo "BLOCKED: Attempting to commit sensitive files"
  exit 1
fi
```

### 3. MCP 시크릿 관리

```json
// .mcp.json - 환경 변수 참조만, 평문 금지
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### 4. 에이전트 도구 권한 제한

```markdown
# .claude/agents/auditor.md
---
name: auditor
description: Read-only code audit agent
tools:
  - Read
  - Glob
  - Grep
---
```
