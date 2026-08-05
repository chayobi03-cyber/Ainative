---
chunk_id: "v3-anti-patterns"
title: "실패·안티패턴과 비용 사고"
category: "reference"
section_path: "참고 > 안티패턴"
audience: ["아키텍트", "관리자", "재무"]
use_cases: ["실패 사례 학습", "비용 사고 방지", "현실적 기대치 설정"]
tags: ["anti-pattern", "Gartner", "McKinsey", "cost-accident", "fan-out", "autocompact"]
priority: "medium"
confidence: "mixed"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["에이전트 프로젝트 실패율은?", "비용 급증 사고 사례는?", "가장 흔한 비용 급증 원인은?"]
related_chunks: ["v3-enterprise-cases", "v3-cost-visibility"]
supersedes: ["rag-anti-patterns-001"]
---

# 실패·안티패턴과 비용 사고

## 한 줄 요약
Gartner는 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망하며, 파일럿의 88%는 출시되지 못한다. 비용 사고도 빈번하므로 가시화가 선택이 아니다.

## 실패 통계 (⚠️ 컨설팅사 취합)
- Gartner: 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망
- McKinsey: 23%의 기업만이 AI 에이전트를 스케일한다
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%
- 파일럿의 88%는 출시되지 못함

## 첫 에이전트 대상 선정 기준
내부 헬프데스크가 강력한 첫 에이전트인 이유는 데이터를 소유하고 있고 실패 비용이 낮기 때문이다.

## 비용 사고
- 한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금을 기록
- Microsoft는 비용이 예산을 초과해 롤아웃을 공개적으로 철회
- **가장 흔한 비용 급증 원인**: 서브에이전트 팬아웃 (하나의 태스크가 20개 이상의 병렬 에이전트를 스폰)과 autocompact 루프
