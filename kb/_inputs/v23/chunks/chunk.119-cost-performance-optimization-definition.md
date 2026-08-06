---
chunk_id: chunk.119
source_file: 03_operations/05-cost-performance-optimization.md
title: "비용·성능 최적화"
section: "정의"
section_id: definition
category: operations
tags: [cost, performance, prompt-caching, ccusage, model-routing, token-efficiency]
---

# 비용·성능 최적화 - 정의

비용·성능 최적화는 AI 에이전트 운영에서 발생하는 토큰 비용과 응답 지연을 체계적으로 절감하는 영역입니다. prompt caching(입력 토큰 최대 90% 절감), ccusage(비용 가시화), 모델 라우팅(서브에이전트 비용 절감), 컨텍스트 정리로 구성됩니다.

### 절감 스택 요약

| 레버 | 절감 | 노력 | 비고 |
|------|------|------|------|
| Prompt caching | 입력 최대 90% | 하 | 프리픽스 안정성이 전제 |
| Batch API | 전 토큰 50% | 하 | 즉시성 불필요 작업만 |
| 모델 라우팅 | 워커 비용 대폭 | 하 | 서브에이전트 frontmatter |
| 컨텍스트 정리(/clear) | 누적 방지 | 하 | 태스크 간 컨텍스트 비우기 |
| 서브에이전트 팬아웃 제한 | 급증 방지 | 중 | 최대 병렬 수 상한 |