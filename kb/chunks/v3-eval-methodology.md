---
chunk_id: "v3-eval-methodology"
title: "평가 방법론과 비결정성 다루기"
category: "quality"
section_path: "평가·운영 > 방법론"
audience: ["개발자", "QA", "아키텍트"]
use_cases: ["eval 케이스 설계", "비결정적 결과 처리", "회귀 방지"]
tags: ["eval", "golden-set", "LLM-as-judge", "pass-k", "non-determinism", "UNSTABLE"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["LLM-as-judge의 한계는?", "pass^k 통계 판정이란?", "UNSTABLE을 어떻게 처리해야 하는가?", "3계층 평가 전략은?"]
related_chunks: ["v3-regression-gate", "v3-observability-otel"]
supersedes: ["rag-eval-methodology-001"]
---

# 평가 방법론과 비결정성 다루기

## 한 줄 요약
평가는 골든 데이터셋(>=30 케이스), task success rate, tool-call accuracy, trajectory evaluation, LLM-as-judge를 활용하되, 비결정성을 다루기 위해 pass^k 통계 판정과 3계층 전략을 사용해야 한다.

## 평가 방법론
- 골든 데이터셋 (>=30 케이스 회귀셋)
- task success rate
- tool-call accuracy (정확한 툴 선택 + 파라미터)
- trajectory evaluation
- LLM-as-judge (한계: judge 자체가 비결정적, "stably wrong" 가능)

## 3계층 전략
1. **deterministic 로직** (라우팅·파싱·상태전이): 매 커밋 유닛테스트 (`pytest -m "not llm_eval"`)
2. **품질 차원** (faithfulness/relevance/coherence/hallucination 0.0~1.0 임계): eval 테스트
3. **전체 태스크**: online eval

## 비결정성 다루기
- judge temperature=0
- pass/fail 기준 최대한 구체화 (무엇이 pass인지 나열)
- 각 케이스 3회 실행 majority-vote
- 동일 케이스가 10%+ 뒤집히면 기준 재작성
- **pass^k/pass@k**: "k회 중 1회 이상 성공 확률"로 통계 판정
- **UNSTABLE을 CI 실패 상태로 취급** (단일 pass rate 대신 agreement 보고)
- judge·agent 모델 버전 pinning
- 3-of-5 flip을 60% pass로 평균내면 회귀가 숨는다 ("95% pass at 0.6 judge agreement is noise")
