---
chunk_id: chunk.054
source_file: 02_setup/03-mcp-setup.md
title: "MCP 설정법"
section: "설정법"
section_id: setup
category: setup
tags: [mcp, setup, configuration, mcp-servers, transport]
---

# MCP 설정법 - 설정법

### 1. HTTP 서버 추가 (원격)

```bash
# 기본 문법
claude mcp add --transport http <name> <url>

# 예: Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Bearer 토큰
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

### 2. stdio 서버 추가 (로컬)

```bash
# Playwright
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Context7
claude mcp add context7 -- npx -y @upstash/context7-mcp

# 환경 변수와 함께
claude mcp add github -e GITHUB_TOKEN=ghp_xxx -- npx -y @modelcontextprotocol/server-github

# Python 서버
claude mcp add my-server -- python3 -m my_mcp_server
```

### 3. SSE 서버 추가 (레거시)

```bash
claude mcp add my-remote -t sse -- https://mcp.example.com/sse

# 인증 헤더와 함께
claude mcp add secure-server -t sse -h "Authorization: Bearer token123" -- https://api.example.com/sse
```

### 4. 스코프 지정

```bash
# local (기본값)
claude mcp add --transport http stripe https://mcp.stripe.com

# project (.mcp.json에 저장, 팀 공유)
claude mcp add --scope project --transport http docs https://code.claude.com/docs/mcp

# user (모든 프로젝트)
claude mcp add --scope user --transport http docs https://code.claude.com/docs/mcp
```

### 5. .mcp.json 직접 작성

```json
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "postgres://..."
      },
      "timeout": 600000
    }
  }
}
```

### 6. 관리 명령

```bash
claude mcp list                    # 서버 목록 및 상태
claude mcp get <name>              # 특정 서버 정보
claude mcp remove <name>           # 서버 제거
claude mcp remove <name> --scope local  # 스코프 지정 제거
claude mcp reset-project-choices   # 프로젝트 승인 초기화
claude mcp add-json '<json>'       # JSON으로 직접 추가
claude mcp add-from-claude-desktop # Claude Desktop에서 가져오기
claude mcp serve                   # Claude Code를 MCP 서버로 실행
```
