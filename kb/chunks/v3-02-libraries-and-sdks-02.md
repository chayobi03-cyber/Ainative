---
chunk_id: "v3-02-libraries-and-sdks-02"
title: "관련 라이브러리 및 SDK — MCP 서버 구축 예시"
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
retrieval_questions: ["TypeScript SDK에 대해 알려줘", "Python SDK에 대해 알려줘", "서브에이전트 SDK 정의에 대해 알려줘", "관련 라이브러리 및 SDK에는 무엇이 있는가?"]
related_chunks: ["v3-02-libraries-and-sdks-01", "v3-mcp-sdk"]
supersedes: ["chunk.091", "chunk.092", "chunk.093"]
---

# 관련 라이브러리 및 SDK (2/2)

> **범위**: MCP 서버 구축 예시, Claude Code Agent SDK, 관련 리소스 · **출처 문서**: `05_mcp_catalog/02-libraries-and-sdks.md`

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
