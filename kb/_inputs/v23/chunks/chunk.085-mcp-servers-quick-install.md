---
chunk_id: chunk.085
source_file: 05_mcp_catalog/01-open-source-mcp-servers.md
title: "오픈소스 MCP 서버 카탈로그"
section: "빠른 설치 명령"
section_id: quick-install
category: mcp-catalog
tags: [mcp-servers, open-source, catalog, reference-implementations, community]
---

# 오픈소스 MCP 서버 카탈로그 - 빠른 설치 명령

### 3개 필수 서버 설치

```bash
# Context7 - 라이브 문서
claude mcp add context7 -- npx -y @upstash/context7-mcp

# GitHub - 저장소 관리
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

# Playwright - 브라우저 자동화
claude mcp add playwright -- npx @playwright/mcp@latest
```

### 데이터베이스 서버 설치

```bash
# PostgreSQL
claude mcp add postgres --command "uvx mcp-server-postgres" --env "DATABASE_URL=postgres://..."

# Supabase (원격)
claude mcp add --transport http supabase https://mcp.supabase.com/mcp
```

### 개발 도구 서버 설치

```bash
# Sentry (에러 추적)
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# Notion (문서)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Filesystem (파일 접근)
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/files

# Sequential Thinking (문제 해결)
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```
