---
id: catalog.libraries-sdks
title: 관련 라이브러리 및 SDK
category: mcp-catalog
tags: [sdk, libraries, mcp-sdk, typescript, python, development]
source_urls:
  - https://github.com/modelcontextprotocol/servers
  - https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md
  - https://code.claude.com/docs/en/mcp-quickstart
last_reviewed: 2026-08-05
chunking_policy: whole-document
---

# 관련 라이브러리 및 SDK

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

## MCP 서버 구축 예시

### TypeScript SDK

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {}, resources: {} } }
);

// 도구 등록
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "my-tool",
      description: "Description of my tool",
      inputSchema: { type: "object", properties: {} }
    }
  ]
}));

// stdio 전송으로 실행
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Python SDK

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="my-tool",
            description="Description of my tool",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, InitializationOptions(
            server_name="my-server",
            server_version="1.0.0"
        ))
```

## Claude Code Agent SDK

| SDK | 언어 | 용도 |
|-----|------|------|
| [TypeScript SDK](https://code.claude.com/docs/en/agent-sdk/typescript) | TypeScript | Claude Code 에이전트 프로그래밍 제어 |
| [Python SDK](https://code.claude.com/docs/en/agent-sdk/python) | Python | Claude Code 에이전트 프로그래밍 제어 |

### 서브에이전트 SDK 정의

```python
# Python SDK에서 서브에이전트 정의
result = query(
    prompt="Analyze the codebase",
    agents=[{
        "name": "code-analyzer",
        "description": "Analyzes code patterns",
        "model": "sonnet"
    }],
    allowedTools=["Agent"]
)
```

## 관련 리소스

| 리소스 | URL |
|--------|-----|
| MCP 프로토콜 사양 | [modelcontextprotocol.io](https://modelcontextprotocol.io/) |
| MCP 서버 저장소 | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| Claude Code 공식 문서 | [code.claude.com/docs](https://code.claude.com/docs) |
| Anthropic Directory | [claude.ai/customize/connectors](https://claude.ai/customize/connectors) |
| MCP 서버 디렉토리 | [codehelper.me/tools/mcp-server-directory](https://codehelper.me/tools/mcp-server-directory/) |

## 출처

- [modelcontextprotocol/servers - GitHub](https://github.com/modelcontextprotocol/servers)
- [modelcontextprotocol/servers README - GitHub Raw](https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md)
- [Claude Code 공식 문서 - MCP 퀵스타트](https://code.claude.com/docs/en/mcp-quickstart)
- [Claude Code 공식 문서 - Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
