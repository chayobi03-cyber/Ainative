---
chunk_id: chunk.121
source_file: 03_operations/05-cost-performance-optimization.md
title: "비용·성능 최적화"
section: "운영 가이드"
section_id: operations
category: operations
tags: [cost, performance, prompt-caching, ccusage, model-routing, token-efficiency]
---

# 비용·성능 최적화 - 운영 가이드

### 캐시 히트율 모니터링

cache_read_input_tokens를 반드시 모니터링합니다. 안정 프롬프트에서 60% 미만 히트율은 구조적 문제 신호입니다. 정적 블록에 타임스탬프·요청 ID 등이 섞이면 히트율이 0이 됩니다.

실사례: ProjectDiscovery는 동적 콘텐츠를 재배치해 Anthropic 캐시 히트율을 7%에서 84%로 끌어올려 전체 LLM 비용을 59~70% 절감, 프로덕션에서 98억 토큰을 캐시로 서빙.

### Tool Search Tool (토큰 절감)

Anthropic "Introducing advanced tool use" (2025-11-24): 대형 툴 라이브러리 MCP eval 정확도가 Opus 4 49%→74%, Opus 4.5 79.5%→88.1%로 향상. 5개 서버(약 58 tools) 셋업 시 툴 정의가 약 55,000 토큰 소비, defer_loading: true 적용 시 ~134k→~5k로 약 85% 토큰 절감.

### 토큰 효율 툴 설계

- 페이지네이션, range, 필터, truncation을 기본값과 함께
- Claude Code는 툴 응답을 기본 25,000 토큰으로 제한
- response_format enum(concise/detailed)으로 verbosity 제어 (예: detailed 206토큰 vs concise 72토큰, 약 1/3)
- 에러 메시지도 "무엇을 고쳐야 하는지"를 포함 (불투명한 traceback 금지)

### 비용 가시화 보완 도구

- Claude-Code-Usage-Monitor: 실시간 대시보드
- claude-code-otel: 팀용 셀프호스팅 관측 스택 (Langfuse/OTel과 직접 결합 가능)

### 모델 라우팅 주의사항

Opus 5는 입력 기준 Sonnet 5의 2.5배 (도입기), 정가 복귀 후 1.67배. 옛 가이드가 인용하는 5배는 Opus 4.1 기준이며 Opus 4.1은 deprecated. 모델 배수 기반 라우팅 규칙은 하드코딩하지 말고 설정으로 뺄 것.

Claude 4.7 이후 모델은 새 토크나이저를 쓰며 같은 텍스트에 대해 약 30% 더 많은 토큰을 생성. 모델 업그레이드 시 토큰 예산·컨텍스트 한도 재계산 필요. 회귀 게이트에 "토큰 사용량 회귀" 항목 추가 권장.