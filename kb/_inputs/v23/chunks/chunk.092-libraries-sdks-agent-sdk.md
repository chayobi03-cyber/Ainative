---
chunk_id: chunk.092
source_file: 05_mcp_catalog/02-libraries-and-sdks.md
title: "관련 라이브러리 및 SDK"
section: "Claude Code Agent SDK"
section_id: agent-sdk
category: mcp-catalog
tags: [sdk, libraries, mcp-sdk, typescript, python, development]
---

# 관련 라이브러리 및 SDK - Claude Code Agent SDK

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
