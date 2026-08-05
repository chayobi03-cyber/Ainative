---
chunk_id: "v3-prompt-caching"
title: "Prompt caching: 단일 최대 비용 절감 레버"
category: "cost"
section_path: "비용·성능 > Prompt caching"
audience: ["개발자", "아키텍트", "재무"]
use_cases: ["LLM 비용 절감", "TTFT 단축", "토큰 효율화"]
tags: ["prompt-caching", "cache_control", "Anthropic", "OpenAI", "Google", "TTFT", "token-reduction"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["prompt caching의 절감 효과는?", "cache_control breakpoint는 어떻게 설정하는가?", "캐시 히트율이 낮은 이유는?"]
related_chunks: ["v3-cost-visibility", "v3-model-routing"]
supersedes: ["rag-prompt-caching-001"]
---

# Prompt caching: 단일 최대 비용 절감 레버

## 한 줄 요약
prompt caching을 적용하면 입력 토큰을 최대 90% 절감하고 TTFT(Time To First Token)를 최대 85% 단축할 수 있다. 정적→동적 순서로 프롬프트를 배열하고 정적 블록 끝에 breakpoint를 찍는 것이 핵심이다.

## 핵심 수치
- **Anthropic**: cache_control breakpoint, write는 입력의 1.25배(5분 TTL) 또는 2.0배(1시간 TTL), read는 0.10배 — **90% 할인**. 최소 1,024 토큰.
- **OpenAI**: 자동 캐싱, 서버사이드, 코드 변경 불필요, read는 0.5배 — **50% 할인**.
- **Google**: implicit caching, **75% 할인**. 입력 토큰만 건드리며 출력은 절대 할인되지 않음.

## 손익분기
- Anthropic 5분 티어: 캐시 write당 약 1.4회 read에서 손익분기
- 안정 프롬프트에서 히트율 ~30% 미만이면 write 프리미엄이 read 절감보다 클 수 있음
- 안정 프롬프트에서 60% 미만 히트율은 구조적 문제 신호

## 실사례
- ProjectDiscovery: 동적 콘텐츠 재배치로 캐시 히트율 7% → 84%, 전체 LLM 비용 59~70% 절감, 프로덕션에서 98억 토큰 캐시 서빙 (⚠️ 2차 인용)

## 적용 방법
**정적 → 동적 순서로 프롬프트를 배열**하고 정적 블록 끝에 breakpoint를 찍는다:
```
[system prompt] [tool definitions] [사내 정책·컨벤션] ← 여기까지 cache_control
[대화 히스토리] [현재 요청]                          ← 매번 변하는 부분
```

## 본 프로젝트 적용
툴 생성 에이전트는 Anthropic 5원칙 + 사내 규칙 + MCP 템플릿이라는 거대하고 안정적인 프리픽스를 매 호출 재전송한다. 캐싱 적용의 교과서적 대상.

## 리스크
- 정적 블록에 타임스탬프·요청 ID 등이 섞이면 히트율 0
- `cache_read_input_tokens`를 반드시 모니터링

## 난이도/소요
하 | 2시간
