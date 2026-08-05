---
chunk_id: "v3-mcp-compliance"
title: "mcp-compliance와 계약 테스트 원칙"
category: "quality"
section_path: "품질 검증 > mcp-compliance"
audience: ["개발자", "QA", "운영자"]
use_cases: ["MCP 사양 준수 검증", "계약 드리프트 감지", "스키마 회귀 방지"]
tags: ["mcp-compliance", "YawLabs", "contract-test", "schema-drift", "compliance"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["mcp-compliance란?", "계약 테스트 원칙은?", "스키마 드리프트를 어떻게 감지하는가?"]
related_chunks: ["v3-mcp-inspector", "v3-mcp-eval"]
supersedes: ["rag-mcp-compliance-001"]
---

# mcp-compliance와 계약 테스트 원칙

## 한 줄 요약
mcp-compliance(YawLabs)는 8개 카테고리 88개 테스트로 MCP 사양 준수를 검증하며, 각 툴을 API 계약으로 취급해 스키마 드리프트·레이턴시·derived content 회귀를 감지한다.

## mcp-compliance
- 8개 카테고리 88개 테스트.
- A-F 등급 부여.
- 버전된 JSON 리포트 (schemaVersion, specVersion).
- GitHub: https://github.com/YawLabs/mcp-compliance

## 계약 테스트 원칙
각 툴을 API 계약으로 취급하여 다음을 감지:
- 스키마 드리프트
- 레이턴시 회귀
- derived content 변경

### 계층화 전략
1. In-memory 유닛 테스트 (FastMCP Client / TS InMemoryTransport, 서브초 피드백)
2. 스키마 validation (CI에서 계약 드리프트 차단)
3. Inspector conformance (최종 관문)

### 주의사항
- 복잡 스키마의 `$ref`/`anyOf`는 일부 클라이언트가 취약하므로 Inspector로 실제 노출 스키마 확인 필수.
