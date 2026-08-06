---
chunk_id: rag-workflow-patterns-001
title: 워크플로우 아키텍처 패턴 (Anthropic Building Effective Agents)
category: architecture
section_path: "아키텍처 > 워크플로우 패턴"
audience: ['아키텍트', '개발자', '기술 기획자']
use_cases: ['에이전트 시스템 설계', '워크플로우 패턴 선택', '복잡도 관리']
tags: ['workflow', 'prompt-chaining', 'routing', 'parallelization', 'orchestrator', 'evaluator-optimizer']
priority: medium
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['워크플로우와 에이전트의 차이는?', '5가지 워크플로우 패턴은?', '언제 프레임워크 없이 direct API를 써야 하는가?']
related_chunks: ['rag-framework-comparison-001', 'rag-component-selection-001']
---
# 워크플로우 아키텍처 패턴 (Anthropic Building Effective Agents)

## 한 줄 요약
Anthropic "Building Effective Agents"(2024-12)는 워크플로우(LLM·툴이 사전 정의된 코드 경로로 오케스트레이션)와 에이전트(LLM이 자기 프로세스·툴 사용을 동적 지휘)를 구분하고, "가장 단순한 해법부터, 필요할 때만 복잡도 추가"를 권장한다.

## 핵심 원칙
- "가장 단순한 해법부터, 필요할 때만 복잡도 추가"
- 에이전트 시스템을 아예 안 만드는 것도 선택지 (에이전트는 latency·비용을 정확도와 맞바꿈)
- 프레임워크는 프롬프트를 가리고 과설계를 유발하므로 **direct LLM API부터** 권장

## 5가지 워크플로우 패턴

### 1. Prompt chaining
- 각 LLM 호출이 앞 출력을 처리
- 결정론적 순차 태스크에 적합

### 2. Routing
- 입력 분류 → 전문 후속 태스크
- 고객 문의 등 입력 카테고리가 뚜렷할 때

### 3. Parallelization
- sectioning (독립 서브태스크 병렬)
- voting (동일 태스크 다회 실행 후 집계)
- 속도·다관점 신뢰도가 필요할 때

### 4. Orchestrator-workers
- 중앙 LLM이 동적 분해·위임·종합
- 서브태스크를 예측 불가한 멀티파일 코딩/리서치에 적합

### 5. Evaluator-optimizer
- 생성-평가 피드백 루프

## Agent Skills와의 관계
Agent Skills는 별개 축 (범용 에이전트 위 도메인 전문성을 on-demand 로드) — 워크플로우 우선 규율을 대체하지 않고 보완.
