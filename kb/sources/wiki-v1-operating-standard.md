<!-- markdownlint-disable MD013 MD033 MD041 -->

# 사내 AI 협업용 툴 생성 에이전트 운영 표준

| 항목 | 내용 |
|---|---|
| **문서명** | 사내 AI 협업용 툴 생성 에이전트 운영 표준 |
| **버전** | v1.0 |
| **작성일** | 2026년 8월 5일 |
| **정책 등급** | 사내 표준 (준필수) |
| **문서 상태** | 초안 (Draft) |
| **적용 범위** | 사내 AI 협업 환경 (Claude Code, Gemini CLI, MCP, Skills, Hooks, Plugins) |
| **관련 문서** | 본 문서의 RAG 청크 세트 (`rag_chunks/` 디렉토리) |

---

## 변경 이력

| 버전 | 일자 | 변경 내용 | 작성자 |
|---|---|---|---|
| v0.1 | 2026-08-04 | 종합 기술 리서치 보고서 초안 (MCP 사양·보안·eval·배포) | AI 협업팀 |
| v0.2 | 2026-08-05 | 저리스크·고ROI 실전 패턴 보강 (Quick Wins·컨텍스트·비용·사례) | AI 협업팀 |
| v0.3 | 2026-08-05 | 위키 구조/FAQ/정책/샘플 추가 (운영 표준 초안) | AI 협업팀 |
| v1.0 | 2026-08-05 | 3개 원본 통합·중복 제거·사내 위키 배포용 완성본 | AI 협업팀 |

---

## 목차

1. 개요 (목적, 핵심 원칙, 적용 범위)
2. 권장 아키텍처 (3층 구조: 연결층/지식층/통제층 + 구조 요약)
3. MCP 사양 및 전송 방식
4. Anthropic 툴 작성 가이드 (5원칙 + Advanced Tool Use)
5. MCP 품질 검증 (Inspector, mcp-eval, mcp-compliance, 계약 테스트)
6. MCP 보안 (사양 필수 통제 + 실제 사고/CVE)
7. Claude Agent Skills (포맷, progressive disclosure, 선택 기준)
8. 역할 분담: MCP / Skills / Hooks / Plugins / Subagents
9. 워크플로우 아키텍처 패턴 (5가지 패턴)
10. 에이전트 프레임워크 비교 (LangGraph, Claude Agent SDK 등)
11. 평가·운영 안정성 (방법론, 비결정성, 회귀 게이트, 관측)
12. Eval/Observability 셀프호스팅 (폐쇄망)
13. 사내 배포 및 거버넌스 (플러그인 마켓플레이스, 거버넌스 원칙, 채택)
14. 컨텍스트 엔지니어링 (AGENTS.md, 파일 메모리, llms.txt)
15. 코드 생성 품질 (Spec-first, Cross-model review, 결정론 최대화)
16. MCP 서버 운영 실전 (Gateway, 배포 채널, 개발 규칙)
17. 선도 기업 사례 (Block/Goose, Uber, Coinbase 등)
18. 사용자 편의성 (doctor, dry-run, 피드백)
19. 비용·성능 최적화 (prompt caching, ccusage, 모델 라우팅)
20. 운영 절차 (새 툴 만들 때, 배포 전, 운영 중, 변경 관리)
21. Claude Code 운영 가이드
22. Gemini CLI 운영 가이드
23. 정책 문구 (툴 설계, 보안, 운영, 품질)
24. 예시 설정 파일 (.mcp.json, CLAUDE.md, GEMINI.md, SKILL.md, CI YAML)
25. 3단계 로드맵 실행 계획
26. Quick Wins TOP 15
27. 종합 체크리스트 (사양/컨텍스트/강제장치/품질/보안/산출물/비용/배포)
28. FAQ
29. 부록: 고급 프롬프트 템플릿 (5종)
30. Caveats (주의사항 및 불확실성)

---

## TL;DR

