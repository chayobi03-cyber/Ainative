---
chunk_id: "v3-05-cost-performance-optimization-01"
title: "비용·성능 최적화 — 정의"
category: "operations"
section_path: "03_operations > 비용·성능 최적화"
audience: ["운영자"]
tags: ["ccusage", "cost", "model-routing", "performance", "prompt-caching", "token-efficiency"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/05-cost-performance-optimization.md"]
source_urls: ["https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching", "https://www.anthropic.com/engineering/advanced-tool-use", "https://www.anthropic.com/engineering/writing-tools-for-agents", "https://www.npmjs.com/package/ccusage"]
retrieval_questions: ["비용·성능 최적화란 무엇인가?", "비용·성능 최적화의 핵심 개념은?", "비용·성능 최적화는 어떻게 설정하는가?", "비용·성능 최적화 초기 구성 절차는?"]
related_chunks: ["v3-05-cost-performance-optimization-02", "v3-cost-visibility", "v3-budget-management"]
supersedes: ["chunk.119", "chunk.120"]
---

# 비용·성능 최적화 (1/2)

> **범위**: 정의, 설정법 · **출처 문서**: `03_operations/05-cost-performance-optimization.md`

## 정의

비용·성능 최적화는 AI 에이전트 운영에서 발생하는 토큰 비용과 응답 지연을 체계적으로 절감하는 영역입니다. prompt caching(입력 토큰 최대 90% 절감), ccusage(비용 가시화), 모델 라우팅(서브에이전트 비용 절감), 컨텍스트 정리로 구성됩니다.

### 절감 스택 요약

| 레버 | 절감 | 노력 | 비고 |
|------|------|------|------|
| Prompt caching | 입력 최대 90% | 하 | 프리픽스 안정성이 전제 |
| Batch API | 전 토큰 50% | 하 | 즉시성 불필요 작업만 |
| 모델 라우팅 | 워커 비용 대폭 | 하 | 서브에이전트 frontmatter |
| 컨텍스트 정리(/clear) | 누적 방지 | 하 | 태스크 간 컨텍스트 비우기 |
| 서브에이전트 팬아웃 제한 | 급증 방지 | 중 | 최대 병렬 수 상한 |

## 설정법

### Prompt caching 설정

정적 → 동적 순서로 프롬프트를 배열하고 정적 블록 끝에 cache_control breakpoint를 찍습니다:

```
[system prompt] [tool definitions] [사내 정책·컨벤션] ← 여기까지 cache_control
[대화 히스토리] [현재 요청]                          ← 매번 변하는 부분
```

핵심 수치:
- Anthropic: cache write 1.25x(5분 TTL) 또는 2.0x(1시간 TTL), read 0.10x — 90% 할인. 최소 1,024 토큰
- OpenAI: 자동 캐싱, read 0.5x — 50% 할인
- Google: implicit caching 75% 할인

### ccusage 설치

```bash
npm install -g ccusage
ccusage daily              # 일별
ccusage monthly            # 월별
ccusage blocks --live      # 실시간 5시간 과금 윈도우
ccusage daily --breakdown  # 모델별 분해
```
ccusage는 계정 설정 불필요, 무료 오픈소스, 로컬 JSONL 세션 로그만 파싱, API 키·네트워크 호출 없음. 폐쇄망 OK.

### 모델 라우팅 설정

서브에이전트 frontmatter에 model 필드 지정:
```markdown
---
name: schema-checker
description: MCP 툴 스키마 검증 전담
model: haiku
---
```
