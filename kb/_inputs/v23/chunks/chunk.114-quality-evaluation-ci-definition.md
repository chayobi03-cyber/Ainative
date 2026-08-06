---
chunk_id: chunk.114
source_file: 03_operations/04-quality-evaluation-ci.md
title: "품질 평가 및 CI"
section: "정의"
section_id: definition
category: operations
tags: [quality, evaluation, mcp-inspector, mcp-eval, regression-gate, ci]
---

# 품질 평가 및 CI - 정의

품질 평가 및 CI는 MCP 서버와 툴의 품질을 검증하고 회귀를 방지하기 위한 계층적 테스트 전략입니다. MCP Inspector(연결/스키마 검증), mcp-eval(어서션 기반 eval), mcp-compliance(사양 준수 검사), 골든셋 회귀 게이트로 구성됩니다.

### 3계층 테스트 전략

| 계층 | 도구 | 목적 | 실행 시점 |
|------|------|------|----------|
| In-memory 유닛 테스트 | FastMCP Client / TS InMemoryTransport | 서브초 피드백, 스키마 validation | 매 커밋 |
| 계약 테스트 | MCP Inspector | 스키마 드리프트, conformance | CI |
| Eval 골든셋 | mcp-eval | 툴 사용 정확도, 응답 품질 | CI (회귀 게이트) |

### 결정론 최대화 원칙

Shopify Roast의 철학: "비결정성은 신뢰성의 적". 검증 우선순위: (1) 타입체커·스키마 validation, (2) 유닛 테스트, (3) 골든 파일 비교, (4) 룰 기반 린트, (5) 최후에만 LLM judge. LLM judge 사용 시 temperature=0 고정.