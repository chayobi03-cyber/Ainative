---
chunk_id: chunk.090
source_file: 05_mcp_catalog/02-libraries-and-sdks.md
title: "관련 라이브러리 및 SDK"
section: "Claude Code 확장 라이브러리"
section_id: extension-libraries
category: mcp-catalog
tags: [sdk, libraries, mcp-sdk, typescript, python, development]
---

# 관련 라이브러리 및 SDK - Claude Code 확장 라이브러리

### Node.js / TypeScript 패키지

| 패키지 | 용도 | 설치 명령 |
|--------|------|-----------|
| `@anthropic-ai/claude-code` | Claude Code CLI 본체 | `npm install -g @anthropic-ai/claude-code` |
| `@modelcontextprotocol/sdk` | MCP 서버 개발 (TypeScript) | `npm install @modelcontextprotocol/sdk` |
| `@playwright/mcp` | Playwright 브라우저 MCP 서버 | `npx @playwright/mcp@latest` |
| `@upstash/context7-mcp` | Context7 라이브 문서 MCP | `npx @upstash/context7-mcp` |
| `@modelcontextprotocol/server-filesystem` | 파일시스템 MCP 서버 | `npx @modelcontextprotocol/server-filesystem` |
| `@modelcontextprotocol/server-github` | GitHub MCP 서버 | `npx @modelcontextprotocol/server-github` |
| `@modelcontextprotocol/server-everything` | 참조/테스트 MCP 서버 | `npx @modelcontextprotocol/server-everything` |
| `@modelcontextprotocol/server-memory` | 메모리 그래프 MCP 서버 | `npx @modelcontextprotocol/server-memory` |
| `@modelcontextprotocol/server-sequential-thinking` | 순차 사고 MCP 서버 | `npx @modelcontextprotocol/server-sequential-thinking` |

### Python 패키지

| 패키지 | 용도 | 설치 명령 |
|--------|------|-----------|
| `mcp` | MCP Python SDK | `pip install mcp` |
| `mcp-server-fetch` | 웹 콘텐츠 가져오기 | `uvx mcp-server-fetch` |
| `mcp-server-git` | Git 저장소 MCP | `uvx mcp-server-git` |
| `mcp-server-time` | 시간/타임존 MCP | `uvx mcp-server-time` |
| `mcp-server-postgres` | PostgreSQL MCP | `uvx mcp-server-postgres` |

### 커뮤니티 MCP 서버 패키지

| 패키지 | 용도 | 소스 |
|--------|------|------|
| `@ahrefs/mcp-server` | Ahrefs SEO MCP | Ahrefs |
| `@masonator/coolify-mcp` | Coolify 배포 MCP | 커뮤니티 |
| `@anthropic/mcp-server-brave-search` | Brave 검색 MCP | Anthropic (아카이브) |
| `@anthropic/mcp-server-slack` | Slack MCP | Anthropic (아카이브) |
