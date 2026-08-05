---
chunk_id: "v3-mcp-spec"
title: "MCP 사양 현황과 주요 리비전 (2024~2026)"
category: "specification"
section_path: "MCP > 사양 현황"
audience: ["개발자", "아키텍트", "기술 기획자"]
use_cases: ["MCP 서버 설계", "사양 버전 선택", "기술 의사결정"]
tags: ["MCP", "specification", "versioning", "protocol", "2025-11-25"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["MCP 사양의 주요 버전은?", "MCP 최신 stable 버전은 언제인가?", "MCP 2026-07-28 RC에서 바뀐 점은?"]
related_chunks: ["v3-mcp-transport", "v3-mcp-sdk"]
supersedes: ["rag-mcp-spec-001"]
---

# MCP 사양 현황과 주요 리비전 (2024~2026)

## 한 줄 요약
MCP(Model Context Protocol)는 날짜 기반 버저닝을 사용하며, 2024-11-05 초기 stable부터 2026-07-28 RC까지 빠르게 진화하고 있다. 사내 구축 시 2025-11-25 stable을 기준으로 pinning할 것을 권장한다.

## 언제 참고하나
- 새 MCP 서버를 설계할 때 사양 버전을 선택해야 할 때
- 기술 의사결정에서 MCP 사양의 지원 범위를 확인할 때
- 사양 업그레이드 시 영향 범위를 평가할 때

## 핵심 내용

### 주요 리비전 타임라인

- **2024-11-05**: 초기 stable. client-server 모델, tools/resources/prompts primitive 확립.
- **2025-03-26**: Streamable HTTP transport 도입, OAuth 2.1 authorization, **HTTP+SSE deprecated**.
- **2025-06-18**: structured tool output, elicitation(서버가 사용자에게 추가 입력 요청), resource links, OAuth Resource Server 분류, RFC 8707 Resource Indicators, JSON-RPC 배칭 제거.
- **2025-11-25 (최신 stable)**: OpenID Connect Discovery, tools/resources/prompts용 icons(SEP-973), incremental scope consent(SEP-835), URL mode elicitation(SEP-1036), sampling에 tool calling(SEP-1577), OAuth Client ID Metadata Documents(CIMD, SEP-991), experimental Tasks.
- **2026-07-28 RC**: stateless core, MCP Apps, Tasks를 확장으로 이동, 공식 deprecation 라이프사이클 정책. Roots/Sampling/Logging이 deprecated 예정으로 표시됨. Streamable HTTP는 Mcp-Method·Mcp-Name 헤더 요구(SEP-2243), list/resource 결과에 ttlMs·cacheScope(SEP-2549) 추가.

### Primitive 구성
- **Tools**: 모델이 호출하는 함수 (name + description + JSON Schema). 2025-06-18부터 structured output·resource link 선언 가능.
- **Resources**: URI로 식별되는 읽기 컨텍스트.
- **Prompts**: 재사용 템플릿.
- 클라이언트가 서버에 제공하는 역량: Sampling, Elicitation(2025-06-18 신규), Roots(작업 가능 디렉터리/URI 통지).

## 운영 체크리스트
- [ ] 사내 MCP 서버의 사양 버전을 2025-11-25 stable로 pinning했는가
- [ ] 2026-07-28 RC 정식화 시 stateless core·Roots/Sampling deprecated 대응 계획이 있는가
- [ ] 신규 구현에서 deprecated 기능(HTTP+SSE, Roots, Sampling)을 사용하지 않았는가
