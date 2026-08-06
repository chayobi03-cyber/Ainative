---
chunk_id: chunk.122
source_file: 03_operations/05-cost-performance-optimization.md
title: "비용·성능 최적화"
section: "예외 사례"
section_id: exceptions
category: operations
tags: [cost, performance, prompt-caching, ccusage, model-routing, token-efficiency]
---

# 비용·성능 최적화 - 예외 사례

### 비용 급증 사고

- 한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금 기록
- Microsoft는 비용 초과로 롤아웃 공개 철회
- 가장 흔한 비용 급증 원인: 서브에이전트 팬아웃(하나의 태스크가 20개 이상의 병렬 에이전트 스폰)과 autocompact 루프

### 캐시 무효화

정적 블록에 타임스탬프, 요청 ID, 세션 ID 등 동적 값이 섞이면 캐시 히트율이 0이 됩니다. 안정 프롬프트에서 히트율이 30% 미만이면 write 프리미엄이 read 절감보다 클 수 있습니다.

### 모델 가격 변동

가격은 2026년 중반 기준이며 도입기 할인이 걸려 있습니다. Sonnet의 $2/$10 도입가는 2026-08-31 종료 예정 등, 모든 비용 계산은 재확인이 필요합니다.

### 토크나이저 변경

Claude 4.7 이후 모델과 Claude Mythos Preview는 새 토크나이저를 사용하여 같은 텍스트에 대해 약 30% 더 많은 토큰을 생성합니다. 모델 업그레이드 시 토큰 예산과 컨텍스트 한도를 재계산해야 합니다.