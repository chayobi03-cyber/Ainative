---
chunk_id: "v3-mcp-inspector"
title: "MCP Inspector: 품질 검증 첫 관문"
category: "quality"
section_path: "품질 검증 > MCP Inspector"
audience: ["개발자", "QA", "운영자"]
use_cases: ["MCP 서버 검증", "CI conformance 테스트", "스키마 확인"]
tags: ["MCP", "Inspector", "conformance", "CI", "JSON-RPC", "stdout"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["MCP Inspector란?", "Inspector CLI 모드는 어떻게 쓰는가?", "stdout 오염 문제는?"]
related_chunks: ["v3-mcp-eval", "v3-mcp-compliance"]
supersedes: ["rag-mcp-inspector-001"]
---

# MCP Inspector: 품질 검증 첫 관문

## 한 줄 요약
MCP Inspector는 공식 검증 도구로, MCP 서버가 연결되고 툴을 나열할 수 있는지 확인하는 첫 번째 관문이다. Inspector가 통과하지 못하면 에이전트도 사용할 수 없다.

## 핵심 내용

### 기본 정보
- 공식 도구: `npx @modelcontextprotocol/inspector`
- Node.js ^22.7.5 필요
- UI 기본 localhost:6274, proxy 6277
- 기본 세션 토큰 인증
- Tools 탭에서 스키마·description·실행 결과·raw JSON-RPC 확인

### CLI 모드 (CI 자동화)
```bash
npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server
```
- exit code로 pass/fail 판정.
- CI 파이프라인에 자동 통합 가능.

### 핵심 원칙
- **첫 관문**: Inspector가 연결/툴 나열 못 하면 에이전트도 못 한다.
- **stdout 오염 금지**: stdout에 비-JSON 출력(print/log)이 섞이면 stdio JSON-RPC 파서가 깨진다. 로깅은 반드시 stderr로.

### 계층화된 테스트 전략
1. In-memory 유닛 테스트 (FastMCP Client / TS InMemoryTransport, 서브초 피드백)
2. 스키마 validation (CI에서 계약 드리프트 차단)
3. Inspector conformance (최종 관문)

### 주의사항
- 복잡 스키마의 `$ref`/`anyOf`는 일부 클라이언트가 취약하므로 Inspector로 실제 노출 스키마 확인 필수.
