---
chunk_id: "v3-determinism-max"
title: "결정론 최대화 원칙 (Shopify Roast의 교훈)"
category: "development"
section_path: "코드 품질 > 결정론 최대화"
audience: ["개발자", "아키텍트"]
use_cases: ["검증 전략 수립", "비결정성 관리", "신뢰성 향상"]
tags: ["determinism", "Roast", "Shopify", "Uber", "validation", "LLM-judge"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["결정론 최대화 원칙이란?", "검증 우선순위는?", "Shopify Roast란?"]
related_chunks: ["v3-spec-first", "v3-eval-methodology"]
supersedes: ["rag-determinism-max-001"]
---

# 결정론 최대화 원칙 (Shopify Roast의 교훈)

## 한 줄 요약
Shopify의 Roast DSL 철학 "비결정성은 신뢰성의 적"에 따라, 검증은 가능한 한 결정론적 수단으로 우선순위를 정한다.

## Shopify Roast
- Shopify는 구조화된 AI 워크플로우를 위한 Ruby DSL 'Roast'를 오픈소스화
- 철학: "non-determinism is the enemy of reliability"

## 적용 규칙 (생성 에이전트 시스템 프롬프트에 삽입)
> 검증은 가능한 한 결정론적 수단으로 한다. 우선순위:
> 1. 타입체커·스키마 validation
> 2. 유닛 테스트
> 3. 골든 파일 비교
> 4. 룰 기반 린트
> 5. 최후에만 LLM judge
>
> LLM judge를 쓸 때는 무엇이 pass인지 열거하고 temperature=0으로 고정한다.

## 관련 사례
- Uber는 LangGraph 기반 Validator와 Autocover 에이전트로 21,000 개발자 시간 절감 (IDE 내장 + 하이브리드 LLM + 결정론 구조)

## 난이도/소요
하 (원칙) | 즉시
