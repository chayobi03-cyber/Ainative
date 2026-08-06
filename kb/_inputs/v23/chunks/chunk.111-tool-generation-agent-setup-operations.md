---
chunk_id: chunk.111
source_file: 02_setup/04-tool-generation-agent-setup.md
title: "툴 생성 에이전트 설정법"
section: "운영 가이드"
section_id: operations
category: setup
tags: [tool-generation-agent, fastmcp, mcp-json, spec-first, pre-commit, mcp-eval]
---

# 툴 생성 에이전트 설정법 - 운영 가이드

### mcp-eval 테스트 케이스 예제

```python
from mcp_eval import Expect, task

@task("search_customers finds a known customer")
async def test_search(agent, session):
    response = await agent.generate_str(
        "Find the customer with email jane@acme.corp and summarize their status."
    )
    await session.assert_that(Expect.tools.was_called("search_customers"))
    await session.assert_that(
        Expect.tools.was_called_with("search_customers", {"query": "jane@acme.corp"})
    )
    await session.assert_that(Expect.content.contains("acme", case_sensitive=False), response=response)
    await session.assert_that(Expect.performance.response_time_under(5000))
    await session.assert_that(
        Expect.path.efficiency(expected_tool_sequence=["search_customers"],
                               allow_extra_steps=1,
                               tool_usage_limits={"search_customers": 1})
    )
```

### CI 회귀 게이트 (GitHub Actions)

```yaml
name: MCP Server Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: uv sync --dev
      - run: uv run pytest -m "not integration" -q      # deterministic 유닛(매 커밋)
      - run: uv run pytest tests/test_schema.py -v        # 스키마 validation(계약 드리프트)
      - run: npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server
      - run: uv run mcp-eval run --golden tests/golden/ --min-pass 0.9  # eval 골든셋 게이트
```

### pre-commit 설정 (생성 코드 자동 검증)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks: [{id: ruff, args: [--fix]}, {id: ruff-format}]
  - repo: local
    hooks:
      - id: mcp-schema-check
        name: MCP tool schema validation
        entry: uv run python -m tools.check_schema
        language: system
        pass_filenames: false
```

### MCP 서버 로컬 개발 규칙 (생성 에이전트 하드 규칙)

1. stdout에는 JSON-RPC만. 모든 로그·print는 stderr
2. 가능한 한 stateless. 상태가 필요하면 명시적으로 문서화
3. 툴 응답은 25,000 토큰 이내. 초과 시 truncate + 안내 메시지
4. 에러는 "다음에 무엇을 하라"를 포함한 문장으로. raw traceback 금지
5. 환경변수는 ${VAR} 확장으로만. 시크릿 하드코딩 금지
6. 산출물에 반드시 포함: server 코드 / .mcp.json / gemini settings / mcpb manifest / mcp-eval 골든셋 / Inspector 스모크 / README(doctor 포함)