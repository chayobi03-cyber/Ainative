---
chunk_id: chunk.110
source_file: 02_setup/04-tool-generation-agent-setup.md
title: "툴 생성 에이전트 설정법"
section: "설정법"
section_id: setup
category: setup
tags: [tool-generation-agent, fastmcp, mcp-json, spec-first, pre-commit, mcp-eval]
---

# 툴 생성 에이전트 설정법 - 설정

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