# 비용·성능 최적화

> **카테고리**: operations
> **태그**: cost, performance, prompt-caching, ccusage, model-routing, token-efficiency

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

---

# 비용·성능 최적화 - 출처

- [Anthropic - Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic - Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)
- [ccusage (npm)](https://www.npmjs.com/package/ccusage)
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)

---

