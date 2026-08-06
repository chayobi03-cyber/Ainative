---
chunk_id: rag-gradual-autonomy-001
title: 점진적 자율성 로드맵
category: governance
section_path: "배포 > 자율성 로드맵"
audience: ['아키텍트', '관리자']
use_cases: ['에이전트 자율성 단계 설계', '안전한 도입 경로']
tags: ['autonomy', 'gradual', 'incremental', 'safety', 'adoption']
priority: medium
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['에이전트 자율성은 어떻게 단계적으로 높여야 하는가?', '완전 자율으로 시작하면 안 되는 이유는?']
related_chunks: ['rag-enterprise-cases-001', 'rag-roadmap-001']
---
# 점진적 자율성 로드맵

## 한 줄 요약
완전 자율성으로 시작하지 말고, 테스트 추가 → 작은 버그 수정 → 저위험 리팩터 → 의존성 업데이트 → 모듈 간 기능 작업 순서로 점진적으로 자율성을 높인다.

## 단계적 경로
1. 에이전트가 테스트를 추가하고 작은 버그를 고치게 한다
2. 저위험 리팩터를 하게 한다
3. 의존성 업데이트와 문서 동기화를 맡긴다
4. 그 다음에야 모듈 간 기능 작업을 시도한다

## 본 프로젝트 적용
사내 배포 시 **툴 생성 에이전트의 자율성도 단계적으로**:
- 1차 배포: "코드 초안 + 테스트를 생성하되 커밋은 사람이"
- 안정화 후: 자동 PR

## 첫 배포 대상 선정 기준
내부 헬프데스크가 강력한 첫 에이전트인 이유는 데이터를 소유하고 있고 실패 비용이 낮기 때문이다.
