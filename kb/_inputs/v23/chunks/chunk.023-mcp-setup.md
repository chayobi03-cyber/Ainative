---
chunk_id: chunk.023
source_file: 01_concepts/04-mcp.md
title: "MCP (Model Context Protocol)"
section: "설정법"
section_id: setup
category: concept
tags: [mcp, model-context-protocol, external-tools, mcp-servers, transport]
---

# MCP (Model Context Protocol) - 설정법

### 1. 원격 HTTP 서버 추가

```bash
# 기본 문법
claude mcp add --transport http <name> <url>

# 실제 예: Notion 연결
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Bearer 토큰과 함께
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"

# GitHub 연결 (원격)
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

### 2. 로컬 stdio 서버 추가

```bash
# Playwright (브라우저 자동화)
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Context7 (라이브러리 문서)
claude mcp add context7 -- npx -y @upstash/context7-mcp

# GitHub (stdio)
claude mcp add github -e GITHUB_TOKEN=ghp_xxx -- npx -y @modelcontextprotocol/server-github

# PostgreSQL
claude mcp add postgres --command "uvx mcp-server-postgres" --env "DATABASE_URL=postgres://..."

# Python 서버
claude mcp add my-server -- python3 -m my_mcp_server
```

### 3. 스코프 지정

```bash
# 로컬 스코프 (기본값)
claude mcp add --transport http stripe https://mcp.stripe.com

# 프로젝트 스코프 (팀 공유)
claude mcp add --scope project --transport http docs https://code.claude.com/docs/mcp

# 사용자 스코프 (모든 프로젝트)
claude mcp add --scope user --transport http docs https://code.claude.com/docs/mcp
```

### 4. .mcp.json 직접 편집

프로젝트 루트에 `.mcp.json` 파일 생성:

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
    }
  }
}
```

### 5. 서버 관리 명령

```bash
# 서버 목록 및 상태 확인
claude mcp list

# 특정 서버 정보 조회
claude mcp get <name>

# 서버 제거
claude mcp remove <name>

# 스코프 지정 제거
claude mcp remove <name> --scope local

# 프로젝트 승인 초기화
claude mcp reset-project-choices

# JSON 설정으로 직접 추가
claude mcp add-json '<json-string>'

# Claude Desktop에서 설정 가져오기 (macOS/WSL)
claude mcp add-from-claude-desktop

# Claude Code 자체를 MCP 서버로 실행
claude mcp serve
```

### 6. 연결 상태 확인

`claude mcp list` 출력 상태:

| 상태 | 의미 |
|------|------|
| `✔ Connected` | 사용 준비 완료 |
| `! Connected · tools fetch failed` | 연결됨, 도구 목록 조회 실패 |
| `! Needs authentication` | 인증 필요 (브라우저 로그인 또는 토큰) |
| `✘ Failed to connect` | 서버 응답 없음 |
| `✘ Connection error` | 연결 시도 중 에러 발생 |
| `⏸ Pending approval` | 프로젝트 스코프 서버 미승인 |

### 7. OAuth 인증이 필요한 서버

```bash
# Sentry 연결 (OAuth)
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 세션 내에서 인증
# /mcp 명령 실행 → 서버 선택 → Authenticate
```