- **1단계 MCP 서버 생성 에이전트부터 시작하되, 절대 "코드 생성기"로만 만들지 말고 "eval 하네스가 내장된 생성기"로 설계하라.** Anthropic 공식 가이드(2025년 9월 11일 "Writing effective tools for agents — with agents")는 툴을 "결정론적 시스템과 비결정론적 에이전트 간의 계약"으로 규정하고, 툴 품질은 프롬프트 엔지니어링과 eval 반복(human-written vs Claude-optimized held-out test set 비교)으로만 확보된다고 결론짓는다. 생성 에이전트가 MCP 서버 코드와 함께 mcp-eval 테스트 케이스·MCP Inspector 계약 테스트를 동시에 산출하도록 만들어야 "배포 후 회수 불가" 제약을 견딜 수 있다 ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- **전송 방식은 로컬은 stdio, 원격/사내 웹은 Streamable HTTP로 확정하고 SSE는 신규 구축에서 배제하라.** MCP 사양은 2025-03-26에 HTTP+SSE를 deprecated 처리했고, 2025-06-18(structured output·elicitation·OAuth Resource Server), 2025-11-25(최신 stable, CIMD·incremental scope), 2026-07-28 RC(stateless core)로 빠르게 진화 중이다. 보안은 사양이 명시적으로 "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server"를 요구하며, tool poisoning·rug pull·confused deputy가 실제 CVE(mcp-remote CVE-2025-6514, CVSS 9.6)로 입증되었으므로 allowlist·서명·감사로그가 필수다 ([GitHub — MCP spec security best practices](https://github.com/johnzfitch/claude-wiki/blob/master/06-MCP-Tools/General/mcp-specification-2025-11-25-basic-security-best-practices.md)).
- **배포 형태는 "Claude Code 플러그인 마켓플레이스(사내 GitHub 레지스트리) + managed-settings.json 거버넌스" 조합을 1순위로 권고한다.** 터미널 중심 환경에 가장 잘 맞고, `strictKnownMarketplaces`·`managed-mcp.json`으로 IT가 승인 공급망을 통제할 수 있다. 평가/관측은 폐쇄망 셀프호스팅이 가능한 Langfuse(오픈소스 MIT, ClickHouse+PostgreSQL 기반, 2026년 1월 16일 ClickHouse에 인수되었으나 오픈소스·셀프호스팅 유지) + OpenTelemetry GenAI semantic conventions를 표준으로 삼고, CI에 골든셋 회귀 게이트(≥30케이스, pass^k 통계 판정)를 붙여 모델 버전 업그레이드 회귀를 자동 차단하라 ([Langfuse](https://langfuse.com/self-hosting/configuration/observability)).
- **당장 체감 ROI가 큰 건 "더 많은 기능"이 아니라 운영·보안·재사용·관측이다.** 사내 도입에서는 툴 수를 늘리기보다 툴 호출 품질과 실패 복구를 높이는 쪽이 효과가 크다 ([Claude Code Best Practices](https://code.claude.com/docs/en/best-practices), [Claude Code MCP](https://code.claude.com/docs/en/mcp)). 실무적으로 가장 ROI가 큰 건 "툴을 잘 만드는 에이전트"보다 **"검증·배포·관측까지 자동으로 붙는 에이전트"**다.

---

## 1. 개요 (목적, 핵심 원칙, 적용 범위)

### 1.1 목적

이 문서는 사내 AI 협업 환경에서 Claude Code, Gemini CLI, MCP, Skills, Hooks, Plugins를 안전하고 일관되게 운영하기 위한 표준을 정의한다. 목표는 "코드를 대신 써주는 에이전트"가 아니라, **검증 가능한 도구·문서·테스트·설정 파일까지 함께 생성하는 에이전트**를 만드는 것이다 ([Claude Code Best Practices](https://code.claude.com/docs/en/best-practices), [Claude Code MCP](https://code.claude.com/docs/en/mcp)).

이 체계의 목적은 AI가 "그럴듯한 답"을 내는 것이 아니라, **실행 가능한 작업 결과**를 안정적으로 만드는 데 있다. 따라서 에이전트는 코드, 설정, 테스트, 문서, 검증 절차를 한 세트로 생성해야 한다.

### 1.2 핵심 원칙

1. 툴은 적게, 의미는 크게 설계한다.
2. 검증 가능한 결과만 채택한다.
3. 기본값은 안전해야 하며, 예외는 명시적으로 승인한다.
4. 반복되는 업무는 사람이 아니라 시스템이 기억하게 한다.
5. 배포 후 수정이 어렵다고 가정하고 처음부터 회수 가능하게 설계한다 ([Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)).
6. **비결정성은 신호의 적이며, 가능한 한 결정론적 수단으로 검증한다.**

### 1.3 적용 범위

- 사내 AI 툴 생성 에이전트
- Claude Code 기반 개발/운영 작업
- Gemini CLI 기반 개발/운영 작업
- MCP 서버, Skills, Hooks, Plugins, Subagents
- 평가(Eval), 관측(Observability), 보안 거버넌스

현업에서 가장 효과가 좋은 구조는 "연결은 MCP, 지식은 Skills, 강제는 Hooks, 배포는 Plugins, 복잡 작업은 Subagents"로 나누는 방식이다. 이 구조를 쓰면 팀마다 다른 업무라도 공통 운영 원칙을 유지할 수 있고, 새 사람이 와도 규칙을 빠르게 학습할 수 있다.

### 1.4 핵심 효과

- 반복 작업 시간 단축
- 잘못된 실행과 권한 오남용 감소
- 도구 품질의 회귀 방지
- 팀 전체 작업 방식의 표준화

---

## 2. 권장 아키텍처 (3층 구조: 연결층/지식층/통제층 + 구조 요약)

권장 아키텍처는 3층 구조다. 1층은 MCP 서버와 외부 시스템 연결, 2층은 Skills와 slash command로 반복 업무 표준화, 3층은 hooks와 CI eval로 품질을 강제하는 운영층이다.

### 2.1 연결층 (Connection Layer)

MCP 서버가 사내 DB, GitHub, 문서 저장소, 이슈 트래커, 검색 시스템을 연결한다. 이 계층은 "실제 일을 하는 도구"이므로 프로젝트 범위별로 최소한만 활성화하는 것이 좋다. 최근 실무 가이드는 "2~3개 핵심 MCP부터 시작하고 나머지는 필요할 때만 활성화"하는 방식을 권장한다.

### 2.2 지식층 (Knowledge Layer)

Skills는 반복되는 업무 절차와 도메인 규칙을 담는다. 예를 들어 "주간 보고서 작성", "릴리즈 노트 생성", "보안 점검", "코드 리뷰 절차" 같은 것은 Skill로 만드는 편이 훨씬 효율적이다. 이 계층은 사람이 자주 잊는 규칙, 예외 처리, 템플릿, 체크리스트를 담아둔다.

### 2.3 통제층 (Control Layer)

Hooks, permission mode, allowlist, CI eval, Inspector, logging, tracing이 이 층에 해당한다. 이 계층은 에이전트가 잘못된 행동을 하기 전에 막거나, 잘못했을 때 추적 가능하게 만든다. 특히 "실행 전 차단"보다 "작업 완료 시 검증"이 사용자 경험에 유리한 경우가 많다. 최근 실무 가이드도 과도한 중간 차단보다 최종 검증형 훅을 선호한다.

### 2.4 구조 요약

- **MCP 서버**: 사내 DB, GitHub, 문서, 이슈 트래커, 웹 검색 등 외부 시스템 연결
- **Skills**: 반복되는 절차, 체크리스트, 도메인 규칙, 산출물 템플릿
- **Hooks**: 승인, 검사, 포맷 검증, 금지 명령 차단 같은 결정론적 규칙
- **CI/Eval**: Inspector, 골든셋, 회귀 테스트, 성능/정확도 측정
- **Observability**: Langfuse + OpenTelemetry tracing

평가/관측은 Langfuse와 OpenTelemetry 계열을 붙여, 세션·툴 호출·응답 품질·비용을 추적한다.

---

## 3. MCP 사양 및 전송 방식 (사양 현황, transport, SDK/FastMCP)

### 3.1 MCP 사양 현황 (2025~2026)

MCP는 날짜 기반 버저닝을 쓴다. 주요 리비전:

- **2024-11-05**: 초기 stable. client-server 모델, tools/resources/prompts primitive 확립.
- **2025-03-26**: Streamable HTTP transport 도입, OAuth 2.1 authorization, **HTTP+SSE deprecated**.
- **2025-06-18**: structured tool output, elicitation(서버가 사용자에게 추가 입력 요청), resource links, OAuth Resource Server 분류, RFC 8707 Resource Indicators, JSON-RPC 배칭 제거.
- **2025-11-25 (최신 stable)**: OpenID Connect Discovery, tools/resources/prompts용 icons(SEP-973), incremental scope consent(SEP-835), URL mode elicitation(SEP-1036), sampling에 tool calling(SEP-1577), OAuth Client ID Metadata Documents(CIMD, SEP-991), experimental Tasks.
- **2026-07-28 RC**: stateless core, MCP Apps, Tasks를 확장으로 이동, 공식 deprecation 라이프사이클 정책. 이 RC에서 Roots/Sampling/Logging이 deprecated 예정으로 표시됨(신규 구현은 tool parameters·direct provider API·stderr/OpenTelemetry 사용 권장). Streamable HTTP는 Mcp-Method·Mcp-Name 헤더 요구(SEP-2243), list/resource 결과에 ttlMs·cacheScope(SEP-2549) 추가 ([MCP spec version timeline](https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html)).

**Primitive 구성**: Tools(모델이 호출하는 함수, name+description+JSON Schema; 2025-06-18부터 structured output·resource link 선언 가능), Resources(URI로 식별되는 읽기 컨텍스트), Prompts(재사용 템플릿). 클라이언트가 서버에 제공하는 역량: Sampling(서버가 클라이언트 모델에 생성 요청), Elicitation(2025-06-18 신규), Roots(작업 가능 디렉터리/URI 통지).

### 3.2 Transport

사양이 정의하는 live 옵션은 stdio(로컬 서브프로세스, stdin/stdout newline-delimited JSON-RPC)와 Streamable HTTP(원격, 단일 엔드포인트 /mcp, 필요 시 SSE 스트림 업그레이드; HTTP/1.1 chunked로 동작, HTTP/2 불필요) 두 가지뿐이다. 구형 HTTP+SSE(2024-11-05, POST/GET 두 엔드포인트)는 2025-03-26에 deprecated, 2026-07-28 RC에서 정식 Deprecated 라이프사이클로 분류되어 향후 제거 대상. TypeScript SDK 1.10.0(2025-04-17)이 Streamable HTTP를 최초 지원 ([AgentCat](https://agentcat.com/guides/comparing-stdio-sse-streamablehttp/)). stdio는 동시 부하에 취약(한 테스트에서 20 동시연결 중 22요청 중 20 실패 보고).

### 3.3 MCP 개발 SDK / FastMCP

- 공식 SDK는 전 주요 언어에 존재(Python, TypeScript 등). **FastMCP 1.0은 2024년 공식 MCP Python SDK에 통합**되었다. 독립 프로젝트 FastMCP(현재 PrefectHQ 유지)는 자체 주장으로 하루 100만+ 다운로드, 전 언어 MCP 서버의 약 70%를 구동한다고 함(1차 검증 불가 — 벤더 주장, [GitHub — PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp)).
- **중요 구분**: 공식 SDK 내장 `mcp.server.fastmcp.FastMCP`(FastMCP 1.0 계열, `lifespan` 파라미터 사용, `dependencies` 파라미터 **없음**)와 별도 프로젝트 FastMCP 2.0(jlowin/PrefectHQ)은 다르다. 공식 SDK는 **Python ≥3.10 필수**(3.7~3.9 설치 실패). 2025-11-11 감사 기준 공식 SDK 버전 1.21.0, 프로토콜 2025-06-18 지원.
- TypeScript 진영: 공식 modelcontextprotocol/typescript-sdk(스펙 동기), punkpeye/fastmcp(고수준 프레임워크), @prefecthq/fastmcp-ts(FastMCP TS 공식 카운터파트). FastAPI-MCP(기존 FastAPI 앱을 브리지)도 옵션.

---

## 4. Anthropic 툴 작성 가이드 (5원칙 + Advanced Tool Use)

"Writing effective tools for agents — with agents"(2025-09-11)의 5대 원칙:

1. **올바른 툴 선택**: API를 얇게 래핑하지 말 것. `list_contacts` 대신 `search_contacts`. 여러 API 호출을 하나로 합친 고레버리지 툴(`schedule_event`, `get_customer_context`)을 소수만 구현. 툴이 많거나 겹치면 에이전트가 혼란 ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).
2. **네임스페이싱**: 서비스·리소스별 prefix(`asana_search`, `asana_projects_search`). prefix vs suffix는 LLM별로 효과가 달라 eval로 결정 ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).
3. **의미 있는 컨텍스트 반환**: `uuid`·`mime_type` 같은 저수준 식별자 대신 `name`·`file_type`. UUID를 의미 있는 언어/0-index로 해석하면 환각 감소·검색 정밀도 향상. `response_format` enum(`concise`/`detailed`)으로 verbosity 제어(예시: detailed 206토큰 vs concise 72토큰, ~⅓) ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).
4. **토큰 효율**: 페이지네이션·range·필터·truncation을 기본값과 함께. Claude Code는 툴 응답을 **기본 25,000 토큰**으로 제한. 에러 메시지도 "무엇을 고쳐야 하는지" 프롬프트 엔지니어링(불투명한 traceback 금지) ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).
5. **툴 description 프롬프트 엔지니어링**: 신입에게 설명하듯 암묵지를 명시화. `user` 대신 `user_id`. Claude Sonnet 3.5가 SWE-bench Verified에서 description 정밀 개선만으로 SOTA 달성 ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).

**평가 방법론(가이드 원문)**: 실제 워크플로우 기반 태스크 수십 개 생성(단순 sandbox 금지, 여러 툴 호출 요구) → 각 태스크에 검증 가능한 응답 페어링 → 단순 while-loop 에이전트로 프로그래매틱 실행 → reasoning/feedback 블록을 tool call 앞에 출력 유도(CoT) → transcript·tool-call 메트릭(런타임, 호출 수, 토큰, 에러) 분석 → Claude Code로 transcript 붙여넣어 툴 자동 리팩터. Held-out test set으로 오버핏 방지(그래프 캡션: "Held-out test set performance ... human-written vs Claude-optimized Slack MCP tools").

### 4.1 Code execution with MCP (2025-11-04)

툴 정의를 전부 컨텍스트에 올리고 중간 결과를 컨텍스트로 통과시키는 기존 방식의 토큰 낭비를 해결. MCP 툴을 코드 API(파일)로 노출하고 모델이 코드를 작성해 호출 → progressive tool discovery, 중간 데이터가 모델을 안 거침(민감정보 un-tokenize 패턴). 단, Anthropic은 개념만 제시하고 **구현 코드는 미제공**(샌드박스 보안 부담을 팀에 전가) ([Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp)).

### 4.2 Introducing advanced tool use (2025-11-24, Opus 4.5 동시 발표)

Tool Search Tool 활성화 시 대형 툴 라이브러리 MCP eval 정확도가 **Opus 4 49%→74%, Opus 4.5 79.5%→88.1%**로 향상. Anthropic 측정에서 5개 서버(약 58 tools) 셋업 시 툴 정의가 약 55,000 토큰을 소비하며, `defer_loading: true` 적용 시 ~134k→~5k로 **약 85% 토큰 절감**(on-demand 툴 발견). description 개선만으로 "40% task completion time 감소" 사례도 보고 ([Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)).

---

## 5. MCP 품질 검증 (Inspector, mcp-eval, mcp-compliance, 계약 테스트)

### 5.1 MCP Inspector (공식)

`npx @modelcontextprotocol/inspector`: Node.js ^22.7.5 필요, UI 기본 localhost:6274, proxy 6277, 기본 세션 토큰 인증. Tools 탭에서 스키마·description·실행 결과·raw JSON-RPC 확인. CLI 모드로 CI 자동화 가능(`--method tools/list`), exit code로 pass/fail ([Augment Code](https://www.augmentcode.com/mcp/mcp-inspector)).

**첫 관문**: Inspector가 연결/툴 나열 못 하면 에이전트도 못 한다. 주의: stdout에 비-JSON 출력(print/log)이 섞이면 stdio JSON-RPC 파서가 깨진다 → 로깅은 stderr로.

### 5.2 mcp-eval / mcp-agent (lastmile-ai, docs.mcp-agent.com)

어서션 API 4범주:

- **정확성**: `Expect.content.contains`, `Expect.tools.output_matches`
- **툴 사용**: `Expect.tools.was_called`, `Expect.tools.sequence`, `Expect.tools.was_called_with`
- **성능**: `Expect.performance.response_time_under`, `Expect.performance.max_iterations`
- **품질**: `Expect.judge.llm`, `Expect.judge.multi_criteria`
- **경로 효율**: `Expect.path.efficiency(expected_tool_sequence, allow_extra_steps, tool_usage_limits)`

`@task` 데코레이터, `mcpeval.yaml` 필수, OpenTelemetry `.jsonl` 트레이스 출력, `mcp-eval generate`로 테스트 자동 생성 ([Medium — Three-layer test pyramid for MCP](https://medium.com/@anil.goyal0057/the-complete-guide-to-testing-mcp-server-applications-a-three-layer-test-pyramid-for-ai-powered-027e941be6d4)).

### 5.3 mcp-compliance (YawLabs)

8개 카테고리 88개 테스트, A-F 등급, 버전된 JSON 리포트(schemaVersion, specVersion) ([GitHub — YawLabs/mcp-compliance](https://github.com/YawLabs/mcp-compliance)).

### 5.4 계약 테스트 원칙

각 툴을 API 계약으로 취급 → 스키마 드리프트·레이턴시·derived content 회귀 감지. In-memory 유닛 테스트(FastMCP Client / TS InMemoryTransport, 서브초 피드백) → 스키마 validation(CI에서 계약 드리프트 차단) → Inspector conformance 순으로 계층화. 복잡 스키마의 `$ref`/anyOf는 일부 클라이언트가 취약하므로 Inspector로 실제 노출 스키마 확인.

### 5.5 mcp-eval 테스트 케이스 예제

```python
from mcp_eval import Expect, task

@task("search_customers finds a known customer")
async def test_search(agent, session):
    response = await agent.generate_str(
        "Find the customer with email jane@acme.corp and summarize their status."
    )
    await session.assert_that(Expect.tools.was_called("search_customers"))
    await session.assert_that(
        Expect.tools.was_called_with("search_customers", {"query": "jane@acme.corp"})
    )
    await session.assert_that(Expect.content.contains("acme", case_sensitive=False),
                              response=response)
    await session.assert_that(Expect.performance.response_time_under(5000))
    await session.assert_that(
        Expect.path.efficiency(expected_tool_sequence=["search_customers"],
                               allow_extra_steps=1,
                               tool_usage_limits={"search_customers": 1})
    )
    await session.assert_that(
        Expect.judge.llm("Summary should reflect the customer's current status",
                         min_score=0.8),
        response=response,
    )
```

---

## 6. MCP 보안 (사양 필수 통제 + 실제 사고/CVE)

### 6.1 사양 필수 통제

(2025-06-18 = 2025-11-25 동일 문구, `security_best_practices` + `authorization`):

- **토큰 패스스루 금지**: "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server." "MCP clients MUST NOT send tokens to the MCP server other than ones issued by the MCP server's authorization server." ([MCP spec security best practices](https://github.com/johnzfitch/claude-wiki/blob/master/06-MCP-Tools/General/mcp-specification-2025-11-25-basic-security-best-practices.md))
- **RFC 8707 Resource Indicators**: "MCP clients MUST implement Resource Indicators for OAuth 2.0 ... resource 파라미터는 authorization·token 요청 모두에 포함, MCP 서버의 canonical URI 사용." "MCP servers MUST validate that access tokens were issued specifically for them as the intended audience." 유효하지 않은/만료 토큰은 HTTP 401 ([MCP authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization)).
- **세션**: "MCP servers MUST NOT use sessions for authentication", "MUST use secure, non-deterministic session IDs"(UUID·secure RNG), "SHOULD bind session IDs to user-specific information"(`<user_id>:<session_id>` — ID를 추측당해도 타 사용자 가장 불가).
- **로컬 서버 원클릭 설정**: "MUST implement proper consent mechanisms prior to executing commands" — 실행 명령 전체를 truncation 없이 표시, 위험 작업(sudo, rm -rf) 경고, 명시적 승인, stdio로 접근 제한.
- **Confused deputy(proxy 서버)**: "MUST implement per-client consent" — 사용자별 승인 `client_id` 레지스트리를 3rd-party 인증 흐름 개시 **전에** 확인, redirect_uri 정확 문자열 일치(와일드카드 금지), state 파라미터(암호학적 랜덤, 단회용, 10분 만료, consent 승인 후에만 쿠키 설정), `__Host-` 접두 + Secure/HttpOnly/SameSite=Lax 쿠키.
- **스코프 최소화**(2025-11-25): 최소 초기 스코프(예: `mcp:tools-basic`) + WWW-Authenticate scope 챌린지로 증분 상승. 와일드카드/omnibus 스코프(`*`, `all`, `full-access`) 금지.

### 6.2 실제 사고/연구

- **mcp-remote CVE-2025-6514**: JFrog Security Research(Or Peles) 2025-07-09 공개, CVSS 9.6 OS 커맨드 인젝션, v0.0.5–0.1.15 영향·v0.1.16 수정, 437,000+ 다운로드. "the first time that full remote code execution is achieved in a real-world scenario on the client operating system when connecting to an untrusted remote MCP server"(JFrog).
- **Cursor CVE-2025-54136(MCPoison)·CVE-2025-54135(CurXecute)**: config swap/rug pull — 승인된 key name을 신뢰하고 command content를 재검증하지 않는 허점.
- **Postmark MCP 백도어**(2025-09): 유지관리자가 공식 패키지에 BCC 로직 추가로 전 메일 탈취(패키지 서명이 행위를 보증하지 못함).
- **arXiv:2508.12538 "Systematic Analysis of MCP Security"**(Guo, Liu, Ma, Deng, Zhu, Di, Xiao, Wen): 배포된 1,800+ MCP 서버를 조사해 "over 30 percent had at least one exploitable vulnerability".
- **MCPTox 벤치(arXiv:2508.14925, Wang et al., AAAI 2026)**: 45개 실제 MCP 서버·353개 authentic tools·1,312개 악성 테스트케이스. 최고 공격성공률 **o1-mini 72.8%**이며 "more capable models are often more susceptible"(강한 모델이 오히려 더 취약). 최강 방어 모델 **Claude-3.7-Sonnet조차 거부율 3% 미만** — "모델이 알아서 걸러줄 것"이라는 가정은 성립하지 않음.
- **스캐너 노이즈 주의**: YARA 기반 MCP 스캐너에서 ~78% false positive 보고(AppSec Santa) — 원시 "X% 취약" 수치는 방법론 편차 큼.
- **rug pull 완화 연구**: ETDI(서명된 JWT에 툴 정의 바인딩, 정의 변경 시 서명 무효화) 제안.

---

## 7. Claude Agent Skills (포맷, progressive disclosure, 선택 기준)

### 7.1 포맷

skill 폴더 안 `SKILL.md`(YAML frontmatter + Markdown body). 필수 frontmatter는 `name`, `description` **두 개뿐**. 선택: `allowed-tools`, `license`, 모델 오버라이드 ([Hidekazu-konishi — Claude Code Skills guide](https://hidekazu-konishi.com/entry/claude_code_skills_complete_guide.html)). 선택 디렉터리 `scripts/`(실행 Python/Bash), `references/`(필요시 로드 문서), `assets/`(템플릿/폰트) ([Lee Hanchung — Claude Skills deep dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)).

### 7.2 Progressive disclosure 3단계

1. frontmatter name+description만 시작 시 로드(스킬당 ~60~100 토큰)
2. 관련 판단/명시 호출 시 SKILL.md body 로드(권장 <5,000 토큰 / <500줄)
3. 참조 파일은 실제 필요 시에만

8개 스킬 예시: 전부 로드 시 ~70,000 토큰 → progressive로 시작 ~500 토큰, 임의 시점 ~2,000 토큰(70-90% 절감) ([Anthropic — Complete Guide to Building Skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)).

### 7.3 배포 경로

개인 `~/.claude/skills/`, 프로젝트 `.claude/skills/`, plugin 제공, built-in. Agent Skills 오픈 표준(agentskills.io, 2025-12-18 발표)은 Claude, OpenAI Codex, Gemini CLI, Cursor, VS Code 등 26+ 플랫폼 채택 → 이식성 확보 ([Lee Hanchung — Claude Skills deep dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)).

### 7.4 description이 트리거 정확도의 핵심

"무엇을 하는지 + 언제 쓰는지" 둘 다 명시. description이 모호하면 스킬이 자동 발화하지 않아 매번 명시 호출해야 하는 실패가 흔하다. Claude 모델은 SKILL.md 포맷을 네이티브 이해하므로 "스킬 작성 스킬" 없이도 생성 가능.

---

## 8. 역할 분담: MCP / Skills / Hooks / Plugins / Subagents

### 8.1 MCP

MCP는 외부 시스템 접근 계층이다. 데이터 조회, 작업 생성, 메시지 전송, 문서 검색처럼 **실제로 호출되어야 하는 기능**은 MCP가 맡는다. MCP 서버는 가능한 한 작고 명확해야 하며, search/get/create/update 같은 명확한 동사형 툴이 좋다. 세션 시작 시 툴 정의가 시스템 프롬프트에 로드되어 컨텍스트 소비 ([Substack — Choosing between skills/subagents](https://smithhorngroup.substack.com/p/choosing-between-skills-subagents), [Obot AI — MCP Anthropic](https://obot.ai/resources/learning-center/mcp-anthropic/)).

### 8.2 Skills

지식/절차(체크리스트, 하우스 스타일, 반복 워크플로우, 번들 스크립트). auto-detection 가치가 큰 **대형 도메인 지식**에 적합. progressive disclosure로 70-90% 토큰 절감 ([Substack — Choosing between skills/subagents](https://smithhorngroup.substack.com/p/choosing-between-skills-subagents)). "언제 이 작업을 써야 하는가", "어떤 순서로 처리해야 하는가", "무엇을 출력해야 하는가"를 정의한다.

### 8.3 Hooks

사내 정책을 강제한다. 포맷 검사, 금지 명령 차단, 경고 출력, 승인 요청, 커밋 전 검증을 자동화할 수 있다. "언제나 적용되어야 하는 규칙"에 적합 (자세한 구현은 §14·§16·§24 참조).

### 8.4 Plugins

배포 단위다. 여러 Skills, Hooks, MCP 서버를 한 묶음으로 패키징해 팀 단위로 배포할 수 있다. plugin은 역량 단위가 아니라 배포 단위 — "plugin vs skill"은 갈림길이 아니다. 온보딩과 롤백이 쉬워서 내부 표준 배포에 잘 맞는다.

### 8.5 Subagents

격리된 컨텍스트 창의 병렬 워커(긴 코드리뷰, 깊은 리서치, 컨텍스트 오염 방지). 각자 컨텍스트·토큰 독립 소비(과다 병렬 시 사용량 급증). 설계, 구현, 검증, 문서화를 별도 에이전트로 분리할 수 있다.

### 8.6 Slash command

사용자가 통제하는 명시적 트리거(`/name`). 서브에이전트/스킬을 파이프라인으로 호출 가능.

### 8.7 흔한 실수

- 커밋 메시지 포맷을 Skill로 (→ CLAUDE.md)
- 배포 체크리스트를 Skill로 (→ slash command)
- GitHub 접근을 Skill에 기대 (→ MCP)

### 8.8 Gemini CLI 매핑

GEMINI.md(컨텍스트=CLAUDE.md), extensions(패키징=plugin), custom commands(=slash), skills/(SKILL.md 동일 표준), sub-agents(preview).

---

## 9. 워크플로우 아키텍처 패턴 (5가지 패턴)

Anthropic "Building Effective Agents"(2024-12) 핵심: **워크플로우**(LLM·툴이 사전 정의된 코드 경로로 오케스트레이션) vs **에이전트**(LLM이 자기 프로세스·툴 사용을 동적 지휘). "가장 단순한 해법부터, 필요할 때만 복잡도 추가" — 에이전트 시스템을 아예 안 만드는 것도 선택지(에이전트는 latency·비용을 정확도와 맞바꿈). 프레임워크는 프롬프트를 가리고 과설계를 유발하므로 **direct LLM API부터** 권장 ([Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

워크플로우 패턴과 사용 시점:

1. **Prompt chaining**: 각 LLM 호출이 앞 출력을 처리. 결정론적 순차 태스크.
2. **Routing**: 입력 분류 → 전문 후속 태스크. 고객 문의 등 입력 카테고리가 뚜렷할 때.
3. **Parallelization**: sectioning(독립 서브태스크 병렬)·voting(동일 태스크 다회 실행 후 집계). 속도·다관점 신뢰도.
4. **Orchestrator-workers**: 중앙 LLM이 동적 분해·위임·종합. 서브태스크를 예측 불가한 멀티파일 코딩/리서치.
5. **Evaluator-optimizer**: 생성-평가 피드백 루프.

Agent Skills는 별개 축(범용 에이전트 위 도메인 전문성을 on-demand 로드) — 워크플로우 우선 규율을 대체하지 않고 보완.

---

## 10. 에이전트 프레임워크 비교 (LangGraph, Claude Agent SDK 등)

| 프레임워크 | 아키텍처 | 내구성/상태 | HITL | 사내 배포 적합성 | 비고 |
|---|---|---|---|---|---|
| **LangGraph** | 그래프(명시적 state) | durable checkpointing, resume, time-travel | 일급 interrupt | 규제/승인 많은 장기 워크플로우 1순위 | 모델 무관, 가장 많은 프로덕션 마일리지(Klarna/Uber/LinkedIn) |
| **Claude Agent SDK** | Claude Code 엔진(배터리 포함) | 내장 상태 persistence 없음(직접 관리) | 권한 프롬프트/hooks | "repo/filesystem에서 일하는 Claude"에 최적 | MCP 통합 최심, TS/Python 패키지 |
| **OpenAI Agents SDK** | handoff 체인 | 상태 persistence 없음(직접) | harness 승인/resume 트레이싱 | OpenAI 스택 팀 | 2026-04 sandbox 실행 추가, 경량 |
| **Google ADK** | A2A 프로토콜 | — | — | GCP/Vertex 팀 | 1.0(Java/Go) |
| **Microsoft Agent Framework** | SK+AutoGen 통합 | — | — | Azure/.NET 팀 | 1.0 GA 2026-04-03 |
| **CrewAI** | role-based crew | 상대적 약함 | — | 빠른 프로토타입(→프로덕션은 LangGraph 재구현 흔함) | MCP 네이티브(`crewai-tools[mcp]`) |
| **Temporal** | durable execution 엔진 | 최강 내구·재시도·재생 | 워크플로우 신호 | 장기·fault-tolerant 자동화의 신뢰성 척추 | 에이전트 프레임워크와 병용 |

**권고**: 3단계 워크플로우 자동화에서 **결정론적 장기 승인 흐름은 LangGraph 또는 Temporal**, **코드/파일 조작형은 Claude Agent SDK**. 모든 주요 프레임워크가 2025-2026에 MCP를 툴 통합 표준으로 수렴 → MCP 툴은 프레임워크 간 이식 가능. 단순 분류/추출/2-툴 조회는 프레임워크 없이 단일 API 호출로 충분(하네스는 오버헤드).

---

## 11. 평가·운영 안정성 (방법론, 비결정성, 회귀 게이트, 관측)

### 11.1 평가 방법론

골든 데이터셋(≥30 케이스 회귀셋), task success rate, tool-call accuracy(정확한 툴 선택+파라미터), trajectory evaluation, LLM-as-judge(한계: judge 자체가 비결정적·"stably wrong" 가능). **3계층 전략**:

- deterministic 로직(라우팅·파싱·상태전이)은 매 커밋 유닛테스트(`pytest -m "not llm_eval"`)
- 품질 차원(faithfulness/relevance/coherence/hallucination 0.0~1.0 임계)은 eval 테스트
- 전체 태스크는 online eval

### 11.2 비결정성 다루기

judge temperature=0, pass/fail 기준 최대한 구체화(무엇이 pass인지 나열), 각 케이스 3회 실행 majority-vote, 동일 케이스가 10%+ 뒤집히면 기준 재작성. **pass^k/pass@k**로 "k회 중 1회 이상 성공 확률" 통계 판정 ([arXiv — pass^k](https://arxiv.org/pdf/2404.05520)). **UNSTABLE을 CI 실패 상태로 취급**(단일 pass rate 대신 agreement 보고 — "95% pass at 0.6 judge agreement is noise"). judge·agent 모델 버전 pinning. 3-of-5 flip을 60% pass로 평균내면 회귀가 숨는다.

### 11.3 회귀 게이트

골든셋 key metric ±3% 임계 초과 시 빌드 실패(비협상 품질 게이트), canary 5% 트래픽 + online eval을 control과 비교, eval delta 통계 유의성(노이즈 초과) 확인 후에만 100% 승격. no-LLM 결정론적 replay를 CI 1차 게이트로(빠르고 저렴).

### 11.4 관측

OpenTelemetry GenAI semantic conventions(`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens/output_tokens`; `invoke_agent`/`execute_tool`/model/workflow 스팬 + latency·token 메트릭). **단 v1.41 기준 대부분 `gen_ai.*` 속성이 Development 안정성 badge** — 속성명이 major bump 없이 바뀔 수 있으므로 semantic convention 버전 pinning 필수. OpenInference(tool_call 상관 속성) 병용. OpenLLMetry 등 auto-instrumentation으로 LLM 클라이언트 스팬 즉시 확보 → 에이전트/툴 스팬 수동 추가 ([MLflow — LLM observability pipelines 2026](https://mlflow.org/articles/setting-up-llm-observability-pipelines-in-2026/)).

### 11.5 실패 복구

재시도(idempotent 보장), timeout, guardrail(입력/출력 스크리닝), fallback 모델, circuit breaker, 사용자에게 정직한 실패 통지(성공으로 위장 금지 — 에이전트는 "well-formed but wrong"으로 실패).

### 11.6 배포 후 수정 어려움 대응

feature flag, remote config(프롬프트·모델 버전 원격 전환), canary 단계적 롤아웃, 버전 호환성 유지.

---

## 12. Eval/Observability 셀프호스팅 (폐쇄망)

| 도구 | 셀프호스팅 | 라이선스/비용 | 강점 | 폐쇄망 주의점 |
|---|---|---|---|---|
| **Langfuse** | ✅ Docker/K8s | 오픈소스 MIT, 무료 | 트레이싱·세션 리플레이·프롬프트 관리·비용 추적, 전 프레임워크 통합 | FOSS는 SOC2/ISO 미포함, SSO·고급 RBAC은 유료 키. ClickHouse/Redis/PostgreSQL/S3 운영 부담. eval 워크플로우는 상대적 약함 |
| **Arize Phoenix** | ✅ | 오픈소스(Elastic License 2.0), 무료 | OpenInference/OTel 네이티브, Phoenix Evals, notebook 친화 | 유료는 Arize AX(~$50/월~), 전사 UX는 span-tree 중심 |
| **Braintrust** | ✅(엔터프라이즈) | proprietary, 관대한 무료 티어(1M spans/월) | eval-gated CI/CD 최강, 회귀 감지, 릴리스 통제 연결 | 셀프호스팅은 엔터프라이즈 계약 |
| **DeepEval** | ✅(로컬) | 오픈소스 | Python 로컬 eval, CI 적합 | 관측보다 eval 중심 |
| **LangSmith** | 제한적 | proprietary, 볼륨 과금 | LangChain/LangGraph 통합 최강 | 외부 SaaS 전송, 폐쇄망 부적합 |
| **Promptfoo / Ragas** | ✅ | 오픈소스 | 프롬프트/RAG eval | 보조 도구 |

**폐쇄망 1순위 권고: Langfuse(트레이싱·비용·프롬프트 버전) + DeepEval/mcp-eval(CI eval) + OpenTelemetry 계측.** Langfuse는 2026년 1월 16일 ClickHouse가 $400M Series D(밸류 $15B)와 동시에 인수 발표했으나 공동창업자 Max Deichmann이 "Langfuse stays open source and self-hostable"라 확인(MIT 유지, 2025년 말 기준 GitHub 20K+ stars, 월 26M+ SDK installs) ([Langfuse — self-hosting observability](https://langfuse.com/self-hosting/configuration/observability), [Langfuse — OTel integration](https://langfuse.com/integrations/native/opentelemetry)). "best" 순위 상당수가 벤더 블로그(Latitude/Braintrust)이므로 자체 PoC 검증 필수.

---

## 13. 사내 배포 및 거버넌스 (플러그인 마켓플레이스, 거버넌스 원칙, 채택)

### 13.1 Claude Code 플러그인/마켓플레이스

plugin = 배포 단위(skills+agents+hooks+MCP servers+LSP 번들, `.claude-plugin/plugin.json`), marketplace = 카탈로그(repo의 `.claude-plugin/marketplace.json`). 팀 배포는 프로젝트 `.claude/settings.json`의 `extraKnownMarketplaces`+`enabledPlugins` → 팀원이 repo 신뢰 시 자동 설치 프롬프트 ([Agent Wikis — plugin marketplaces](https://agentwikis.com/wiki/claude-code/wiki/entities/plugin-marketplaces.md)). plugin은 MCP 서버를 `.mcp.json`(plugin 루트)로 선언해 자동 기동. `claude plugin details <name>`로 always-on/per-invoke 토큰 비용 사전 확인. **plugin은 사용자 권한으로 임의 코드 실행 → 신뢰 소스만.** managed 스코프는 불변(admin 설치). Anthropic은 3rd-party plugin 내용을 검증하지 않음.

### 13.2 거버넌스

**리스크 비례 원칙**(저위험 내부 실험은 며칠 내 승인, 후보 심사자·크리덴셜 접근·파괴적 작업은 심층 심사). MCP 레지스트리/게이트웨이로 등록·승인된 툴만 프로덕션 실행. 감사로그(워크플로우 버전·사용자 액션·툴 호출) ([Obot AI — AI governance trends 2026](https://obot.ai/blog/ai-governance-trends-2026/)). 리뷰 프로세스: 툴 정의 서명·해시 고정(rug pull 방지), allowlist ([Stackai — enterprise AI adoption 2026](https://www.stackai.com/insights/enterprise-ai-adoption-2026-trends-benchmarks-and-best-practices-for-scalable-success)). ISO/IEC 42001, NIST AI RMF(GOVERN/MAP/MEASURE/MANAGE), EU AI Act(일반 조항 2026-08-02 적용) ([Hymalaia — enterprise AI governance 2026](https://www.hymalaia.com/blog/enterprise-ai-governance-best-practices-for-2026-en)) 참조. IBM: 87% 기업이 "명확한 거버넌스" 주장하나 25% 미만만 실제 통제 구현 — 문서가 아닌 실행 규율이 관건.

### 13.3 채택률

프로젝트 스코프 plugin으로 팀 전원 동일 툴 자동 확보, 온보딩 문서/사용 가이드, 미승인 툴 사용 급증은 "처벌"이 아니라 "정식 도입 검토 신호"로 해석.

### 13.4 managed 설정

`managed-settings.json` + `managed-mcp.json`으로 IT 강제 정책(예: `Bash(curl *)` deny — 어떤 하위 스코프도 오버라이드 불가). `strictKnownMarketplaces`(마켓플레이스 allowlist), `allowManagedHooksOnly`, `disableAllHooks`로 공급망 통제. MCP 출력은 `MAX_MCP_OUTPUT_TOKENS`(기본 25,000)로 제어. 설정 정밀도: **managed > project > user > local** ([Anthropic — writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)).

---

## 14. 컨텍스트 엔지니어링 (AGENTS.md, 파일 메모리, llms.txt)

### 14.1 AGENTS.md 단일 소스 전략 **[Quick Win #1]**

3사 CLI가 각자 다른 컨텍스트 파일을 읽는 파편화를 AGENTS.md 하나로 수렴. 2025년 12월 Linux Foundation이 OpenAI, Anthropic, Block을 창립 멤버로 Agentic AI Foundation(AAIF)을 결성했다. Anthropic은 MCP를, OpenAI는 AGENTS.md를 기증했으며, AGENTS.md는 60,000개 이상의 오픈소스 repo와 에이전트 프레임워크(Codex, Cursor, Devin, Factory, Gemini CLI, GitHub Copilot, Jules, VS Code, Amp)에 채택되었다. 2026년의 정직한 기본값은 AGENTS.md로 시작하고, 실제 스코핑 한계에 부딪힐 때만 Cursor MDC rules를 추가하고, 팀이 Claude Code로 표준화한 경우에만 CLAUDE.md를 추가하는 것이다.

```
repo/
├── AGENTS.md              # ← 정본. 프로젝트 개요, 빌드/테스트 명령, 코드 스타일
├── CLAUDE.md              # @AGENTS.md + Claude 전용 항목만
├── GEMINI.md              # AGENTS.md 내용 참조 + Gemini 전용
└── packages/
    └── mcp-gen/AGENTS.md  # 서브프로젝트별 오버라이드
```

```markdown
<!-- CLAUDE.md -->
@AGENTS.md

## Claude Code 전용
- 서브에이전트는 model: haiku 사용
- .claude/hooks/ 의 가드를 우회하지 말 것
```

**AGENTS.md에 넣을 것**: 필수 필드는 없고 스펙은 "에이전트를 위한 README"라고 설명한다. 대부분의 repo가 쓰는 순서는: 프로젝트 개요(무엇인지, 주 언어·프레임워크와 버전), 빌드·테스트 명령(모호한 도구명이 아니라 플래그까지 포함한 정확한 명령), 코드 스타일 가이드라인(언어 기본값과 다른 규칙만).

- ✅ 정확한 명령어 (`uv run pytest -m "not integration"`, 플래그 포함)
- ✅ 언어 기본값과 **다른** 규칙만
- ✅ 하지 말아야 할 것 (금지 경로, 금지 패턴)
- ❌ 언어 기본 스타일 재설명, 일반론, 장문의 아키텍처 서사

**모노레포**: 각 패키지에 AGENTS.md를 둔다. 에이전트는 편집 중인 파일에 가장 가까운 파일을 읽는다. OpenAI의 Codex 저장소는 디렉터리 트리 전반에 88개의 AGENTS.md를 사용한다.

**리스크**: NVIDIA가 간접 AGENTS.md 인젝션 공격 완화를 다룬 기술 블로그를 낸 바 있다. → **외부에서 받은 repo의 AGENTS.md를 무비판 신뢰 금지**. 사내 규칙: 외부 repo 작업 시 AGENTS.md를 사람이 먼저 읽는다.

**참고**: Claude Code는 이제 AGENTS.md도 읽으며 CLAUDE.md가 우선한다(⚠️ 2026-06 커뮤니티 출처, 버전에 따라 동작 상이 가능 — 실제 환경에서 확인 필요). 어느 쪽이든 CLAUDE.md에서 `@AGENTS.md` import하는 방식은 안전하게 동작.

### 14.2 파일 기반 메모리 패턴 **[Quick Win #14]**

에이전트가 중간 결과·다음 단계를 파일에 쓰고 다음 세션에서 다시 읽게 하는 패턴. 긴 세션에서 컨텍스트가 압축(compact)되면 초기 결정 근거가 소실된다. 파일은 압축되지 않는다.

```markdown
<!-- CONTINUE.md — 세션 종료 시 에이전트가 갱신 -->
## Next Session
- **Active Task:** mcp-gen-042
- **Current Focus:** search_customers 툴 스키마 확정
- **Blockers:** 사내 CRM API 페이지네이션 스펙 미확인
## Recent Changes
- FastMCP 서버 스켈레톤 생성
- mcp-eval 골든셋 12/30 작성
```

Stop hook으로 자동 갱신을 강제하면 더 안정적.

**보너스 — compact 지시문**: "## Compact Instructions — 이 대화를 요약할 때: 모든 API 변경과 근거를 보존할 것, 에러 메시지와 해법을 유지할 것, 수정된 파일 목록을 유지할 것, 탐색 시도는 간략히 요약할 것" 같은 블록을 CLAUDE.md에 넣으면 압축 손실을 통제 가능.

### 14.3 llms.txt로 사내 문서를 에이전트 친화화 **[Quick Win #15]**

사내 API 문서·SDK 레퍼런스를 에이전트가 읽기 좋은 단일 마크다운 인덱스로 제공. 1단계 MCP 생성 에이전트의 입력 품질이 곧 출력 품질. 사내 API 문서가 HTML·Confluence에 흩어져 있으면 에이전트가 추측하고, 추측은 환각이 된다. 다운로드는 허용되므로 외부 라이브러리의 llms.txt도 함께 캐시해 두면 폐쇄망에서도 최신 레퍼런스 확보.

사내 API마다 `docs/llms.txt` 생성 → MCP 생성 에이전트의 필수 입력으로 지정. 생성 에이전트 프롬프트에 "llms.txt에 없는 엔드포인트는 절대 가정하지 말고 사람에게 질문할 것" 규칙 삽입.

---

## 15. 코드 생성 품질 (Spec-first, Cross-model review, 결정론 최대화)

### 15.1 Spec-first 워크플로우 (GitHub Spec Kit) **[Quick Win #10]**

프롬프트 → 코드가 아니라, spec → plan → tasks → code. GitHub의 프레이밍에 따르면 문제는 코딩 에이전트의 능력이 아니라 접근법이다. 개발자들이 코딩 에이전트를 검색 엔진처럼 다뤄왔지만, 실제로는 패턴 인식에는 뛰어나되 명확한 지시가 필요한 문자 그대로 받아들이는 페어 프로그래머처럼 다뤄야 한다. SDD는 채팅 히스토리가 아니라 작성된 스펙을 진실의 원천으로 삼는다. Specify → Plan → Tasks → Implement 4단계 루프이며 각각이 다음 단계가 읽는 마크다운 파일이다. 기능당 토큰을 20~40% 더 쓰지만 낭비되는 사이클 감소로 상쇄된다.

```bash
uv tool install specify-cli
specify init mcp-gen-agent --integration claude   # Claude Code / Copilot / Gemini / Cursor 등 30+ 지원
# /speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
```

일부 통합에서는 `--integration <agent> --integration-options="--skills"`로 슬래시 커맨드 프롬프트 파일 대신 agent skills를 설치할 수 있다. `/speckit.tasks` 이후 `/speckit.implement` 이전에 실행하는 교차 산출물 일관성·커버리지 분석 명령과, 요구사항의 완결성·명확성·일관성을 검증하는 커스텀 품질 체크리스트 생성 명령("영어를 위한 유닛 테스트" 같은)도 있다.

**규모 참고**: 현재 90k+ stars, 8k+ forks(⚠️ 2026-05 시점 보도). 138개 커뮤니티 익스텐션(70+ 저자)과 25개 프리셋. 공식 Spec Kit 패키지는 GitHub 저장소에서 직접 배포되며, PyPI의 동명 패키지는 Spec Kit 팀이 유지하지 않으므로 설치하면 안 된다. ← **공급망 주의점**

**본 프로젝트 적용**: 툴 생성 에이전트 자체를 SDD로 만들고, 생성 에이전트가 만드는 MCP 서버도 spec.md를 먼저 산출하게 한다. spec.md가 곧 mcp-eval 골든셋의 근거가 되므로 §11 회귀 게이트와 자연 결합.

**리스크**: 소형 태스크에는 오버헤드. 프로토타입은 vibe로, 프로덕션은 SDD로.

### 15.2 Cross-model review (3사 계약을 낭비하지 않기) **[Quick Win #11]**

Claude가 생성 → Gemini CLI가 리뷰 → 불일치만 사람이 판단. 같은 모델은 같은 blind spot을 갖는다. 이미 3사 엔터프라이즈 계약을 보유하고 있으므로 **한계비용 거의 0**. §11의 LLM-as-judge 한계("judge가 stably wrong일 수 있음")를 완화하는 가장 값싼 수단.

```bash
# 1) Claude가 MCP 서버 생성
claude -p "Generate MCP server per spec.md" > out.log
# 2) Gemini가 독립 리뷰 (동일 spec.md만 주고 구현은 검토 대상으로)
gemini -p "Review the diff against spec.md. List: (a) spec 위반, (b) 보안 문제, (c) 스키마 드리프트.
추측하지 말고 근거 라인 번호를 인용할 것."
# 3) 두 결과가 불일치하는 항목만 사람 리뷰 큐로
```

**핵심 설계 원칙**: 리뷰어에게는 **spec만 주고 생성자의 논리는 주지 않는다**(앵커링 방지).

### 15.3 결정론 최대화 원칙 (Shopify Roast의 교훈)

Shopify는 구조화된 AI 워크플로우를 위한 Ruby DSL 'Roast'를 오픈소스화했으며, 그 철학은 "비결정성은 신뢰성의 적(non-determinism is the enemy of reliability)"이다.

**적용 규칙** (생성 에이전트 시스템 프롬프트에 삽입할 문장):

> 검증은 가능한 한 결정론적 수단으로 한다. 우선순위: (1) 타입체커·스키마 validation, (2) 유닛 테스트, (3) 골든 파일 비교, (4) 룰 기반 린트, (5) 최후에만 LLM judge.
> LLM judge를 쓸 때는 무엇이 pass인지 열거하고 temperature=0으로 고정한다.

동일 맥락 사례: Uber는 LangGraph 기반 Validator와 Autocover 에이전트로 21,000 개발자 시간을 절감했으며, IDE 내장 + 하이브리드(LLM + 결정론) 구조다.

### 15.4 생성 코드 자동 검증 레이어 (pre-commit)

```yaml
# .pre-commit-config.yaml — 생성 에이전트가 산출물에 항상 포함시킬 것
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks: [{id: ruff, args: [--fix]}, {id: ruff-format}]
  - repo: local
    hooks:
      - id: mcp-schema-check
        name: MCP tool schema validation
        entry: uv run python -m tools.check_schema
        language: system
        pass_filenames: false
```

PostToolUse hook(§16)과 결합하면 **에이전트가 쓴 순간 → 커밋 시점** 이중 게이트.

---

## 16. MCP 서버 운영 실전 (Gateway, 배포 채널, 개발 규칙)

> §14는 컨텍스트, §15는 코드 품질, 본 절은 MCP 서버 자체의 운영·배포·개발 규칙을 다룬다.

### 16.1 Hooks — "프롬프트로 부탁"을 "쉘로 강제"로 **[Quick Win #2, #3]**

**무엇**: Claude Code의 lifecycle 이벤트에 쉘 명령을 바인딩. 2026년 4월 기준 27개, 이후 문서에 따라 30개 내외의 hook 이벤트 존재(수치는 출처마다 다름). 실무에서 쓰는 건 사실상 5개: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `UserPromptSubmit`.

**왜(ROI)**: hook은 LLM 프롬프트가 아니라 쉘 명령이라 결정론적으로 발화한다. PostToolUse hook이 "수정된 파일에 Prettier를 돌려라"라고 하면 매번 돌아간다. 모델은 잊을 수 없고, 대화가 길어졌다고 건너뛸 수도 없다. LLM 주도 워크플로우에서 규칙을 100% 신뢰도로 강제하는 유일한 방법이다. → **CLAUDE.md에 적어둔 규칙 중 "지켜지면 좋은 것"을 "반드시 지켜지는 것"으로 승격**시키는 장치. 배포 후 회수 불가 제약에 정확히 맞는 도구.

**어떻게**:

```json
// .claude/settings.json (팀 공유) — .claude/settings.local.json은 개인용
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{ "type": "command", "command": ".claude/hooks/format.sh" }]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": ".claude/hooks/guard.sh" }]
    }],
    "SessionStart": [{
      "hooks": [{ "type": "command", "command": "cat .claude/policy.md" }]
    }]
  }
}
```

```bash
#!/usr/bin/env bash
# .claude/hooks/guard.sh — PreToolUse. exit 2 = 차단, stderr가 Claude에게 사유로 전달
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
if echo "$cmd" | grep -qE 'rm -rf /|curl .*\| *(ba)?sh|git push --force'; then
  echo "정책 위반: 파괴적/원격실행 명령은 차단됩니다. 사유를 사람에게 보고하세요." >&2
  exit 2
fi
exit 0
```

**핵심 사실**:

- 모든 hook은 stdin으로 JSON 이벤트 페이로드를 받는다. 형태는 이벤트마다 다르지만 항상 `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_response`를 포함한다. exit 0 = 통과, exit 2(PreToolUse) = 툴 호출 차단이며 stderr 출력이 Claude에게 사유로 표시된다.
- PreToolUse hook은 permission mode를 오버라이드한다. hook이 deny를 반환하면 bypassPermissions 모드에서도 툴이 차단된다. hook은 permission 설정보다 항상 더 제한적이지, 덜 제한적일 수 없다. → **거버넌스 관점에서 가장 강한 통제점**
- hook은 사용자 권한으로 실행된다. 실행 코드로 취급하라.
- 2026년 1월 Anthropic이 `async: true` 옵션을 릴리스해 백그라운드 실행이 가능하고, HTTP hook으로 로컬 스크립트 대신 웹 서버에 이벤트를 보내 팀 전체 정책을 원격 검증할 수도 있다. → **"배포 후 수정 불가" 완화책**: HTTP hook을 사내 정책 서버로 향하게 하면 배포된 에이전트의 가드레일을 원격에서 갱신 가능.

**리스크·주의점**:

- 무거운 검사(전체 테스트 스위트, 전체 린트)는 매 편집이 아니라 SessionEnd나 CI에서 돌려라. hook이 설치되지 않은 도구에 의존하면 깨진다(npx prettier는 prettier가 node_modules에 있다고 가정).
- hook은 1초 미만으로 유지하고 구체적인 matcher를 써서 무관한 툴에 발화하지 않게 하라. 네트워크 호출이나 무거운 연산이 있으면 PostToolUse나 Stop 이벤트로 옮겨라. 개수 제한은 없지만 전형적인 프로덕션 셋업은 3~5개를 돌린다. 8~10개를 넘어가면 관련 검사를 하나의 스크립트로 통합하는 걸 고려하라.
- CI에서도 같은 `.claude/settings.json`이 적용되므로 hook 스크립트와 의존성이 CI 환경에도 있어야 한다.

### 16.2 MCP Gateway 도입 판단 (⚠️ 벤더 콘텐츠 다수)

**무엇**: 여러 MCP 서버를 단일 엔드포인트 뒤로 짠택하고 인증·권한·감사를 한 곳에서.

**왜**: 파일시스템, DB, GitHub, Slack, 내부 API에 걸쳐 10개 MCP 서버를 운영하는 팀은 10개의 커넥션, 10벌의 크리덴셜, 그리고 모든 AI 클라이언트가 매 요청마다 로드하는 10개의 툴 카탈로그를 유지하게 된다. 개수가 늘면 서버별 설정, 부재한 접근 제어, 수백 개 툴 정의를 컨텍스트에 밀어 넣는 토큰 비용이 사소한 성가심을 넘어 출시의 주된 장애물이 된다.

**오픈소스 후보** (⚠️ 순위는 대부분 벤더 블로그 기준이므로 자체 PoC 필수):

| 게이트웨이 | 특징 | 비고 |
|---|---|---|
| **MCPX** (Lunar) | Tool Groups, 툴 커스터마이징, 로컬/원격 MCP 인증. 팀별로 같은 서버에서 완전히 다른 툴 부분집합만 보이게 해 과권한 에이전트 문제를 인프라 계층에서 해결 | 오픈소스판 존재 |
| **Bifrost** (Maxim AI, Go) | MCP 클라이언트이자 서버로 동작. STDIO/HTTP/SSE로 외부 툴 서버에 연결해 툴을 짠택하고 단일 /mcp로 노출. LLM 라우팅과 MCP 오케스트레이션을 단일 바이너리로 처리 | ⚠️ 자사 콘텐츠에서 자사 1위 |
| **MetaMCP** | 단일 엔드포인트로 라우팅 + BM25 툴 필터링, 활동 로그, 격리(quarantine) 보안, 웹 UI | BM25 툴 필터링이 툴 폭발에 유효 |
| **IBM ContextForge / MCPJungle / Obot / Open Edison / Microsoft MCP Gateway** | K8s 환경의 세션 인식 라우팅·라이프사이클 관리(Microsoft), 데이터 유출 방지·실행 통제(Open Edison) | 목록: e2b-dev/awesome-mcp-gateways |

**평가 기준**: 런타임·언어(Go vs Python의 요청당 오버헤드 차이), 프로토콜 범위(단순 짠택만 하는지, REST/gRPC를 MCP 툴로 변환하는지), 레이트리밋·쿼터를 툴별/테넌트별/에이전트역할별로 걸 수 있는지, 관측성 깊이(툴 호출 활동이 쿼리 가능하고 SIEM으로 내보낼 수 있는지, 아니면 아무도 검색 못 하는 로그 파일인지).

**판단 가이드**: **1단계(MCP 서버 몇 개)에서는 불필요. 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입.** 단, "게이트웨이 도입"은 되돌리기 어려운 결정이므로 §13의 `managed-mcp.json` 거버넌스로 먼저 버티고, 필요가 실증되면 도입.

### 16.3 배포 채널 3종 세트 **[Quick Win #12]**

생성 에이전트가 **항상 3가지 배포 형태를 함께 산출**하게 하면 사용자층 전체를 커버:

| 대상 | 형태 | 명령 |
|---|---|---|
| 개발자(TS) | npm + npx | `npx @corp/mcp-crm` |
| 개발자(Py) | PyPI(사내 미러) + uvx | `uvx corp-mcp-crm` |
| 비개발자 | **MCPB 번들(.mcpb)** | 더블클릭 설치 |

**MCPB 핵심**: MCP Bundle 형식(MCPB)은 이제 Model Context Protocol 프로젝트의 일부다. ZIP 아카이브에 로컬 MCP 서버와 capabilities를 기술한 manifest.json이 들어 있고, Chrome 확장(.crx)이나 VS Code 확장(.vsix)과 유사하게 단일 클릭으로 로컬 MCP 서버를 설치할 수 있다. Claude 데스크탑 앱, Claude Code, MCP for Windows 등 호환 클라이언트 전반에서 동작한다.

```bash
npm install -g @modelcontextprotocol/mcpb
mcpb init my-server     # manifest.json 생성
mcpb pack               # .mcpb 파일 생성
mcpb validate my-server.mcpb
```

사용자 입장에서 JSON 설정 파일 편집도, Python 경로 찾기도, 환경변수 디버깅도 없다. 개발자 입장에서는 낡아가는 설치 문서를 유지하는 대신 단일 파일만 제공하면 되고, 호스트 애플리케이션이 업데이트·환경변수·파라미터 설정을 처리한다.

**⚠️ 흔한 실수** (실제 사례 기반): manifest에서 `command: "npx"`를 쓰면 npm 레지스트리 네트워크 접근이 필요하고 Claude Desktop의 번들 Node.js를 쓰지 않아 MCPB 번들링의 목적을 무산시킨다. 올바른 구현은 `command: "node", args: ["${__dirname}/server/index.js"]`. → **업로드 불가/네트워크 제약 환경에서는 특히 치명적. 생성 에이전트의 MCPB 템플릿에 이 규칙을 하드코딩할 것.**

### 16.4 MCP 서버 로컬 개발 규칙 (생성 에이전트 하드 규칙)

```
[MCP 서버 생성 시 반드시 지킬 것]
1. stdout에는 JSON-RPC만. 모든 로그·print는 stderr. (stdout 오염 = 파서 붕괴)
2. 가능한 한 stateless. 상태가 필요하면 명시적으로 문서화 (worktree 병렬 실행 충돌 방지)
3. 툴 응답은 25,000 토큰 이내. 초과 시 truncate + 안내 메시지
4. 에러는 "다음에 무엇을 하라"를 포함한 문장으로. raw traceback 금지
5. 환경변수는 ${VAR} 확장으로만. 시크릿 하드코딩 금지
6. 산출물에 반드시 포함: server 코드 / .mcp.json / gemini settings.json / mcpb manifest /
   mcp-eval 골든셋 / Inspector 스모크 스크립트 / README(doctor 명령 포함)
```

---

## 17. 선도 기업 사례 (Block/Goose, Uber, Coinbase 등)

### 17.1 Block(Goose) — 사내 전사 배포의 교과서

Block이 엔지니어링 팀을 통합 구조로 재편하면서 12,000명 직원 전반의 도구와 워크플로우를 정리하는 과제가 생겼다. 처음 목표는 개발자용 에이전트였지만 채택이 늘면서 "엔지니어뿐 아니라 모두를 위한 MCP 에이전트를 어떻게 만들 것인가"라는 더 넓은 질문이 나왔다.

핵심 전략:

- **Default Distribution: Goose가 모든 Block 노트북에 자동 설치되고 자동 업데이트된다.** ← **채택률의 근본 해법. "설치하세요"가 아니라 "이미 있습니다"**
- 초기 CLI 전용이었으나 데스크탑 앱으로 재구축하고 LLM 비종속으로 만들어 OpenAI·Anthropic·Meta 등 복수 모델 제공자와 통합했으며(Databricks로 사내 호스팅), 개발자를 겨냥한 이 초기 설계 선택들이 전사 사용의 핵심 인에이블러가 되었다.
- 내부 OAuth 기반 서버 인증, **동적 MCP 서버 활성화**, Snowflake MCP를 통한 자연어→SQL, Recipe 스키마

**본 프로젝트 시사점**:

1. **LLM 비종속 설계**를 처음부터 (3사 계약 보유 = 강점)
2. **동적 MCP 서버 활성화** = 툴 폭발 대응의 사내 검증된 답
3. **Recipe(레시피) 개념**: 워크플로우를 스키마화해 공유 → 3단계 로드맵의 설계 힌트
4. 배포 형태 미정 상태라면 **자동 설치·자동 업데이트 채널 확보가 최우선 결정**

### 17.2 사내 코딩 에이전트 도입 수치 (⚠️ 2차 출처 취합, 개별 검증 권장)

Coinbase의 Forge는 머지된 PR의 5%에 도달했고 PR 사이클 타임을 150시간에서 15시간으로 줄였으며, 신규 Mux 레이어는 병렬 에이전트 플릿을 3.5배 처리량으로 돌린다. Block이 오픈소스화한 Goose를 Stripe가 Minions로 포크한 것은 공유 인프라의 가치를 입증한다. Uber는 LangGraph 기반 Validator·Autocover 에이전트로 21,000 개발자 시간을 절감했다. Abnormal AI는 백그라운드 에이전트 PR 비율 13%를 기록했고 Ramp는 50%를 넘겼다. Google의 Agent Smith는 사내에서 너무 인기가 많아 접근을 제한해야 했고 신규 프로덕션 코드의 25% 이상을 차지한다고 보고된다.

공통 아키텍처: **Slack 호출 → 격리 샌드박스 → CI 루프 → PR-ready 산출물** ← 배포 형태 미정 상태에서 참고할 수렴 패턴.

### 17.3 실패·안티패턴 (⚠️)

- Gartner는 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망한다. McKinsey는 23%의 기업만이 AI 에이전트를 스케일한다고 본다.
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과하고, 파일럿의 88%는 출시되지 못한다.(⚠️ 컨설팅사 취합 통계)
- 내부 헬프데스크가 강력한 첫 에이전트인 이유는 데이터를 소유하고 있고 실패 비용이 낮기 때문이다. ← **첫 배포 대상 선정 기준**
- 비용 사고: 한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금을 기록했고, Microsoft는 비용이 예산을 초과해 롤아웃을 공개적으로 철회했다. → §19 비용 가시화가 선택이 아닌 이유
- 가장 흔한 비용 급증 원인은 서브에이전트 팬아웃(하나의 태스크가 20개 이상의 병렬 에이전트를 스폰)과 autocompact 루프다.

### 17.4 점진적 자율성 로드맵

완전 자율성으로 시작하지 마라. 더 안전한 채택 경로는: 에이전트가 테스트를 추가하고 작은 버그를 고치게 한다 → 저위험 리팩터를 하게 한다 → 의존성 업데이트와 문서 동기화를 맡긴다 → 그 다음에야 모듈 간 기능 작업을 시도한다.

**본 프로젝트 적용**: 사내 배포 시 **툴 생성 에이전트의 자율성도 단계적으로**. 1차 배포는 "코드 초안 + 테스트를 생성하되 커밋은 사람이", 안정화 후 자동 PR.

---

## 18. 사용자 편의성 (doctor, dry-run, 피드백)

### 18.1 `doctor` 커맨드 — 온보딩 문의를 없애는 최소 투자 **[Quick Win #7]**

생성 에이전트가 만드는 모든 툴에 자가진단 명령을 기본 탑재:

```bash
$ corp-mcp-crm doctor
✔ Python 3.12.3 (>=3.10 필요)
✔ uv 0.5.11
✖ CRM_TOKEN 환경변수 없음
  → 해결: 사내 포털 > 개인 토큰 발급 후 `export CRM_TOKEN=...`
✔ CRM API 연결 (응답 142ms)
✔ Claude Code .mcp.json 등록됨
✖ Gemini CLI settings.json 미등록
  → 해결: `corp-mcp-crm install --client gemini`
```

**왜**: 사내 배포 후 발생하는 문의의 대부분은 "안 돼요"이고, 원인의 대부분은 환경·토큰·등록 3종이다. doctor 하나가 문의 대부분을 셀프서비스로 전환한다.

### 18.2 `--dry-run` + confirm + 진행표시 3종 **[Quick Win #8]**

| 장치 | 구현 | 효과 |
|---|---|---|
| `--dry-run` | 쓰기 작업을 계획만 출력 | 비개발자 신뢰 확보, 사고 방지 |
| confirm 프롬프트 | 파괴적 작업 전 y/N + 대상 전체 표시(truncate 금지) | MCP 사양의 consent 요구와도 정합 |
| 진행 표시 | 단계별 로그(stderr) | "멈춘 건가?" 문의 제거 |

§6의 MCP 사양 요구("로컬 서버 원클릭 설정은 명령 실행 전 적절한 consent 메커니즘을 MUST 구현")와 자연 결합.

### 18.3 피드백 루프를 가볍게

```bash
# 실패 시 자동 제안 (개인정보 없이 로그만)
$ corp-mcp-crm feedback --last-error
  → .corp/feedback/2026-08-05-142301.json 생성됨
  → 사내 이슈 트래커에 첨부하거나 `corp-mcp-crm feedback --send` (사내망 전용)
```

**업로드 불가 제약 대응**: 외부 전송 없이 **사내 파일 경로에 떨어뜨리고 사람이 첨부**하는 형태가 가장 마찰 적고 안전. 자동 수집은 Langfuse 셀프호스팅(사내망)으로.

### 18.4 원커맨드 온보딩

```bash
# README 첫 줄에 이것만
curl -sSL https://내부호스트/install.sh | sh   # ← PreToolUse guard가 막을 패턴이므로 사내 예외 등록 필요
# 또는 (권장, 스크립트 실행 없이)
uvx corp-mcp-crm install --client claude,gemini
```

**주의**: `curl | sh` 패턴은 §16.1의 guard가 차단할 대상이다. **사내 install 경로는 명시적 allowlist에 등록**하고, 가능하면 uvx/npx 직접 실행 형태를 우선한다.

---

## 19. 비용·성능 최적화 (prompt caching, ccusage, 모델 라우팅)

### 19.1 Prompt caching — 단일 최대 레버 **[Quick Win #4]**

**핵심 수치** (여러 출처 교차 확인, 단 가격은 변동):

- Anthropic: cache_control breakpoint를 통한 명시적 캐싱. write는 입력의 1.25×(5분 TTL) 또는 2.0×(1시간 TTL), read는 0.10× — 90% 할인. 최소 1,024 토큰. OpenAI: 자동 캐싱, 서버사이드, 코드 변경 불필요, read는 0.5× — 50% 할인.
- Google의 implicit caching은 75% 할인. 캐싱은 입력 토큰만 건드리며 출력은 절대 할인되지 않는다.
- Anthropic의 5분 티어는 캐시 write당 약 1.4회 read에서 손익분기다. 안정적 프롬프트 워크로드에서 히트율이 ~30% 미만이면 write 프리미엄이 read 절감보다 클 수 있다. 안정 프롬프트에서 60% 미만 히트율은 구조적 문제 신호다.
- 실사례(⚠️ 2차 인용): ProjectDiscovery는 동적 콘텐츠를 재배치해 Anthropic 캐시 히트율을 7%에서 84%로 끌어올려 전체 LLM 비용을 59~70% 절감했고, 프로덕션에서 98억 토큰을 캐시로 서빙했다.

**어떻게 (핵심 원칙)**: **정적 → 동적 순서로 프롬프트를 배열**하고 정적 블록 끝에 breakpoint를 찍는다.

```
[system prompt] [tool definitions] [사내 정책·컨벤션] ← 여기까지 cache_control
[대화 히스토리] [현재 요청]                          ← 매번 변하는 부분
```

**본 프로젝트 적용**: 툴 생성 에이전트는 Anthropic 5원칙 + 사내 규칙 + MCP 템플릿이라는 **거대하고 안정적인 프리픽스**를 매 호출 재전송한다. 캐싱 적용의 교과서적 대상.

**리스크**: 정적 블록에 타임스탬프·요청 ID 등이 섞이면 히트율 0. `cache_read_input_tokens`를 반드시 모니터링.

### 19.2 비용 가시화 — ccusage **[Quick Win #5]**

ccusage는 계정 설정이 전혀 필요 없는 무료 오픈소스 npm CLI다. `npx ccusage@latest`를 실행하면 로컬 JSONL 세션 로그를 전적으로 로컬 머신에서 파싱하며, API 키도 네트워크 호출도 없다. 일별·월별·세션별·5시간 블록 비용 리포트를 모델별·캐시 토큰별 분해와 함께 출력한다. statusline 모드는 실시간 지출을 쉘 프롬프트에 표시한다.

```bash
npm install -g ccusage
ccusage daily              # 일별
ccusage monthly            # 월별
ccusage blocks --live      # 실시간 5시간 과금 윈도우
ccusage daily --breakdown  # 모델별 분해
```

보완: Claude-Code-Usage-Monitor(실시간 대시보드), claude-code-otel(팀용 셀프호스팅 관측 스택). claude-code-otel은 §12의 Langfuse/OTel 스택과 직접 결합 가능.

### 19.3 모델 라우팅 **[Quick Win #6]**

워커 에이전트의 서브에이전트 설정에 `model: haiku`를 지정하라. 플래너는 Opus에 머물러도 되지만, 파일 읽기와 grep을 하는 워커는 그럴 필요가 없다. 서브에이전트별로 frontmatter의 model 필드는 sonnet, opus, haiku, fable 별칭이나 전체 모델 ID, 또는 inherit를 받는다.

```markdown
---
name: schema-checker
description: MCP 툴 스키마 검증 전담
model: haiku
---
```

**주의**: Opus 5는 도입 기간 중 입력 기준 Sonnet 5의 2.5배이며 정가 복귀 후 1.67배로, 옛 가이드가 인용하는 5배가 아니다. 그 5배는 Opus 4.1($15/$75) 대비 수치이고 Opus 4.1은 2026년 8월 5일 은퇴 예정으로 deprecated 상태다. → **모델 배수 기반 라우팅 규칙은 하드코딩하지 말고 설정으로 뺄 것.**

**추가 주의**: Claude 4.7 이후 모델과 Claude Mythos Preview는 새 토크나이저를 쓰며 같은 텍스트에 대해 약 30% 더 많은 토큰을 생성한다. → **모델 업그레이드 시 토큰 예산·컨텍스트 한도 재계산 필요. §11 회귀 게이트에 "토큰 사용량 회귀" 항목 추가 권장.**

### 19.4 절감 스택 요약

| 레버 | 절감 | 노력 | 비고 |
|---|---|---|---|
| Prompt caching | 입력 최대 90% | 하 | 프리픽스 안정성이 전제 |
| Batch API | 전 토큰 50% | 하 | 즉시성 불필요 작업만 |
| 모델 라우팅 | 워커 비용 대폭 | 하 | 서브에이전트 frontmatter |
| 컨텍스트 정리(`/clear`) | 누적 방지 | 하 | 태스크 간 컨텍스트를 비우고, 요청을 보내기 전에 범위를 좁히는 행동 변화가 가장 지속적인 감소를 만든다 |
| 서브에이전트 팬아웃 제한 | 급증 방지 | 중 | 최대 병렬 수 상한 설정 |

---

## 20. 운영 절차 (새 툴 만들 때, 배포 전, 운영 중, 변경 관리)

### 20.1 새 툴을 만들 때

1. 문제를 한 문장으로 정의한다.
2. 입력/출력 스키마를 정한다.
3. 툴 이름을 명확하게 정한다.
4. 성공 케이스와 실패 케이스를 같이 만든다.
5. Inspector로 호출 가능 여부를 확인한다.
6. 골든셋 테스트를 추가한다.
7. 문서와 샘플 config를 같이 저장한다.

### 20.2 배포 전

1. 위험 권한이 있는지 확인한다.
2. 토큰과 인증 범위를 점검한다.
3. stdout 로그 오염이 없는지 확인한다.
4. 로컬과 원격 설정을 분리한다.
5. eval을 통과해야만 배포한다.

### 20.3 운영 중

1. 사용자 피드백과 실패 로그를 모은다.
2. 자주 나오는 작업은 Skill로 승격한다.
3. 반복 실패는 Hook 또는 schema 수정으로 처리한다.
4. 비용이 큰 툴은 호출 횟수와 출력 길이를 점검한다.
5. 회귀가 발견되면 즉시 버전 고정 또는 롤백한다.

### 20.4 변경 관리

- 툴 정의를 바꿀 때는 반드시 버전 기록을 남긴다.
- 구조적 변경은 CI eval 재실행 후 배포한다.
- 권한/토큰/연결 설정은 문서와 함께 업데이트한다.
- 새 팀원이 들어오면 "사용법"보다 먼저 "금지 사항"을 보여준다.

---

## 21. Claude Code 운영 가이드

Claude Code는 "작업 범위 통제"와 "증거 기반 결과 확인"이 핵심이다 ([Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)). 작업의 질을 높이려면 "범위와 검증"을 같이 주는 것이 중요하다.

### 21.1 핵심 설정

- **`.mcp.json`**(프로젝트 스코프, 루트), 사용자 `~/.claude.json`, `claude mcp add <name> <command>`. 설정 정밀도: **managed > project > user > local**.
- `managed-settings.json` + `managed-mcp.json`으로 IT 강제 정책(예: `Bash(curl *)` deny). `strictKnownMarketplaces`, `allowManagedHooksOnly`, `disableAllHooks`로 공급망 통제.
- MCP 출력은 `MAX_MCP_OUTPUT_TOKENS`(기본 25,000)로 제어.
- 프로젝트 스코프 MCP는 승인 흐름이 붙기 때문에, 민감한 내부 서버는 전역보다 프로젝트 단위로 두는 편이 안전하다 ([Claude Code MCP](https://code.claude.com/docs/en/mcp)).

### 21.2 자주 쓰는 명령

| 명령 | 용도 |
|---|---|
| `/init` | 프로젝트용 `CLAUDE.md` 초안 생성. 팀 규칙과 빌드/테스트 명령을 짧게 유지 |
| `/doctor` | 환경 이상을 빠르게 찾는 데 유용 ([Claude Code cheatsheet](https://support.claude.com/en/articles/14553413-claude-code-cheatsheet)) |
| `/plugin` | 팀 공유 플러그인 관리 |
| `claude mcp add` | 외부 MCP 도구 연결 |
| `claude -p` | 비대화형 모드. CI, pre-commit, 자동 리팩터링 파이프라인에 적합 |
| `claude --worktree <name> --tmux` | 저장소별 격리 작업 디렉터리에서 세션 실행 (병렬 세션, 충돌 0) |

### 21.3 git worktree 병렬 세션 **[Quick Win #9]**

`claude --worktree <name>`으로 같은 git repo에서 여러 Claude Code 세션을 코드 편집 충돌 없이 병렬 실행. 서브에이전트도 worktree 격리를 쓸 수 있어 대규모 배치 변경과 코드 마이그레이션에 특히 강력하다. Claude Code 창시자 Boris Cherny가 "단일 최대 생산성 언락"이라 부른 방식(⚠️ 인용의 인용).

```bash
claude --worktree feat-mcp-gen --tmux
# 각 worktree에 태스크 전용 CLAUDE.md를 두면 에이전트별로 범위를 좁힐 수 있다
```

Claude Code는 프로젝트 루트의 CLAUDE.md를 읽는다. worktree마다 디렉터리가 다르므로, 각 worktree에 태스크별 CLAUDE.md를 두어도 다른 worktree에 영향을 주지 않는다.

**리스크**: stateless MCP 서버(순수 함수 툴, 영속 상태 없음)는 문제없다. stateful 서버(DB 커넥션, 파일 인덱스, 캐시된 컨텍스트)는 격리가 필요하다. 두 에이전트가 같은 DB MCP 서버를 통해 같은 스키마에 쓰는 건 브랜치 충돌 문제가 한 계층 위로 올라간 것과 같다. → **MCP 서버 생성 에이전트를 만들 때 "가능한 한 stateless로 설계"를 기본 규칙에 넣을 근거**. 또한 DB·포트도 함께 격리해야 실효(worktree + DB 브랜칭 + 포트 격리를 묶어야 3~5개 세션 동시 실행이 성립).

### 21.4 권장 습관

- 작업 전 "무엇을 만들지"보다 "어떻게 확인할지"를 먼저 적는다.
- 하나의 요청에 너무 많은 목표를 섞지 않는다.
- 관련 파일과 제약을 구체적으로 지정한다.
- 결과를 받을 때는 코드와 검증 방법을 같이 받는다.
- 작업 지시를 줄 때는 "파일명, 시나리오, 기대 결과"를 같이 준다.

### 21.5 자주 쓰는 패턴

- "먼저 계획만." / "구현은 나중." / "테스트 포함." / "실패 케이스 추가." / "호환성 유지."

---

## 22. Gemini CLI 운영 가이드

Gemini CLI는 설정 중심 운영에 적합하다. `mcpServers`와 command 기반 구성이 명확해서, 팀 규칙을 파일로 관리하기 좋다 ([Gemini CLI commands](https://geminicli.com/docs/reference/commands/), [Gemini CLI MCP server](https://geminicli.com/docs/tools/mcp-server/)).

### 22.1 핵심 설정

- `~/.gemini/settings.json` 또는 `.gemini/settings.json`의 `mcpServers` 블록, `gemini mcp <add|list|remove>` ([Google — configure MCP](https://docs.cloud.google.com/cloud-assist/configure-mcp)).
- Extensions는 `gemini-extension.json`(mcpServers, `contextFileName`=GEMINI.md, `excludeTools`; `${extensionPath}` 이식성 참조) ([Phil Schmid — Gemini CLI cheatsheet](https://www.philschmid.de/gemini-cli-cheatsheet)).
- 시크릿은 `"$MY_KEY"` 환경변수 확장 권장, `*TOKEN*/*SECRET*/*PASSWORD*/*KEY*/*AUTH*/*CREDENTIAL*` 자동 redaction(env에 명시하면 informed consent로 예외).
- 툴 병합은 "가장 제한적 정책 승리"(excludeTools union, includeTools intersection).
- Policy Engine(.toml, tier 2)·skills/·agents/(preview) 지원, `gemini --checkpointing`으로 파일 수정 전 스냅샷.

### 22.2 자주 쓰는 명령·단축키

| 명령 | 용도 |
|---|---|
| `/mcp` | 서버 관리·상태 확인 |
| `/settings` | 환경 설정 확인 |
| `gemini mcp add` | MCP 서버 등록 (project scope 권장) |
| `Ctrl+L` | 화면 정리 |
| `--checkpointing` | 파일 수정 전 스냅샷 (되돌리기) |
| custom command / extension 분리 | 개인용 자동화와 팀 표준 분리 |

### 22.3 권장 습관

- 프로젝트마다 필요한 MCP만 등록한다.
- 비밀값은 환경변수로 주고 설정 파일에 평문으로 넣지 않는다.
- 개인용 command와 팀 표준 command를 분리한다.
- 파일 수정형 작업은 checkpoint를 기본으로 둔다.
- `excludeTools`와 include 정책으로 필요한 도구만 보이는 제한적 UI.

### 22.4 호환성 요약

두 클라이언트(Claude Code, Gemini CLI) 모두 stdio + Streamable HTTP, `mcpServers` JSON 키를 공유하므로 **서버 자체는 이식 가능**. 차이는 컨텍스트 파일(CLAUDE.md vs GEMINI.md), 확장 패키징(plugin vs extension), 신뢰/승인 UX, redaction 정책. 생성 에이전트는 양쪽 config를 모두 산출하도록 설계.

| 관심사 | Claude Code | Gemini CLI | 병행 전략 |
|---|---|---|---|
| 컨텍스트 파일 | CLAUDE.md | GEMINI.md | **AGENTS.md를 정본**, 나머지는 import 스텁 (§14.1) |
| 패키징 | plugin + marketplace | extension (`gemini-extension.json`) | 동일 MCP 서버를 양쪽 매니페스트로 산출 |
| 슬래시 커맨드 | `.claude/commands/*.md` | `.toml` custom commands | 커맨드 정의는 공통 md에 두고 얇게 래핑 |
| 스킬 | `.claude/skills/` | `skills/` (SKILL.md 동일 표준) | SKILL.md 그대로 이식 |
| 세션 안전장치 | checkpointing/rewind | `--checkpointing` | 두 쪽 다 켜둘 것 |

---

## 23. 정책 문구 (툴 설계, 보안, 운영, 품질)

아래 문구는 위키 상단 또는 운영 규정 섹션에 그대로 넣어도 된다.

### 23.1 툴 설계 정책

- 툴은 하나의 목적만 가져야 한다.
- 하나의 툴이 너무 많은 일을 하면 분리한다.
- 툴 이름은 동작이 드러나야 한다 (`search_*`, `get_*`, `create_*`, `update_*`).
- 툴 수는 최소화하고 고레버리지로 설계한다.
- 실패 메시지는 사용자가 바로 고칠 수 있어야 한다.
- 응답은 요약(concise)/상세(detailed) 모드를 구분한다.
- 응답은 기본 25,000 토큰 이내, 초과 시 truncate + 안내.

### 23.2 보안 정책

- 승인되지 않은 서버는 연결하지 않는다.
- 토큰은 서버별로 분리하고, 타 서버 발행 토큰을 수용하지 않는다 (토큰 패스스루 금지).
- 최소 권한 원칙을 따른다. 와일드카드/omnibus 스코프(`*`, `all`, `full-access`) 금지.
- 토큰 audience 검증(RFC 8707), non-deterministic 세션 ID + user 바인딩.
- 외부 콘텐츠를 가져오는 서버는 prompt injection 위험을 고려한다.
- stdout에는 로그를 섞지 않는다 (JSON-RPC만, 로그는 stderr).
- 위험 명령은 승인 또는 차단된다 (PreToolUse hook exit 2).
- 툴 정의 서명·해시 고정(rug pull 방지), 의존성 CVE 스캔.
- 사내→외부 업로드 경로는 allowlist로 차단, 다운로드는 허용.

### 23.3 운영 정책

- 배포는 문서, 코드, 테스트, 설정이 함께 있어야 한다.
- 회귀 테스트가 없으면 프로덕션 반영하지 않는다.
- 사용자 영향이 큰 변경은 단계적으로 롤아웃한다 (canary 5% + online eval).
- 문제가 생기면 우선 롤백 가능성을 본다.
- 배포 후 수정이 어렵다고 가정하고 feature flag/remote config로 회수 가능하게 설계한다.
- 감사로그(툴 호출·사용자·버전)를 남긴다.

### 23.4 품질 정책

- 설명은 짧고 명확해야 한다 (description은 "무엇을+언제" 둘 다).
- 반복되는 업무는 Skill로 승격한다.
- 긴 작업은 Subagent 또는 단계형 워크플로우로 분리한다.
- 결과는 반드시 검증 가능한 형태여야 한다.
- 검증은 가능한 한 결정론적 수단 우선, LLM judge는 최후 수단(temperature=0).
- judge·agent 모델 버전 pinning, UNSTABLE=CI 실패.

---

## 24. 예시 설정 파일 (.mcp.json, CLAUDE.md, GEMINI.md, SKILL.md, CI YAML)

### 24.1 MCP 서버 최소 예제 (FastMCP, Python)

```python
from fastmcp import FastMCP

mcp = FastMCP("internal-crm 🚀")

@mcp.tool
def search_customers(query: str, response_format: str = "concise", limit: int = 50) -> dict:
    """Search internal CRM customers by name or email.

    Use this when the user wants to find a customer or needs customer context.
    Prefer many small targeted searches over one broad search.

    Args:
        query: Natural-language name or email fragment. Required.
        response_format: "concise" (name + status only) or "detailed" (adds IDs).
        limit: Max results (default 50). Use pagination for more.
    """
    # ... 실제 조회 로직 (다운스트림 API 호출) ...
    # 25000 토큰 초과 방지: truncation + 안내 메시지
    return {"results": [...], "truncated": False}

if __name__ == "__main__":
    mcp.run()  # 로컬은 stdio; 원격은 mcp.run(transport="streamable-http")
```

설계 규칙: 툴 소수·고레버리지, 네임스페이싱(`crm_search_customers`), `response_format` enum, 25k 토큰 제한, helpful error, `user_id`류 명확한 파라미터명.

### 24.2 .mcp.json (Claude Code 프로젝트 스코프)

```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "${CRM_TOKEN}" }
    },
    "internal-docs": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_docs.server"],
      "env": { "DOCS_API_KEY": "${DOCS_API_KEY}" }
    }
  }
}
```

### 24.3 Gemini CLI settings.json

```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "$CRM_TOKEN" },
      "includeTools": ["search_customers"]
    }
  },
  "excludeTools": [
    "unapproved-dangerous-tool"
  ]
}
```

### 24.4 CLAUDE.md 예시 (팀 프로젝트용 최소)

```markdown
# CLAUDE.md

## Project Goal
사내 AI 협업용 툴 생성 및 검증 자동화

## Working Rules
- 먼저 계획을 제시한다.
- 코드는 테스트와 함께 작성한다.
- 외부 시스템은 승인된 MCP만 사용한다.
- 위험한 작업은 사전 경고를 넣는다.
- 결과는 짧은 요약과 상세로 나눈다.
- 불확실한 부분은 추측하지 말고 확인 질문을 한다.

## Code Style
- 함수명은 동작이 드러나게 쓴다.
- 툴명은 search/get/create/update 패턴을 우선 사용한다.
- 출력은 concise / detailed 같은 명확한 모드를 지원한다.

## Testing Rules
- 새 기능에는 최소 1개 성공 케이스와 1개 실패 케이스를 추가한다.
- 스키마 변경이 있으면 Inspector로 확인한다.
- 회귀 가능성이 있으면 골든셋 테스트를 추가한다.

## Build / Run
- 설치: `uv sync`
- 테스트: `pytest -q`
- 서버 실행: `python -m app.server`

## Verification
- 성공 케이스 1개 이상
- 실패 케이스 1개 이상
- 스키마 확인
- 회귀 체크리스트 포함

## Safety
- stdout에 디버그 로그를 출력하지 않는다.
- 비밀값은 환경변수로만 주입한다.
- 허용되지 않은 외부 전송은 하지 않는다.
```

CLAUDE.md는 **짧고 실행 가능해야** 한다. 너무 긴 규칙 문서는 오히려 실제 작업에 덜 쓰인다. 가능하면 `@AGENTS.md` import로 정본을 분리(§14.1).

### 24.5 GEMINI.md 예시

```markdown
# GEMINI.md

## Project Purpose
사내 협업용 AI 툴 생성 및 검증 작업을 위한 표준 운영 문서.

## Working Rules
- 작업 시작 전에 목표, 제약, 검증 기준을 먼저 적는다.
- MCP 서버는 프로젝트 범위로 우선 등록한다.
- 결과는 요약과 상세를 구분해서 출력한다.
- 파일 수정이 필요한 작업은 checkpoint를 사용한다.
- 위험한 변경은 바로 실행하지 말고 확인을 요청한다.
- 비밀값은 환경변수로만 관리한다.

## Preferred Workflow
1. 계획 작성
2. 변경안 제시
3. 검증 명령 실행
4. 결과 요약
5. 필요한 경우 롤백

## Tool Usage
- 필요한 MCP만 활성화한다.
- 쓰지 않는 서버는 끈다.
- 외부 공개용 도구와 내부 전용 도구를 분리한다.

## Output Style
- 먼저 결론 → 근거 → 실행 명령 순서로 작성한다.
- 실패 원인과 수정 방법을 분리해서 설명한다.
```

### 24.6 SKILL.md 예제

```markdown
---
name: crm-report-writer
description: Generate weekly CRM retention reports from internal CRM data. Use when the user asks for a retention report, churn summary, or weekly customer health digest.
allowed-tools: ["internal-crm__search_customers"]
---

# CRM Retention Report

## When to use
사용자가 "리텐션 리포트", "이탈 요약", "주간 고객 건장도"를 요청할 때.

## Steps
1. `search_customers`로 대상 세그먼트 조회 (concise 모드).
2. references/report_template.md 형식에 맞춰 작성.
3. 수치는 반드시 툴 출력에 근거. 추정 금지.

## Validation
- 모든 고객 ID가 실제 조회 결과에 존재하는지 확인.
```

description은 "무엇을+언제"를 모두 담아 트리거 정확도 확보. body는 <500줄, 상세 문서는 `references/`로 분리.

```markdown
---
name: weekly-status-report
description: Generate a weekly internal status report. Use when the user asks for weekly summary, progress update, or team digest.
allowed-tools: ["internal-search__search_reports"]
---

# Weekly Status Report

## When to use
주간 요약, 진행 상황, 팀 현황 보고가 필요할 때 사용한다.

## Steps
1. 최근 7일 데이터를 조회한다.
2. 중요 이슈와 완료 항목을 분리한다.
3. 숫자와 날짜는 출처 기반으로만 쓴다.
4. 마지막에 action items를 정리한다.

## Validation
- 모든 수치는 실제 조회 결과에 있어야 한다.
- 추정값을 쓰지 않는다.
```

### 24.7 CI 회귀 게이트 (GitHub Actions 골자)

```yaml
name: MCP Server Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: uv sync --dev
      - run: uv run pytest -m "not integration" -q      # deterministic 유닛(매 커밋)
      - run: uv run pytest tests/test_schema.py -v        # 스키마 validation(계약 드리프트)
      - run: npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server  # conformance
      - run: uv run mcp-eval run --golden tests/golden/ --min-pass 0.9  # eval 골든셋 게이트
```

---

## 25. 3단계 로드맵 실행 계획

### 25.1 1단계 (MCP 서버 생성 에이전트, 최우선)

- 생성 에이전트 = Claude Code 기반 오케스트레이터. 입력: 대상 API/도메인 설명(+ llms.txt·SDK 문서). 산출: (a) FastMCP 서버 코드, (b) `.mcp.json`/Gemini `settings.json` 샘플, (c) mcp-eval 테스트 케이스, (d) MCP Inspector conformance 스크립트, (e) README·보안 체크리스트.
- 생성 에이전트에 Anthropic 5원칙을 시스템 프롬프트/Skill로 고정. 툴 개수 최소화·네임스페이싱·`response_format` enum·25k 토큰 제한·helpful error를 강제 규칙화.
- 게이트: 생성 직후 자동으로 Inspector 연결 + mcp-eval 실행. 통과 못 하면 배포 산출 금지("배포 후 회수 불가" 대응).

### 25.2 2단계 (Skills/프롬프트팩 생성)

- SKILL.md 생성 에이전트. description 품질 검사기(트리거 시뮬레이션: 실제 요청 문장 10개로 발화율 측정) 내장. body <500줄 강제, 상세는 `references/`.
- 프롬프트팩/스킬은 사내 GitHub repo에서 버전 관리, plugin으로 패키징해 마켓플레이스 배포. 개인→프로젝트→plugin 순으로 승격.

### 25.3 3단계 (워크플로우 자동화)

- 결정론적으로 표현 가능한 것은 워크플로우(chaining/routing)로, 예측 불가한 것만 에이전트로. LangGraph(durable checkpoint·HITL interrupt) 또는 Temporal(내구 실행) 위에 사내 API 커넥터를 MCP 툴로.
- 시크릿은 환경변수 확장·keychain·사내 secret manager. **업로드 불가 제약상 사내→외부 데이터 유출 경로를 allowlist로 차단**, 다운로드는 허용.

### 25.4 실행 권고 (시간별)

**즉시 (0~4주)**

1. MCP 사양 버전을 **2025-11-25 stable**로 고정(pinning). 신규 서버는 stdio(로컬)+Streamable HTTP(원격), SSE 금지.
2. 생성 에이전트 v0를 Claude Code로 구축: FastMCP 서버 + mcp-eval 케이스 + Inspector 스크립트를 한 번에 산출. Anthropic 5원칙을 Skill로 고정.
3. Langfuse 셀프호스팅(Docker) + OpenTelemetry GenAI conventions 계측을 파일럿 프로젝트에 붙임. semantic convention 버전 pinning.

**단기 (1~3개월)**

4. CI 회귀 게이트 구축: 골든셋 ≥30케이스, judge temperature=0·3회 majority-vote, ±3% 임계, 모델/judge 버전 pinning. UNSTABLE=실패.
5. 사내 GitHub에 `.claude-plugin/marketplace.json` 레지스트리 생성. `managed-settings.json` + `strictKnownMarketplaces` + `managed-mcp.json`으로 IT 승인 공급망 강제.
6. 보안 통제 구현: 토큰 audience 검증(RFC 8707), allowlist, 툴 정의 서명/해시 고정(rug pull 방지), non-deterministic 세션 ID, 감사로그, mcp-remote 등 의존성 CVE 스캔.

**중기 (3~6개월)**

7. 2단계 Skills 생성 에이전트 + description 트리거 검사기.
8. canary 롤아웃(5% + online eval), feature flag/remote config로 "배포 후 수정 불가" 완화.
9. 3단계 워크플로우: LangGraph/Temporal + 사내 API 커넥터, HITL 승인 게이트.

### 25.5 변경 트리거 (벤치마크)

- 골든셋 pass rate <90% 또는 judge agreement <0.8 → 배포 중단.
- 모델 버전 업그레이드 시 회귀셋 재실행 필수(회귀 감지되면 pin 유지).
- tool-call error율 >5% → description 재작성.
- MCP 사양이 2026-07-28 RC로 정식화되면 stateless core·Roots/Sampling deprecated 대응 재평가.

---

## 26. Quick Wins TOP 15

ROI 높고 리스크 낮은 순.

| # | 항목 | 카테고리 | 효과(ROI) | 리스크 | 난이도 | 소요 |
|---|---|---|---|---|---|---|
| 1 | **AGENTS.md 단일 소스 + CLAUDE.md/GEMINI.md는 @import 스텁** | B | 3사 CLI 컨텍스트 중복 제거, drift 소멸 | 낮음 | 하 | 1h |
| 2 | **PostToolUse hook로 포맷·린트 강제** | A | LLM이 "잊어버리는" 규칙을 100% 결정론적 강제 | 낮음 | 하 | 1h |
| 3 | **PreToolUse hook로 위험 명령·보호 경로 차단** | A/D | 사고 방지. exit 2로 툴 호출 자체를 블록 | 낮음 | 하 | 2h |
| 4 | **prompt caching 적용 (cache_control)** | G | 입력 토큰 최대 90% 절감, TTFT 최대 85% 단축 | 낮음 | 하 | 2h |
| 5 | **ccusage로 토큰/비용 가시화** | G | 설치 0, 로컬 JSONL만 읽음, 폐쇄망 OK | 없음 | 하 | 15m |
| 6 | **서브에이전트 model: haiku 라우팅** | G | 워커 작업 비용 대폭 절감 | 낮음 | 하 | 30m |
| 7 | **`doctor` 커맨드(환경 자가진단) 산출물에 포함** | F | 온보딩 문의 급감 | 없음 | 하 | 2h |
| 8 | **생성 산출물에 `--dry-run` 기본 탑재** | F | 비개발자 신뢰도·안전성 동시 확보 | 없음 | 하 | 2h |
| 9 | **git worktree 병렬 세션 (`claude --worktree`)** | A | 에이전트 간 파일 충돌 0, 병렬 처리량 상승 | 낮음 | 하 | 30m |
| 10 | **Spec-first: spec.md → plan.md → tasks.md** | C | "그럴듯하지만 틀린 코드" 감소. 토큰 20~40%↑ 대신 재작업↓ | 낮음 | 중 | 반나절 |
| 11 | **cross-model review (Claude 생성 → Gemini 리뷰)** | C | 동일 모델 blind spot 제거. 3사 계약 이미 보유 | 낮음 | 하 | 2h |
| 12 | **MCPB(.mcpb) 번들로 원클릭 배포** | D/F | 비개발자 설치 마찰 제거 | 낮음 | 중 | 반나절 |
| 13 | **SessionStart hook로 사내 정책·컨벤션 자동 주입** | A/B | 매번 붙여넣기 제거, 정책 일관성 | 낮음 | 하 | 1h |
| 14 | **파일 기반 메모리(NOTES.md/CONTINUE.md) 패턴** | B | 긴 세션 컨텍스트 손실 방어 | 없음 | 하 | 1h |
| 15 | **llms.txt로 사내 API 문서 에이전트 친화화** | B | 생성 품질↑, 환각↓ | 없음 | 하 | 반나절 |

카테고리 범례: A=개발자 체감 편의, B=컨텍스트 엔지니어링, C=코드 생성 품질, D=MCP 서버 운영, F=사용자 편의성, G=비용·성능.

---

## 27. 종합 체크리스트 (사양/컨텍스트/강제장치/품질/보안/산출물/비용/배포)

### 27.1 사양·품질

- [ ] MCP 사양 버전 pinning(2025-11-25), transport = stdio/Streamable HTTP만
- [ ] 툴 개수 최소화, 네임스페이싱, `user_id`류 명확한 파라미터명
- [ ] 응답 25k 토큰 제한, 페이지네이션/필터/truncation, helpful error 메시지
- [ ] MCP Inspector conformance 통과, 스키마 `$ref`/anyOf 클라이언트 호환 확인, stdout 오염 없음
- [ ] mcp-eval 골든셋 ≥30, pass rate ≥90%, pass^k 통계 판정
- [ ] judge·agent 모델 버전 pinning, judge temperature=0, UNSTABLE=실패

### 27.2 컨텍스트·문서

- [ ] AGENTS.md가 정본이고 CLAUDE.md/GEMINI.md는 스텁인가
- [ ] AGENTS.md에 "정확한 명령어"가 들어 있는가 (모호한 도구명 금지)
- [ ] 사내 API에 llms.txt가 있는가
- [ ] compact instructions 블록이 있는가

### 27.3 강제 장치 (Hooks)

- [ ] PostToolUse hook: 포맷·린트
- [ ] PreToolUse hook: 파괴적 명령·보호 경로 차단, exit 2 확인
- [ ] hook이 1초 이내인가, CI 환경에도 의존성이 있는가
- [ ] hook 개수 8개 이하인가

### 27.4 보안

- [ ] 토큰 audience 검증(RFC 8707), 세션 non-deterministic ID + user 바인딩, 로컬 원클릭 consent
- [ ] 토큰 정의 서명/해시 고정(rug pull), allowlist, 최소 권한 스코프(와일드카드 금지)
- [ ] 감사로그(툴 호출·사용자·버전), OpenTelemetry 계측(semantic convention 버전 pin)
- [ ] 의존성 CVE 스캔(mcp-remote 등), 사내→외부 업로드 차단 경로 확인
- [ ] 외부 repo의 AGENTS.md를 사람이 먼저 읽는가 (인젝션 방지)

### 27.5 산출물 완결성 (생성 에이전트가 매번 산출해야 할 것)

- [ ] server 코드 / .mcp.json / gemini settings.json
- [ ] .mcpb manifest (command가 npx가 아니라 node/`${__dirname}`인지 확인)
- [ ] mcp-eval 골든셋 + Inspector 스모크
- [ ] `doctor` 명령
- [ ] `--dry-run` + confirm
- [ ] pre-commit 설정
- [ ] README (원커맨드 설치, 실패 시 feedback 경로)
- [ ] fallback 모델·timeout·circuit breaker·정직한 실패 통지
- [ ] feature flag/remote config, canary 롤아웃 경로

### 27.6 비용·성능

- [ ] cache_control breakpoint 배치, `cache_read_input_tokens` 모니터링
- [ ] 캐시 히트율 60% 이상인가
- [ ] 서브에이전트 model 라우팅 설정
- [ ] ccusage 또는 claude-code-otel 도입
- [ ] 서브에이전트 팬아웃 상한 설정
- [ ] 모델 업그레이드 시 토크나이저 변화 대비 토큰 예산 재계산

### 27.7 배포·채택

- [ ] plugin 배포 스코프(project), managed 거버넌스 설정(`strictKnownMarketplaces`)
- [ ] 자동 설치/자동 업데이트 채널이 있는가 (Block 패턴)
- [ ] 첫 배포 대상이 "데이터를 소유하고 실패 비용이 낮은" 영역인가
- [ ] 자율성이 단계적인가 (초안 생성 → 사람 커밋 → 자동 PR)
- [ ] LLM 비종속 구조인가

---

## 28. FAQ

### Q1. 왜 MCP를 많이 두지 말라고 하나요?

MCP가 많아질수록 어떤 툴을 언제 써야 하는지 모델이 혼동하기 쉽고, 컨텍스트와 운영 복잡도도 같이 증가한다. 실무에서는 필요한 것부터 적게 시작하는 편이 안정적이다. 2~3개 핵심 MCP부터 시작하고 나머지는 필요할 때만 활성화하라.

### Q2. Skills와 MCP 중 무엇이 먼저인가요?

먼저 MCP로 실제 연결이 필요한지 확인하고, 반복되는 절차가 보이면 Skill로 빼는 순서가 좋다. MCP는 "행동", Skill은 "지식"에 가깝다.

### Q3. Hooks는 어디에 써야 하나요?

반드시 지켜야 하는 규칙에 쓰는 것이 좋다. 포맷 검사, 위험 명령 차단, 승인, 커밋 전 검증 같은 것들이다. "언제나 적용되어야 하는 규칙"이 핵심 기준이다.

### Q4. Claude Code와 Gemini CLI는 무엇이 다른가요?

Claude Code는 프로젝트 맥락과 승인 흐름을 포함한 작업형 에이전트 운영에 강하고, Gemini CLI는 설정/command 중심의 표준화 운영에 잘 맞는다. 둘 다 MCP를 쓰지만, 설정 파일과 작업 습관은 다르게 가져가는 것이 좋다. 두 클라이언트 모두 `mcpServers` JSON 키를 공유하므로 서버 자체는 이식 가능하고, 생성 에이전트는 양쪽 config를 모두 산출하도록 설계한다.

### Q5. 어떤 팀에 가장 효과가 큰가요?

반복 업무가 많고, 여러 도구를 함께 쓰며, 검증/승인/보안이 중요한 팀에 가장 효과가 크다. 특히 개발, 운영, 데이터, 문서화, 내부 자동화 팀에서 ROI가 높다.

### Q6. 초기에 가장 먼저 해야 할 것은 무엇인가요?

`CLAUDE.md`와 `GEMINI.md`를 짧게 만들고(또는 AGENTS.md 정본 + import 스텁), 프로젝트별 MCP를 2~3개만 붙인 뒤, 테스트와 관측을 추가하는 것이다. 이 순서가 가장 빨리 체감 효과를 준다. 그 다음에 Skills를 추가해 반복 작업을 줄이고, plugin이나 extension으로 팀 배포 단위를 묶는다.

### Q7. "배포 후 회수 불가"는 어떻게 대응하나요?

세 가지로 대응한다: (1) 생성 단계에서 eval 하네스를 내장(Inspector + mcp-eval 골든셋)해 통과 못 하면 배포 산출 자체를 금지. (2) feature flag/remote config로 프롬프트·모델 버전을 원격 전환 가능하게. (3) HTTP hook을 사내 정책 서버로 향하게 해 배포된 가드레일을 원격에서 갱신.

### Q8. MCP 게이트웨이는 언제 도입하나요?

1단계(MCP 서버 몇 개)에서는 불필요. 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입을 검토한다. 단, 게이트웨이 도입은 되돌리기 어려운 결정이므로 `managed-mcp.json` 거버넌스로 먼저 버티고, 필요가 실증되면 도입한다.

### Q9. 비용 급증을 막으려면?

prompt caching(정적→동적 순서 배열), 서브에이전트 model: haiku 라우팅, 서브에이전트 팬아웃 상한, ccusage로 가시화, `/clear`로 태스크 간 컨텍스트 비우기를 조합한다. 가장 흔한 급증 원인은 서브에이전트 팬아웃과 autocompact 루프다.

---

## 29. 부록: 고급 프롬프트 템플릿 (5종)

아래 템플릿은 Claude Code/Gemini CLI 공통으로 쓸 수 있다. 핵심은 "결과물의 형식"과 "검증 기준"을 같이 주는 것이다. Claude의 Best Practices가 권장하는 "scope the task", "show evidence", "use tools for external systems"와 잘 맞는다.

### 29.1 설계 요청형 (제약 우선)

```text
다음 조건으로 설계안을 작성해줘.

목표:
- 사내 툴 생성 에이전트 구축

제약:
- MCP는 프로젝트별 최소 구성
- 보안은 최소 권한 원칙
- 결과물은 코드, 테스트, 설정, 문서를 함께 생성

원하는 출력:
1. 권장 아키텍처
2. 구성 요소별 역할
3. 배포 전 체크리스트
4. 실패 시 복구 전략
```

### 29.2 구현 요청형 (검증 우선)

```text
이 기능을 구현해줘.

입력:
- [기능 설명]

반드시 포함할 것:
- 핵심 코드
- 테스트 케이스 2개 이상
- 실패 케이스 1개
- 실행 방법
- 주의할 점
```

### 29.3 검증 요청형 (증거 우선)

```text
다음 산출물을 검증해줘.

검증 항목:
- 스키마 일치 여부
- 보안상 위험한 설정 여부
- 테스트 누락 여부
- 운영 시 문제가 될 부분

출력 형식:
- 문제 없음 / 수정 필요
- 발견된 이슈
- 우선순위
- 바로 적용 가능한 수정안
```

### 29.4 리팩터 요청형 (분리형)

```text
아래 코드를 리팩터링해줘.

우선순위:
1. 읽기 쉬움
2. 안정성
3. 테스트 가능성

제약:
- 기능은 바꾸지 말 것
- 기존 인터페이스는 유지할 것
- 바뀐 부분은 이유를 짧게 설명할 것
```

### 29.5 운영 자동화 요청형 (회귀 방지)

```text
이 작업을 운영 자동화 관점으로 정리해줘.

필수 항목:
- 반복 가능한 절차
- 실패 지점
- 로그/관측 포인트
- 승인 필요한 단계
- 롤백 방법

기존 행동을 깨는 변경이 있으면 반드시 호환성 노트를 적어라.
```

---

## 30. Caveats (주의사항 및 불확실성)

- **최신성**: MCP 사양은 매우 빠르게 진화한다. 2026-07-28 RC(stateless core, MCP Apps, Tasks 확장)는 조사 시점 기준 release candidate이며 정식화 시 core가 stateless로 바뀌므로 세션/전송 설계 재검토 필요 ([MCP spec version timeline](https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html)). Roots/Sampling/Logging deprecated도 RC 기준 예고 사항이다.
- **OAuth 세부는 버전 민감**: RFC 8707 `resource` MUST 요구는 GitHub Issue #1614에서 SHOULD로 완화 논의 중 ([GitHub Issue #1614](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1614))이고, Dynamic Client Registration은 2025-11-25에서 SHOULD→MAY로 강등되며 CIMD로 대체되었다. 인증 구현 전 해당 리비전 원문 재확인 권장 ([MojoAuth — MCP authorization](https://mojoauth.com/blog/how-mcp-authorization-actually-works-oauth-2-1-resource-servers-and-resource-indicators)). (토큰 패스스루 금지·audience 검증·RFC 9728 protected-resource-metadata·OAuth 2.1 resource-server 역할은 두 리비전 공통 유지.)
- **불확실 수치**: FastMCP "70% 점유율·하루 100만 다운로드"는 FastMCP/PrefectHQ 자체 주장([GitHub — PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp), 1차 검증 아님). Anthropic Slack/Asana MCP 개선 그래프의 정확한 수치는 이미지로만 제공되어 텍스트 추출 불가 — 인용 가능한 확정 수치는 Opus 4 49%→74%, Opus 4.5 79.5%→88.1%(Tool Search Tool, [Anthropic — advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)), 툴 description 개선의 "40% task completion time 감소"([Anthropic — multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)) 뿐이다.
- **eval 프레임워크 비교 출처 편향**: Langfuse/Braintrust/Phoenix 비교 상당수가 벤더(Latitude, Braintrust 등) 블로그다. 셀프호스팅 무료·오픈소스 사실관계는 일치하나, "best" 평가는 마케팅 스핀 가능성 있어 자체 PoC로 검증 권장. Langfuse의 ClickHouse 인수 후 라이선스 정책도 장기적으로 재확인 필요(현재 MIT·셀프호스팅 유지 확인됨).
- **보안 통계**: arXiv:2508.12538 "배포 서버 30%+ 취약", MCPTox(arXiv:2508.14925) "o1-mini ASR 72.8%·Claude-3.7-Sonnet 거부율 <3%"는 학술 벤치 조건 기준이며, YARA 스캐너 78% false positive 보고처럼 방법론에 따라 편차가 크다. 절대 수치보다 통제 원칙(allowlist·서명·audience 검증)의 채택이 핵심.
- **CVE 특정성**: CVE-2025-6514(mcp-remote), CVE-2025-54135/54136(Cursor)은 특정 클라이언트/패키지 버전 취약점이다. 사내 구축 서버가 자동으로 취약한 것은 아니며, 해당 컴포넌트 사용 시에만 해당된다.
- **커뮤니티 블로그 비중이 높다**: hook 이벤트 개수(27개/30개/12개), Claude Code 버전 번호, 모델 가격 등은 출처마다 상이하며 빠르게 변한다. **공식 문서(platform.claude.com/docs, geminicli.com/docs)로 최종 확인 필수.**
- **MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심하다**: Bifrost 관련 글 다수가 Maxim AI 자사 콘텐츠에서 자사를 1위로 놓는다. 순위를 신뢰하지 말고 §16.2의 평가 기준으로 자체 PoC.
- **기업 도입 수치는 대부분 2차 인용이다**: Coinbase 5%, Ramp 50%, Uber 21,000시간 등은 취합 블로그 출처이며 1차 발표 확인 전에는 참고 수준으로만.
- **AGENTS.md의 Claude Code 지원 여부는 출처가 엇갈린다**: "지원한다"(2026-06)와 "지원 대기 중"이 혼재. 실제 환경에서 테스트 후 확정할 것. 어느 쪽이든 CLAUDE.md에서 `@AGENTS.md` import하는 방식은 안전하게 동작.
- **가격은 2026년 중반 기준이며 도입기 할인이 걸려 있다**: Sonnet의 $2/$10 도입가가 2026-08-31 종료 예정 등, 모든 비용 계산은 재확인 필요.
- **AGENTS.md 간접 프롬프트 인젝션**은 NVIDIA 기술 블로그가 다룬 실재 위협 벡터다. 외부 repo의 컨텍스트 파일을 신뢰하지 말 것.
- **엔터프라이즈 3사 버전 사용 관점**: 본 보고서는 Claude Code·Gemini CLI 중심으로 검증했다. OpenAI Agents SDK/Codex 경로도 MCP·Agent Skills 오픈 표준을 지원하므로 이식 가능하나, 구체 config·redaction 정책은 별도 검증이 필요하다.

---

*— 문서 끝 —*
