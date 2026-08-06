---
chunk_id: chunk.120
source_file: 03_operations/05-cost-performance-optimization.md
title: "비용·성능 최적화"
section: "설정법"
section_id: setup
category: operations
tags: [cost, performance, prompt-caching, ccusage, model-routing, token-efficiency]
---

# 비용·성능 최적화 - 설정법

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