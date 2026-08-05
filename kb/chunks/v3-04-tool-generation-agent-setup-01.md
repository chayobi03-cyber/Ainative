---
chunk_id: "v3-04-tool-generation-agent-setup-01"
title: "툴 생성 에이전트 설정법 — 정의"
category: "reference"
section_path: "02_setup > 툴 생성 에이전트 설정법"
audience: ["개발자", "운영자"]
tags: ["fastmcp", "mcp-eval", "mcp-json", "pre-commit", "spec-first", "tool-generation-agent"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["02_setup/04-tool-generation-agent-setup.md"]
source_urls: ["https://code.claude.com/docs/en/mcp", "https://docs.mcp-agent.com", "https://github.com/github/spec-kit", "https://github.com/jlowin/fastmcp", "https://github.com/modelcontextprotocol/inspector", "https://www.anthropic.com/engineering/writing-tools-for-agents"]
retrieval_questions: ["툴 생성 에이전트 설정법란 무엇인가?", "툴 생성 에이전트 설정법의 핵심 개념은?", "MCP 서버 최소 예제 (FastMCP, Python)에 대해 알려줘", ".mcp.json (Claude Code 프로젝트 스코프)에 대해 알려줘", "툴 생성 에이전트 설정법의 Gemini CLI settings.json은 무엇인가?"]
related_chunks: ["v3-04-tool-generation-agent-setup-02", "v3-mcp-sdk", "v3-03-agent-frameworks-and-gateways-01"]
supersedes: ["chunk.109", "chunk.110"]
---

# 툴 생성 에이전트 설정법 (1/2)

> **범위**: 정의, 설정법 · **출처 문서**: `02_setup/04-tool-generation-agent-setup.md`

## 정의

툴 생성 에이전트의 설정법은 MCP 서버 코드, 설정 파일, 테스트 케이스, 검증 스크립트를 한 번에 생성·구성하는 방법을 다룹니다. 생성 에이전트는 항상 3가지 배포 형태(Claude Code .mcp.json, Gemini CLI settings.json, MCPB 번들)를 함께 산출해야 하며, mcp-eval 골든셋과 Inspector 스모크 스크립트를 포함해야 합니다.

설계 규칙: 툴 소수·고레버리지, 네임스페이싱(crm_search_customers), response_format enum, 25k 토큰 제한, helpful error, 명확한 파라미터명(user_id 등).

## 설정법

### MCP 서버 최소 예제 (FastMCP, Python)

```python
from fastmcp import FastMCP
mcp = FastMCP("internal-crm")

@mcp.tool
def search_customers(query: str, response_format: str = "concise", limit: int = 50) -> dict:
    \"\"\"Search internal CRM customers by name or email.
    Use this when the user wants to find a customer or needs customer context.
    Prefer many small targeted searches over one broad search.\"\"\"
    return {"results": [...], "truncated": False}

if __name__ == "__main__":
    mcp.run()  # 로컬은 stdio; 원격은 mcp.run(transport="streamable-http")
```

### .mcp.json (Claude Code 프로젝트 스코프)

```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "${CRM_TOKEN}" }
    }
  }
}
```

### Gemini CLI settings.json

```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "$CRM_TOKEN" },
      "includeTools": ["search_customers"]
    }
  }
}
```

### SKILL.md 예제

```markdown
---
name: crm-report-writer
description: Generate weekly CRM retention reports. Use when the user asks for a retention report or churn summary.
allowed-tools: ["internal-crm__search_customers"]
---
# CRM Retention Report
## Steps
1. search_customers로 대상 세그먼트 조회 (concise 모드)
2. references/report_template.md 형식에 맞춰 작성
3. 수치는 반드시 툴 출력에 근거. 추정 금지.
```

### Spec-first 워크플로우 (GitHub Spec Kit)

```bash
uv tool install specify-cli
specify init mcp-gen-agent --integration claude
# /speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
```
