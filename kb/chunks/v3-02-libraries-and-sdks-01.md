---
chunk_id: "v3-02-libraries-and-sdks-01"
title: "관련 라이브러리 및 SDK — 정의"
category: "reference"
section_path: "05_mcp_catalog > 관련 라이브러리 및 SDK"
audience: ["개발자", "운영자"]
tags: ["development", "libraries", "mcp-sdk", "python", "sdk", "typescript"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["05_mcp_catalog/02-libraries-and-sdks.md"]
source_urls: ["https://code.claude.com/docs/en/agent-sdk/subagents", "https://code.claude.com/docs/en/mcp-quickstart", "https://github.com/modelcontextprotocol/servers", "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md"]
retrieval_questions: ["관련 라이브러리 및 SDK란 무엇인가?", "관련 라이브러리 및 SDK의 핵심 개념은?", "관련 라이브러리 및 SDK의 Claude Code 공식 플러그인은 무엇인가?", "관련 라이브러리 및 SDK의 Node.js / TypeScript 패키지는 무엇인가?", "관련 라이브러리 및 SDK의 Python 패키지는 무엇인가?"]
related_chunks: ["v3-02-libraries-and-sdks-02", "v3-mcp-sdk"]
supersedes: ["chunk.087", "chunk.088", "chunk.089", "chunk.090"]
---

# 관련 라이브러리 및 SDK (1/2)

> **범위**: 정의, MCP 공식 SDK, MCP 서버 개발 플러그인, Claude Code 확장 라이브러리 · **출처 문서**: `05_mcp_catalog/02-libraries-and-sdks.md`

## 정의

MCP 서버 개발 및 Claude Code 확장을 위한 공식 SDK와 커뮤니티 라이브러리 목록입니다. 각 SDK는 MCP 프로토콜을 구현하여 자체 서버를 구축할 수 있게 합니다.

## MCP 공식 SDK

| SDK | 언어 | GitHub 저장소 | 패키지 |
|-----|------|---------------|--------|
| TypeScript SDK | TypeScript | [modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) | `@modelcontextprotocol/sdk` |
| Python SDK | Python | [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | `mcp` (PyPI) |
| C# SDK | C# | [modelcontextprotocol/csharp-sdk](https://github.com/modelcontextprotocol/csharp-sdk) | NuGet |
| Go SDK | Go | [modelcontextprotocol/go-sdk](https://github.com/modelcontextprotocol/go-sdk) | Go module |
| Java SDK | Java | [modelcontextprotocol/java-sdk](https://github.com/modelcontextprotocol/java-sdk) | Maven |
| Kotlin SDK | Kotlin | [modelcontextprotocol/kotlin-sdk](https://github.com/modelcontextprotocol/kotlin-sdk) | Maven |
| Rust SDK | Rust | [modelcontextprotocol/rust-sdk](https://github.com/modelcontextprotocol/rust-sdk) | crates.io |

## MCP 서버 개발 플러그인

### Claude Code 공식 플러그인

```bash
# 마켓플레이스 추가
/plugin marketplace add anthropics/claude-plugins-official

# MCP 서버 개발 플러그인 설치
/plugin install mcp-server-dev@claude-plugins-official

# 세션에서 활성화
/reload-plugins

# MCP 서버 스캐폴딩
/mcp-server-dev:build-mcp-server
```

## Claude Code 확장 라이브러리

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
