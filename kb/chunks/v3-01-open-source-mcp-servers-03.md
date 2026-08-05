---
chunk_id: "v3-01-open-source-mcp-servers-03"
title: "오픈소스 MCP 서버 카탈로그 — MCP 서버 디렉토리 및 검색"
category: "reference"
section_path: "05_mcp_catalog > 오픈소스 MCP 서버 카탈로그"
audience: ["개발자", "운영자"]
tags: ["catalog", "community", "mcp-servers", "open-source", "reference-implementations"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["05_mcp_catalog/01-open-source-mcp-servers.md"]
source_urls: ["https://deepwiki.com/modelcontextprotocol/servers/2-reference-servers-overview", "https://github.com/modelcontextprotocol/servers", "https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/", "https://mcpplaygroundonline.com/blog/awesome-mcp-servers", "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md", "https://techsy.io/en/blog/best-mcp-servers-claude-code", "https://www.totalum.app/blog/best-mcp-for-claude-code-2026"]
retrieval_questions: ["3개 필수 서버 설치에 대해 알려줘", "데이터베이스 서버 설치에 대해 알려줘", "개발 도구 서버 설치에 대해 알려줘", "오픈소스 MCP 서버 카탈로그에는 무엇이 있는가?"]
related_chunks: ["v3-01-open-source-mcp-servers-01", "v3-01-open-source-mcp-servers-02"]
supersedes: ["chunk.084", "chunk.085"]
---

# 오픈소스 MCP 서버 카탈로그 (3/3)

> **범위**: MCP 서버 디렉토리 및 검색, 빠른 설치 명령 · **출처 문서**: `05_mcp_catalog/01-open-source-mcp-servers.md`

## MCP 서버 디렉토리 및 검색

| 디렉토리 | URL | 특징 |
|-----------|-----|------|
| MCP Registry | [GitHub: modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 공식 참조 구현체 |
| Awesome MCP Servers | [mcpservers.org](https://mcpservers.org/) | 커뮤니티 서버 컬렉션 |
| MCP Server Directory | [codehelper.me](https://codehelper.me/tools/mcp-server-directory/) | 검색 가능 디렉토리 (2206+ 서버) |
| MCP Server Finder | [mcpserverfinder.com](https://www.mcpserverfinder.com/servers) | 포괄적 카탈로그 |
| MCP Market | [mcpmarket.com](https://mcpmarket.com/) | 일일 갱신 신규 서버 목록 |
| Model Context Protocol Directory | [model-context-protocol.com](https://model-context-protocol.com/) | MCP 서버/클라이언트 디렉토리 |

## 빠른 설치 명령

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
