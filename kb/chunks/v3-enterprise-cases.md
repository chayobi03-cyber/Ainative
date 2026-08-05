---
chunk_id: "v3-enterprise-cases"
title: "선도 기업 사례 (Block/Goose, Uber, Coinbase 등)"
category: "governance"
section_path: "사례 > 선도 기업"
audience: ["아키텍트", "기술 기획자", "관리자"]
use_cases: ["사내 도입 근거 수집", "아키텍처 참고", "기대효과 설정"]
tags: ["Block", "Goose", "Uber", "Coinbase", "Stripe", "Ramp", "Google", "Agent-Smith"]
priority: "medium"
confidence: "mixed"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["Block의 Goose 사례는?", "Uber의 에이전트 도입 효과는?", "사내 코딩 에이전트 도입 수치는?", "공통 아키텍처 패턴은?"]
related_chunks: ["v3-gradual-autonomy", "v3-anti-patterns"]
supersedes: ["rag-enterprise-cases-001"]
---

# 선도 기업 사례 (Block/Goose, Uber, Coinbase 등)

## 한 줄 요약
Block(Goose), Uber, Coinbase, Stripe, Ramp, Google 등 선도 기업들의 사내 에이전트 도입 사례와 공통 아키텍처 패턴을 정리한다. (⚠️ 대부분 2차 출처 취합, 개별 검증 권장)

## Block (Goose) — 사내 전사 배포의 교과서
- 12,000명 직원 전반의 도구와 워크플로우 정리
- **Default Distribution: Goose가 모든 Block 노트북에 자동 설치, 자동 업데이트** ← 채택률의 근본 해법
- LLM 비종속 설계 (OpenAI·Anthropic·Meta 등 복수 모델, Databricks로 사내 호스팅)
- 동적 MCP 서버 활성화, Snowflake MCP를 통한 자연어→SQL, Recipe 스키마
- Stripe가 Goose를 Minions로 포크 → 공유 인프라의 가치 입증

## 사내 코딩 에이전트 도입 수치 (⚠️ 2차 출처)
- **Coinbase Forge**: 머지된 PR의 5%, PR 사이클 타임 150시간 → 15시간
- **Uber**: LangGraph 기반 Validator·Autocover로 21,000 개발자 시간 절감
- **Abnormal AI**: 백그라운드 에이전트 PR 비율 13%
- **Ramp**: 백그라운드 에이전트 PR 비율 50%+
- **Google Agent Smith**: 사내에서 너무 인기가 많아 접근 제한, 신규 프로덕션 코드의 25%+
- **Mux**: 병렬 에이전트 플릿 3.5배 처리량

## 공통 아키텍처
Slack 호출 → 격리 샌드박스 → CI 루프 → PR-ready 산출물

## 본 프로젝트 시사점
1. LLM 비종속 설계를 처음부터 (3사 계약 보유 = 강점)
2. 동적 MCP 서버 활성화 = 툴 폭발 대응의 사내 검증된 답
3. 자동 설치·자동 업데이트 채널 확보가 최우선 결정
