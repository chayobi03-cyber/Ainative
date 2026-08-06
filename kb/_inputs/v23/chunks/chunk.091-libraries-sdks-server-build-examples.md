---
chunk_id: chunk.091
source_file: 05_mcp_catalog/02-libraries-and-sdks.md
title: "관련 라이브러리 및 SDK"
section: "MCP 서버 구축 예시"
section_id: server-build-examples
category: mcp-catalog
tags: [sdk, libraries, mcp-sdk, typescript, python, development]
---

# 관련 라이브러리 및 SDK - MCP 서버 구축 예시

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
