---
chunk_id: "v3-mcp-eval"
title: "mcp-eval / mcp-agent: MCP 서버 평가 프레임워크"
category: "quality"
section_path: "품질 검증 > mcp-eval"
audience: ["개발자", "QA"]
use_cases: ["MCP 서버 eval 케이스 작성", "CI 골든셋 게이트", "툴 호출 검증"]
tags: ["mcp-eval", "mcp-agent", "lastmile-ai", "assertion", "golden-set", "CI"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["mcp-eval의 assertion 종류는?", "mcp-eval 골든셋은 어떻게 구성하는가?", "MCP 툴 호출 순서를 검증할 수 있는가?"]
related_chunks: ["v3-mcp-inspector", "v3-regression-gate"]
supersedes: ["rag-mcp-eval-001"]
---

# mcp-eval / mcp-agent: MCP 서버 평가 프레임워크

## 한 줄 요약
mcp-eval(lastmile-ai)은 MCP 서버의 정확성·툴 사용·성능·품질·경로 효율을 검증하는 어서션 API를 제공하며, CI 골든셋 게이트로 활용할 수 있다.

## 핵심 내용

### 어서션 API 5범주

1. **정확성**: `Expect.content.contains`, `Expect.tools.output_matches`
2. **툴 사용**: `Expect.tools.was_called`, `Expect.tools.sequence`, `Expect.tools.was_called_with`
3. **성능**: `Expect.performance.response_time_under`, `Expect.performance.max_iterations`
4. **품질**: `Expect.judge.llm`, `Expect.judge.multi_criteria`
5. **경로 효율**: `Expect.path.efficiency(expected_tool_sequence, allow_extra_steps, tool_usage_limits)`

### 사용 방법
- `@task` 데코레이터로 테스트 정의.
- `mcpeval.yaml` 필수 설정 파일.
- OpenTelemetry `.jsonl` 트레이스 출력.
- `mcp-eval generate`로 테스트 자동 생성 가능.

### CI 골든셋 게이트
```bash
uv run mcp-eval run --golden tests/golden/ --min-pass 0.9
```

### 예제
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
    await session.assert_that(
        Expect.judge.llm("Summary should reflect the customer's current status", min_score=0.8),
        response=response,
    )
```
