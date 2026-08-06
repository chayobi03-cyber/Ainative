---
chunk_id: rag-anthropic-principles-001
title: Anthropic 공식 툴 작성 5원칙 (2025-09-11)
category: best-practices
section_path: "설계 원칙 > Anthropic 가이드"
audience: ['개발자', '아키텍트', '프롬프트 엔지니어']
use_cases: ['MCP 툴 설계', '툴 description 작성', '툴 품질 개선']
tags: ['Anthropic', 'tool-design', 'description', 'naming', 'token-efficiency', 'prompt-engineering']
priority: high
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['Anthropic 툴 작성 5원칙은?', 'MCP 툴 description은 어떻게 써야 하는가?', '툴 네이밍 규칙은?', '토큰 효율을 높이는 방법은?']
related_chunks: ['rag-anthropic-advanced-001', 'rag-mcp-dev-rules-001']
---
# Anthropic 공식 툴 작성 5원칙 (2025-09-11)

## 한 줄 요약
Anthropic 공식 가이드 "Writing effective tools for agents — with agents"는 툴을 결정론적 시스템과 비결정론적 에이전트 간의 계약으로 규정하고, 5대 원칙을 제시한다.

## 핵심 내용

### 1. 올바른 툴 선택
- API를 얇게 래핑하지 말 것. `list_contacts` 대신 `search_contacts`.
- 여러 API 호출을 하나로 합친 고레버리지 툴(`schedule_event`, `get_customer_context`)을 소수만 구현.
- 툴이 많거나 겹치면 에이전트가 혼란.

### 2. 네임스페이싱
- 서비스·리소스별 prefix 사용 (`asana_search`, `asana_projects_search`).
- prefix vs suffix는 LLM별로 효과가 달라 eval로 결정.

### 3. 의미 있는 컨텍스트 반환
- `uuid`·`mime_type` 같은 저수준 식별자 대신 `name`·`file_type` 사용.
- UUID를 의미 있는 언어/0-index로 해석하면 환각 감소·검색 정밀도 향상.
- `response_format` enum(`concise`/`detailed`)으로 verbosity 제어 (예시: detailed 206토큰 vs concise 72토큰, 약 1/3).

### 4. 토큰 효율
- 페이지네이션·range·필터·truncation을 기본값과 함께 제공.
- Claude Code는 툴 응답을 **기본 25,000 토큰**으로 제한.
- 에러 메시지도 "무엇을 고쳐야 하는지"를 포함 (불투명한 traceback 금지).

### 5. 툴 description 프롬프트 엔지니어링
- 신입에게 설명하듯 암묵지를 명시화.
- `user` 대신 `user_id`처럼 명확한 파라미터명 사용.
- Claude Sonnet 3.5가 SWE-bench Verified에서 description 정밀 개선만으로 SOTA 달성.

## 평가 방법론
실제 워크플로우 기반 태스크 수십 개 생성 → 각 태스크에 검증 가능한 응답 페어링 → 단순 while-loop 에이전트로 프로그래매틱 실행 → CoT 유도 → transcript·tool-call 메트릭 분석 → Claude Code로 툴 자동 리팩터. Held-out test set으로 오버핏 방지.
