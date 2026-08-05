---
chunk_id: "v3-04-quality-evaluation-ci-01"
title: "품질 평가 및 CI — 정의"
category: "operations"
section_path: "03_operations > 품질 평가 및 CI"
audience: ["운영자"]
tags: ["ci", "evaluation", "mcp-eval", "mcp-inspector", "quality", "regression-gate"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/04-quality-evaluation-ci.md"]
source_urls: ["https://arxiv.org/pdf/2404.05520", "https://docs.mcp-agent.com", "https://github.com/YawLabs/mcp-compliance", "https://www.anthropic.com/engineering/writing-tools-for-agents", "https://www.augmentcode.com/mcp/mcp-inspector"]
retrieval_questions: ["품질 평가 및 CI란 무엇인가?", "품질 평가 및 CI의 핵심 개념은?", "3계층 테스트 전략을 알려줘", "품질 평가 및 CI의 결정론 최대화 원칙은 무엇인가?", "품질 평가 및 CI의 MCP Inspector은 무엇인가?"]
related_chunks: ["v3-04-quality-evaluation-ci-02", "v3-mcp-eval", "v3-regression-gate"]
supersedes: ["chunk.114", "chunk.115"]
---

# 품질 평가 및 CI (1/2)

> **범위**: 정의, 설정법 · **출처 문서**: `03_operations/04-quality-evaluation-ci.md`

## 정의

품질 평가 및 CI는 MCP 서버와 툴의 품질을 검증하고 회귀를 방지하기 위한 계층적 테스트 전략입니다. MCP Inspector(연결/스키마 검증), mcp-eval(어서션 기반 eval), mcp-compliance(사양 준수 검사), 골든셋 회귀 게이트로 구성됩니다.

### 3계층 테스트 전략

| 계층 | 도구 | 목적 | 실행 시점 |
|------|------|------|----------|
| In-memory 유닛 테스트 | FastMCP Client / TS InMemoryTransport | 서브초 피드백, 스키마 validation | 매 커밋 |
| 계약 테스트 | MCP Inspector | 스키마 드리프트, conformance | CI |
| Eval 골든셋 | mcp-eval | 툴 사용 정확도, 응답 품질 | CI (회귀 게이트) |

### 결정론 최대화 원칙

Shopify Roast의 철학: "비결정성은 신뢰성의 적". 검증 우선순위: (1) 타입체커·스키마 validation, (2) 유닛 테스트, (3) 골든 파일 비교, (4) 룰 기반 린트, (5) 최후에만 LLM judge. LLM judge 사용 시 temperature=0 고정.

## 설정법

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector
# UI: localhost:6274, proxy: 6277
# CLI 모드로 CI 자동화:
npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server
```
Node.js ^22.7.5 필요. 첫 관문: Inspector가 연결/툴 나열 못 하면 에이전트도 못 합니다.

### mcp-eval (lastmile-ai)

어서션 API 4범주:
- 정확성: Expect.content.contains, Expect.tools.output_matches
- 툴 사용: Expect.tools.was_called, Expect.tools.sequence, Expect.tools.was_called_with
- 성능: Expect.performance.response_time_under, Expect.performance.max_iterations
- 품질: Expect.judge.llm, Expect.judge.multi_criteria
- 경로 효율: Expect.path.efficiency(expected_tool_sequence, allow_extra_steps, tool_usage_limits)

mcpeval.yaml 필수, OpenTelemetry .jsonl 트레이스 출력, mcp-eval generate로 테스트 자동 생성.

### mcp-compliance (YawLabs)

8개 카테고리 88개 테스트, A-F 등급, 버전된 JSON 리포트(schemaVersion, specVersion).

### Cross-model review 설정

```bash
# 1) Claude가 MCP 서버 생성
claude -p "Generate MCP server per spec.md" > out.log
# 2) Gemini가 독립 리뷰 (동일 spec.md만 주고 구현은 검토 대상으로)
gemini -p "Review the diff against spec.md. List: (a) spec 위반, (b) 보안 문제, (c) 스키마 드리프트."
# 3) 두 결과가 불일치하는 항목만 사람 리뷰 큐로
```
리뷰어에게는 spec만 주고 생성자의 논리는 주지 않습니다 (앵커링 방지).
