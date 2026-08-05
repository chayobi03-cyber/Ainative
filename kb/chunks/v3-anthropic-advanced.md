---
chunk_id: "v3-anthropic-advanced"
title: "Anthropic Advanced Tool Use: Tool Search와 defer_loading"
category: "best-practices"
section_path: "설계 원칙 > Advanced Tool Use"
audience: ["개발자", "아키텍트"]
use_cases: ["대형 툴 라이브러리 최적화", "토큰 절감", "툴 발견 자동화"]
tags: ["Anthropic", "tool-search", "defer-loading", "token-reduction", "Opus-4.5"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["Tool Search Tool이란?", "defer_loading의 토큰 절감 효과는?", "Code execution with MCP 패턴은?"]
related_chunks: ["v3-anthropic-principles", "v3-prompt-caching"]
supersedes: ["rag-anthropic-advanced-001"]
---

# Anthropic Advanced Tool Use: Tool Search와 defer_loading

## 한 줄 요약
Anthropic의 Tool Search Tool과 defer_loading을 활용하면 대형 툴 라이브러리에서 토큰을 최대 85% 절감하고 정확도를 크게 향상시킬 수 있다.

## 핵심 내용

### Tool Search Tool (2025-11-24, Opus 4.5 동시 발표)
- 활성화 시 대형 툴 라이브러리 MCP eval 정확도 향상:
  - Opus 4: 49% -> 74%
  - Opus 4.5: 79.5% -> 88.1%
- 5개 서버(약 58 tools) 셋업 시 툴 정의가 약 55,000 토큰 소비.

### defer_loading
- `defer_loading: true` 적용 시 토큰 소비 ~134k -> ~5k로 **약 85% 절감** (on-demand 툴 발견).

### description 개선 효과
- description 개선만으로 "40% task completion time 감소" 사례 보고.

### Code execution with MCP (2025-11-04)
- 툴 정의를 전부 컨텍스트에 올리는 기존 방식의 토큰 낭비를 해결.
- MCP 툴을 코드 API(파일)로 노출하고 모델이 코드를 작성해 호출.
- progressive tool discovery, 중간 데이터가 모델을 안 거침 (민감정보 un-tokenize 패턴).
- 단, Anthropic은 개념만 제시하고 구현 코드는 미제공 (샌드박스 보안 부담을 팀에 전가).
