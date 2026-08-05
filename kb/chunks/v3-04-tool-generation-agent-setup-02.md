---
chunk_id: "v3-04-tool-generation-agent-setup-02"
title: "툴 생성 에이전트 설정법 — 운영 가이드"
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
retrieval_questions: ["툴 생성 에이전트 설정법 운영 시 주의점은?", "툴 생성 에이전트 설정법의 모범 사례는?", "툴 생성 에이전트 설정법에서 자주 발생하는 문제는?", "툴 생성 에이전트 설정법 트러블슈팅 방법은?"]
related_chunks: ["v3-04-tool-generation-agent-setup-01", "v3-mcp-sdk", "v3-03-agent-frameworks-and-gateways-01"]
supersedes: ["chunk.111", "chunk.112"]
---

# 툴 생성 에이전트 설정법 (2/2)

> **범위**: 운영 가이드, 예외 사례 · **출처 문서**: `02_setup/04-tool-generation-agent-setup.md`

## 운영 가이드

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

## 예외 사례

### MCPB 번들링 흔한 실수

manifest에서 command: "npx"를 쓰면 npm 레지스트리 네트워크 접근이 필요하고 Claude Desktop의 번들 Node.js를 쓰지 않아 MCPB 번들링의 목적을 무산시킵니다. 올바른 구현은 command: "node", args: ["${__dirname}/server/index.js"].

업로드 불가/네트워크 제약 환경에서는 특히 치명적이므로 생성 에이전트의 MCPB 템플릿에 이 규칙을 하드코딩해야 합니다.

### Spec Kit 공급망 주의

공식 Spec Kit 패키지는 GitHub 저장소에서 직접 배포되며, PyPI의 동명 패키지는 Spec Kit 팀이 유지하지 않으므로 설치하면 안 됩니다.

### stdout 오염

MCP stdio 서버에서 stdout에 비-JSON 출력(print/log)이 섞이면 JSON-RPC 파서가 깨집니다. 로깅은 반드시 stderr로 보내야 합니다. 이는 MCP Inspector 연결 실패의 가장 흔한 원인입니다.

### 복잡 스키마 호환성

$ref/anyOf가 포함된 복잡한 스키마는 일부 클라이언트가 취약합니다. Inspector로 실제 노출 스키마를 확인해야 합니다.
