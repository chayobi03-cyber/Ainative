<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# 사내 AI 협업용 "툴 생성 에이전트" 구축 종합 기술 리서치 보고서

*작성일: 2026년 8월 4일 · 조사 시점 최신성: 2025~2026년 자료 기준*

## TL;DR

- **1단계 MCP 서버 생성 에이전트부터 시작하되, 절대 "코드 생성기"로만 만들지 말고 "eval 하네스가 내장된 생성기"로 설계하라.** Anthropic 공식 가이드(2025년 9월 11일 "Writing effective tools for agents — with agents")는 "When we traditionally write software, we're establishing a contract between deterministic systems"라며 툴은 결정론적 시스템과 비결정론적 에이전트 간의 계약이라 규정하고, 툴 품질은 프롬프트 엔지니어링과 eval 반복(human-written vs Claude-optimized held-out test set 비교)으로만 확보된다고 결론짓는다. 생성 에이전트가 MCP 서버 코드와 함께 mcp-eval 테스트 케이스·MCP Inspector 계약 테스트를 동시에 산출하도록 만들어야 "배포 후 회수 불가" 제약을 견딜 수 있다.
- **전송 방식은 로컬은 stdio, 원격/사내 웹은 Streamable HTTP로 확정하고 SSE는 신규 구축에서 배제하라.** MCP 사양은 2025-03-26에 HTTP+SSE를 deprecated 처리했고, 2025-06-18(structured output·elicitation·OAuth Resource Server), 2025-11-25(최신 stable, CIMD·incremental scope), 2026-07-28 RC(stateless core)로 빠르게 진화 중이다. 보안은 사양이 명시적으로 "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server"를 요구하며, [github](https://github.com/johnzfitch/claude-wiki/blob/master/06-MCP-Tools/General/mcp-specification-2025-11-25-basic-security-best-practices.md) tool poisoning·rug pull·confused deputy가 실제 CVE(mcp-remote CVE-2025-6514, CVSS 9.6)로 입증되었으므로 allowlist·서명·감사로그가 필수다.
- **배포 형태는 "Claude Code 플러그인 마켓플레이스(사내 GitHub 레지스트리) + managed-settings.json 거버넌스" 조합을 1순위로 권고한다.** 터미널 중심 환경에 가장 잘 맞고, `strictKnownMarketplaces`·`managed-mcp.json`으로 IT가 승인 공급망을 통제할 수 있다. 평가/관측은 폐쇄망 셀프호스팅이 가능한 Langfuse(오픈소스 MIT, ClickHouse+PostgreSQL 기반, 2026년 1월 16일 ClickHouse에 인수되었으나 오픈소스·셀프호스팅 유지) + OpenTelemetry GenAI semantic conventions를 표준으로 삼고, CI에 골든셋 회귀 게이트(≥30케이스, pass^k 통계 판정)를 붙여 모델 버전 업그레이드 회귀를 자동 차단하라.


## Key Findings

### 1. MCP 사양 현황 (2025~2026)

MCP는 날짜 기반 버저닝을 쓴다. 주요 리비전:

- **2024-11-05**: 초기 stable. client-server 모델, tools/resources/prompts primitive 확립.
- **2025-03-26**: Streamable HTTP transport 도입, OAuth 2.1 authorization, **HTTP+SSE deprecated**.
- **2025-06-18**: structured tool output, elicitation(서버가 사용자에게 추가 입력 요청), resource links, OAuth Resource Server 분류, RFC 8707 Resource Indicators, JSON-RPC 배칭 제거.
- **2025-11-25 (최신 stable)**: OpenID Connect Discovery, tools/resources/prompts용 icons(SEP-973), incremental scope consent(SEP-835), URL mode elicitation(SEP-1036), sampling에 tool calling(SEP-1577), OAuth Client ID Metadata Documents(CIMD, SEP-991), experimental Tasks.
- **2026-07-28 RC**: stateless core, MCP Apps, Tasks를 확장으로 이동, 공식 deprecation 라이프사이클 정책. 이 RC에서 Roots/Sampling/Logging이 deprecated 예정으로 표시됨(신규 구현은 tool parameters·direct provider API·stderr/OpenTelemetry 사용 권장). Streamable HTTP는 Mcp-Method·Mcp-Name 헤더 요구(SEP-2243), list/resource 결과에 ttlMs·cacheScope(SEP-2549) 추가.

**Primitive 구성**: Tools(모델이 호출하는 함수, name+description+JSON Schema; 2025-06-18부터 structured output·resource link 선언 가능), Resources(URI로 식별되는 읽기 컨텍스트), Prompts(재사용 템플릿). 클라이언트가 서버에 제공하는 역량: Sampling(서버가 클라이언트 모델에 생성 요청), Elicitation(2025-06-18 신규), Roots(작업 가능 디렉터리/URI 통지).

**Transport**: 사양이 정의하는 live 옵션은 stdio(로컬 서브프로세스, stdin/stdout newline-delimited JSON-RPC)와 Streamable HTTP(원격, 단일 엔드포인트 /mcp, 필요 시 SSE 스트림 업그레이드; HTTP/1.1 chunked로 동작, HTTP/2 불필요) 두 가지뿐이다. 구형 HTTP+SSE(2024-11-05, POST/GET 두 엔드포인트)는 2025-03-26에 deprecated, 2026-07-28 RC에서 정식 Deprecated 라이프사이클로 분류되어 향후 제거 대상. [AgentCat](https://agentcat.com/guides/comparing-stdio-sse-streamablehttp/) TypeScript SDK 1.10.0(2025-04-17)이 Streamable HTTP를 최초 지원. stdio는 동시 부하에 취약(한 테스트에서 20 동시연결 중 22요청 중 20 실패 보고).

### 2. MCP 개발 SDK / FastMCP

- 공식 SDK는 전 주요 언어에 존재(Python, TypeScript 등). **FastMCP 1.0은 2024년 공식 MCP Python SDK에 통합**되었다. 독립 프로젝트 FastMCP(현재 PrefectHQ 유지)는 자체 주장으로 하루 100만+ 다운로드, 전 언어 MCP 서버의 약 70%를 구동한다고 함(1차 검증 불가 — 벤더 주장).
- **중요 구분**: 공식 SDK 내장 `mcp.server.fastmcp.FastMCP`(FastMCP 1.0 계열, `lifespan` 파라미터 사용, `dependencies` 파라미터 **없음**)와 별도 프로젝트 FastMCP 2.0(jlowin/PrefectHQ)은 다르다. 공식 SDK는 **Python ≥3.10 필수**(3.7~3.9 설치 실패). 2025-11-11 감사 기준 공식 SDK 버전 1.21.0, 프로토콜 2025-06-18 지원.
- TypeScript 진영: 공식 modelcontextprotocol/typescript-sdk(스펙 동기), punkpeye/fastmcp(고수준 프레임워크), @prefecthq/fastmcp-ts(FastMCP TS 공식 카운터파트). FastAPI-MCP(기존 FastAPI 앱을 브리지)도 옵션.


### 3. Anthropic 공식 툴 작성 가이드 (2025-09-11)

"Writing effective tools for agents — with agents"의 5대 원칙:

1. **올바른 툴 선택**: API를 얇게 래핑하지 말 것. `list_contacts` 대신 `search_contacts`. [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) 여러 API 호출을 하나로 합친 고레버리지 툴(`schedule_event`, `get_customer_context`)을 소수만 구현. [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) 툴이 많거나 겹치면 에이전트가 혼란.
2. **네임스페이싱**: 서비스·리소스별 prefix(`asana_search`, `asana_projects_search`). [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) prefix vs suffix는 LLM별로 효과가 달라 eval로 결정.
3. **의미 있는 컨텍스트 반환**: `uuid`·`mime_type` 같은 저수준 식별자 대신 `name`·`file_type`. [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) UUID를 의미 있는 언어/0-index로 해석하면 환각 감소·검색 정밀도 향상. `response_format` enum(`concise`/`detailed`)으로 verbosity 제어(예시: detailed 206토큰 vs concise 72토큰, ~⅓).
4. **토큰 효율**: 페이지네이션·range·필터·truncation을 기본값과 함께. Claude Code는 툴 응답을 **기본 25,000 토큰**으로 제한. 에러 메시지도 "무엇을 고쳐야 하는지" 프롬프트 엔지니어링(불투명한 traceback 금지).
5. **툴 description 프롬프트 엔지니어링**: 신입에게 설명하듯 암묵지를 명시화. `user` 대신 `user_id`. Claude Sonnet 3.5가 SWE-bench Verified에서 description 정밀 개선만으로 SOTA 달성. [Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)

평가 방법론(가이드 원문): 실제 워크플로우 기반 태스크 수십 개 생성(단순 sandbox 금지, 여러 툴 호출 요구) → 각 태스크에 검증 가능한 응답 페어링 → 단순 while-loop 에이전트로 프로그래매틱 실행 → reasoning/feedback 블록을 tool call 앞에 출력 유도(CoT) → transcript·tool-call 메트릭(런타임, 호출 수, 토큰, 에러) 분석 → Claude Code로 transcript 붙여넣어 툴 자동 리팩터. Held-out test set으로 오버핏 방지(그래프 캡션: "Held-out test set performance ... human-written vs Claude-optimized Slack MCP tools").

**"Code execution with MCP" (2025-11-04)**: 툴 정의를 전부 컨텍스트에 올리고 중간 결과를 컨텍스트로 통과시키는 기존 방식의 토큰 낭비를 해결. [anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp) MCP 툴을 코드 API(파일)로 노출하고 모델이 코드를 작성해 호출 → progressive tool discovery, 중간 데이터가 모델을 안 거침(민감정보 un-tokenize 패턴). 단, Anthropic은 개념만 제시하고 **구현 코드는 미제공**(샌드박스 보안 부담을 팀에 전가).

**"Introducing advanced tool use" (2025-11-24, Opus 4.5 동시 발표)**: Tool Search Tool 활성화 시 대형 툴 라이브러리 MCP eval 정확도가 **Opus 4 49%→74%, Opus 4.5 79.5%→88.1%**로 향상. Anthropic 측정에서 5개 서버(약 58 tools) 셋업 시 툴 정의가 약 55,000 토큰을 소비하며, `defer_loading: true` 적용 시 ~134k→~5k로 **약 85% 토큰 절감**(on-demand 툴 발견). description 개선만으로 "40% task completion time 감소" 사례도 보고.

### 4. MCP 품질 검증 도구

- **MCP Inspector**(공식, `npx @modelcontextprotocol/inspector`): Node.js ^22.7.5 필요, UI 기본 localhost:6274, proxy 6277, 기본 세션 토큰 인증. Tools 탭에서 스키마·description·실행 결과·raw JSON-RPC 확인. CLI 모드로 CI 자동화 가능(`--method tools/list`), exit code로 pass/fail. [Augment Code](https://www.augmentcode.com/mcp/mcp-inspector) **첫 관문**: Inspector가 연결/툴 나열 못 하면 에이전트도 못 한다. 주의: stdout에 비-JSON 출력(print/log)이 섞이면 stdio JSON-RPC 파서가 깨진다 → 로깅은 stderr로.
- **mcp-eval / mcp-agent**(lastmile-ai, docs.mcp-agent.com): 어서션 API 4범주 —
    - 정확성: `Expect.content.contains`, `Expect.tools.output_matches`
    - 툴 사용: `Expect.tools.was_called`, `Expect.tools.sequence`, `Expect.tools.was_called_with`
    - 성능: `Expect.performance.response_time_under`, `Expect.performance.max_iterations`
    - 품질: `Expect.judge.llm`, `Expect.judge.multi_criteria`
    - 경로 효율: `Expect.path.efficiency(expected_tool_sequence, allow_extra_steps, tool_usage_limits)`
    - `@task` 데코레이터, [Medium](https://medium.com/@anil.goyal0057/the-complete-guide-to-testing-mcp-server-applications-a-three-layer-test-pyramid-for-ai-powered-027e941be6d4) `mcpeval.yaml` 필수, [Medium](https://medium.com/@anil.goyal0057/the-complete-guide-to-testing-mcp-server-applications-a-three-layer-test-pyramid-for-ai-powered-027e941be6d4) OpenTelemetry `.jsonl` 트레이스 출력, `mcp-eval generate`로 테스트 자동 생성.
- **mcp-compliance**(YawLabs): 8개 카테고리 88개 테스트, A-F 등급, 버전된 JSON 리포트(schemaVersion, specVersion). [GitHub](https://github.com/YawLabs/mcp-compliance)
- **계약 테스트 원칙**: 각 툴을 API 계약으로 취급 → 스키마 드리프트·레이턴시·derived content 회귀 감지. In-memory 유닛 테스트(FastMCP Client / TS InMemoryTransport, 서브초 피드백) → 스키마 validation(CI에서 계약 드리프트 차단) → Inspector conformance 순으로 계층화. 복잡 스키마의 \$ref/anyOf는 일부 클라이언트가 취약하므로 Inspector로 실제 노출 스키마 확인.


### 5. Claude Code / Gemini CLI 등록·호환성

```
- **Claude Code**: 프로젝트 스코프 `.mcp.json`(루트), 사용자 `~/.claude.json`, `claude mcp add <name> <command>`. [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) 설정 정밀도: **managed > project > user > local**. `managed-settings.json` + `managed-mcp.json`으로 IT 강제 정책(예: `Bash(curl *)` deny — 어떤 하위 스코프도 오버라이드 불가). `strictKnownMarketplaces`(마켓플레이스 allowlist), `allowManagedHooksOnly`, `disableAllHooks`로 공급망 통제. MCP 출력은 `MAX_MCP_OUTPUT_TOKENS`(기본 25,000)로 제어.
```

- **Gemini CLI**: `~/.gemini/settings.json` 또는 `.gemini/settings.json`의 `mcpServers` 블록, [Google](https://docs.cloud.google.com/cloud-assist/configure-mcp) `gemini mcp <add|list|remove>`. [Phil Schmid](https://www.philschmid.de/gemini-cli-cheatsheet) Extensions는 `gemini-extension.json`(mcpServers, `contextFileName`=GEMINI.md, `excludeTools`; `${extensionPath}` 이식성 참조). 시크릿은 `"$MY_KEY"` 환경변수 확장 권장, `*TOKEN*/*SECRET*/*PASSWORD*/*KEY*/*AUTH*/*CREDENTIAL*` 자동 redaction(env에 명시하면 informed consent로 예외). 툴 병합은 "가장 제한적 정책 승리"(excludeTools union, includeTools intersection). Policy Engine(.toml, tier 2)·skills/·agents/(preview) 지원, `gemini --checkpointing`으로 파일 수정 전 스냅샷.
- **호환성 요약**: 두 클라이언트 모두 stdio + Streamable HTTP, `mcpServers` JSON 키를 공유하므로 **서버 자체는 이식 가능**. 차이는 컨텍스트 파일(CLAUDE.md vs GEMINI.md), 확장 패키징(plugin vs extension), 신뢰/승인 UX, redaction 정책. 생성 에이전트는 양쪽 config를 모두 산출하도록 설계.


### 6. MCP 보안 (사양 필수 통제 + 실제 사고)

**사양 필수 통제**(2025-06-18 = 2025-11-25 동일 문구, `security_best_practices` + `authorization`):

- **토큰 패스스루 금지**: "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server." [github](https://github.com/johnzfitch/claude-wiki/blob/master/06-MCP-Tools/General/mcp-specification-2025-11-25-basic-security-best-practices.md) "MCP clients MUST NOT send tokens to the MCP server other than ones issued by the MCP server's authorization server."
- **RFC 8707 Resource Indicators**: "MCP clients MUST implement Resource Indicators for OAuth 2.0 ... resource 파라미터는 authorization·token 요청 모두에 포함, MCP 서버의 canonical URI 사용." [Model Context Protocol](https://modelcontextprotocol.io/specification/draft/basic/authorization) "MCP servers MUST validate that access tokens were issued specifically for them as the intended audience." [Model Context Protocol](https://modelcontextprotocol.io/specification/draft/basic/authorization) 유효하지 않은/만료 토큰은 HTTP 401.
- **세션**: "MCP servers MUST NOT use sessions for authentication", "MUST use secure, non-deterministic session IDs"(UUID·secure RNG), "SHOULD bind session IDs to user-specific information"(`<user_id>:<session_id>` — ID를 추측당해도 타 사용자 가장 불가).
- **로컬 서버 원클릭 설정**: "MUST implement proper consent mechanisms prior to executing commands" — 실행 명령 전체를 truncation 없이 표시, 위험 작업(sudo, rm -rf) 경고, 명시적 승인, stdio로 접근 제한.
- **Confused deputy(proxy 서버)**: "MUST implement per-client consent" — 사용자별 승인 `client_id` 레지스트리를 3rd-party 인증 흐름 개시 **전에** 확인, redirect_uri 정확 문자열 일치(와일드카드 금지), state 파라미터(암호학적 랜덤, 단회용, 10분 만료, consent 승인 후에만 쿠키 설정), `__Host-` 접두 + Secure/HttpOnly/SameSite=Lax 쿠키.
- **스코프 최소화**(2025-11-25): 최소 초기 스코프(예: `mcp:tools-basic`) + WWW-Authenticate scope 챌린지로 증분 상승. 와일드카드/omnibus 스코프(`*`, `all`, `full-access`) 금지.

**실제 사고/연구**:

- **mcp-remote CVE-2025-6514**: JFrog Security Research(Or Peles) 2025-07-09 공개, CVSS 9.6 OS 커맨드 인젝션, v0.0.5–0.1.15 영향·v0.1.16 수정, 437,000+ 다운로드. "the first time that full remote code execution is achieved in a real-world scenario on the client operating system when connecting to an untrusted remote MCP server"(JFrog).
- **Cursor CVE-2025-54136(MCPoison)·CVE-2025-54135(CurXecute)**: config swap/rug pull — 승인된 key name을 신뢰하고 command content를 재검증하지 않는 허점.
- **Postmark MCP 백도어**(2025-09): 유지관리자가 공식 패키지에 BCC 로직 추가로 전 메일 탈취(패키지 서명이 행위를 보증하지 못함).
- **arXiv:2508.12538 "Systematic Analysis of MCP Security"**(Guo, Liu, Ma, Deng, Zhu, Di, Xiao, Wen): 배포된 1,800+ MCP 서버를 조사해 "over 30 percent had at least one exploitable vulnerability".
- **MCPTox 벤치(arXiv:2508.14925, Wang et al., AAAI 2026)**: 45개 실제 MCP 서버·353개 authentic tools·1,312개 악성 테스트케이스. 최고 공격성공률 **o1-mini 72.8%**이며 "more capable models are often more susceptible"(강한 모델이 오히려 더 취약). 최강 방어 모델 **Claude-3.7-Sonnet조차 거부율 3% 미만**("highest refused rate ... less than 3%") — "모델이 알아서 걸러줄 것"이라는 가정은 성립하지 않음.
- 스캐너 노이즈 주의: YARA 기반 MCP 스캐너에서 ~78% false positive 보고(AppSec Santa) — 원시 "X% 취약" 수치는 방법론 편차 큼.
- rug pull 완화 연구: ETDI(서명된 JWT에 툴 정의 바인딩, 정의 변경 시 서명 무효화) 제안.


### 7. Claude Agent Skills (2단계)

- **포맷**: skill 폴더 안 `SKILL.md`(YAML frontmatter + Markdown body). [Hidekazu-konishi](https://hidekazu-konishi.com/entry/claude_code_skills_complete_guide.html) 필수 frontmatter는 `name`, `description` **두 개뿐**. 선택: `allowed-tools`, `license`, 모델 오버라이드. [Lee Hanchung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) 선택 디렉터리 `scripts/`(실행 Python/Bash), `references/`(필요시 로드 문서), `assets/`(템플릿/폰트).
- **Progressive disclosure 3단계**: (1) frontmatter name+description만 시작 시 로드(스킬당 ~60~100 토큰), (2) 관련 판단/명시 호출 시 SKILL.md body 로드(권장 <5,000 토큰 / <500줄), (3) 참조 파일은 실제 필요 시에만. [Anthropic](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) 8개 스킬 예시: 전부 로드 시 ~70,000 토큰 → progressive로 시작 ~500 토큰, 임의 시점 ~2,000 토큰(70-90% 절감).
- **배포 경로**: 개인 `~/.claude/skills/`, 프로젝트 `.claude/skills/`, plugin 제공, built-in. [Lee Hanchung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) Agent Skills 오픈 표준(agentskills.io, 2025-12-18 발표)은 Claude, OpenAI Codex, Gemini CLI, Cursor, VS Code 등 26+ 플랫폼 채택 → 이식성 확보.
- **description이 트리거 정확도의 핵심**: "무엇을 하는지 + 언제 쓰는지" 둘 다 명시. description이 모호하면 스킬이 자동 발화하지 않아 매번 명시 호출해야 하는 실패가 흔하다. Claude 모델은 SKILL.md 포맷을 네이티브 이해하므로 "스킬 작성 스킬" 없이도 생성 가능.


### 8. Skills vs MCP vs Subagent vs Slash Command 선택 기준

- **MCP** = 배관(외부 시스템/DB/사내 API 연결, live 서버, 실제 tools/resources/prompts). 세션 시작 시 툴 정의가 시스템 프롬프트에 로드되어 컨텍스트 소비. [Substack](https://smithhorngroup.substack.com/p/choosing-between-skills-subagents) [Obot AI](https://obot.ai/resources/learning-center/mcp-anthropic/)
- **Skill** = 지식/절차(체크리스트, 하우스 스타일, 반복 워크플로우, 번들 스크립트). auto-detection 가치가 큰 **대형 도메인 지식**에 적합. progressive disclosure로 70-90% 토큰 절감. [Substack](https://smithhorngroup.substack.com/p/choosing-between-skills-subagents)
- **Slash command** = 사용자가 통제하는 명시적 트리거(`/name`). 서브에이전트/스킬을 파이프라인으로 호출 가능.
- **Subagent** = 격리된 컨텍스트 창의 병렬 워커(긴 코드리뷰, 깊은 리서치, 컨텍스트 오염 방지). 각자 컨텍스트·토큰 독립 소비(과다 병렬 시 사용량 급증).
- **흔한 실수**: 커밋 메시지 포맷을 Skill로(→ CLAUDE.md), 배포 체크리스트를 Skill로(→ slash command), GitHub 접근을 Skill에 기대(→ MCP). "plugin vs skill"은 갈림길이 아니다 — skill은 역량 단위, plugin은 배포 단위.
- **Gemini CLI 매핑**: GEMINI.md(컨텍스트=CLAUDE.md), extensions(패키징=plugin), custom commands(=slash), skills/(SKILL.md 동일 표준), sub-agents(preview).


### 9. 워크플로우 아키텍처 (3단계)

Anthropic "Building Effective Agents"(2024-12) 핵심: **워크플로우**(LLM·툴이 사전 정의된 코드 경로로 오케스트레이션) vs **에이전트**(LLM이 자기 프로세스·툴 사용을 동적 지휘). [Anthropic](https://www.anthropic.com/engineering/building-effective-agents) "가장 단순한 해법부터, 필요할 때만 복잡도 추가" — 에이전트 시스템을 아예 안 만드는 것도 선택지(에이전트는 latency·비용을 정확도와 맞바꿈). 프레임워크는 프롬프트를 가리고 과설계를 유발하므로 **direct LLM API부터** 권장.
워크플로우 패턴과 사용 시점:

- **Prompt chaining**: 각 LLM 호출이 앞 출력을 처리. 결정론적 순차 태스크.
- **Routing**: 입력 분류 → 전문 후속 태스크. 고객 문의 등 입력 카테고리가 뚜렷할 때.
- **Parallelization**: sectioning(독립 서브태스크 병렬)·voting(동일 태스크 다회 실행 후 집계). 속도·다관점 신뢰도.
- **Orchestrator-workers**: 중앙 LLM이 동적 분해·위임·종합. 서브태스크를 예측 불가한 멀티파일 코딩/리서치.
- **Evaluator-optimizer**: 생성-평가 피드백 루프.
Agent Skills는 별개 축(범용 에이전트 위 도메인 전문성을 on-demand 로드) — 워크플로우 우선 규율을 대체하지 않고 보완.


### 10. 에이전트 프레임워크 비교 (사내 배포 관점)

| 프레임워크 | 아키텍처 | 내구성/상태 | HITL | 사내 배포 적합성 | 비고 |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **LangGraph** | 그래프(명시적 state) | durable checkpointing, resume, time-travel | 일급 interrupt | 규제/승인 많은 장기 워크플로우 1순위 | 모델 무관, 가장 많은 프로덕션 마일리지(Klarna/Uber/LinkedIn) |
| **Claude Agent SDK** | Claude Code 엔진(배터리 포함) | 내장 상태 persistence 없음(직접 관리) | 권한 프롬프트/hooks | "repo/filesystem에서 일하는 Claude"에 최적 | MCP 통합 최심, TS/Python 패키지 |
| **OpenAI Agents SDK** | handoff 체인 | 상태 persistence 없음(직접) | harness 승인/resume 트레이싱 | OpenAI 스택 팀 | 2026-04 sandbox 실행 추가, 경량 |
| **Google ADK** | A2A 프로토콜 | — | — | GCP/Vertex 팀 | 1.0(Java/Go) |
| **Microsoft Agent Framework** | SK+AutoGen 통합 | — | — | Azure/.NET 팀 | 1.0 GA 2026-04-03 |
| **CrewAI** | role-based crew | 상대적 약함 | — | 빠른 프로토타입(→프로덕션은 LangGraph 재구현 흔함) | MCP 네이티브(`crewai-tools[mcp]`) |
| **Temporal** | durable execution 엔진 | 최강 내구·재시도·재생 | 워크플로우 신호 | 장기·fault-tolerant 자동화의 신뢰성 척추 | 에이전트 프레임워크와 병용 |

권고: 3단계 워크플로우 자동화에서 **결정론적 장기 승인 흐름은 LangGraph 또는 Temporal**, **코드/파일 조작형은 Claude Agent SDK**. 모든 주요 프레임워크가 2025-2026에 MCP를 툴 통합 표준으로 수렴 → MCP 툴은 프레임워크 간 이식 가능. 단순 분류/추출/2-툴 조회는 프레임워크 없이 단일 API 호출로 충분(하네스는 오버헤드).

### 11. 평가·운영 안정성 (핵심)

- **평가 방법론**: 골든 데이터셋(≥30 케이스 회귀셋), task success rate, tool-call accuracy(정확한 툴 선택+파라미터), trajectory evaluation, LLM-as-judge(한계: judge 자체가 비결정적·"stably wrong" 가능). **3계층 전략** — deterministic 로직(라우팅·파싱·상태전이)은 매 커밋 유닛테스트(`pytest -m "not llm_eval"`), 품질 차원(faithfulness/relevance/coherence/hallucination 0.0~1.0 임계)은 eval 테스트, 전체 태스크는 online eval.
- **비결정성 다루기**: judge temperature=0, pass/fail 기준 최대한 구체화(무엇이 pass인지 나열), 각 케이스 3회 실행 majority-vote, 동일 케이스가 10%+ 뒤집히면 기준 재작성. **pass^k/pass@k**로 "k회 중 1회 이상 성공 확률" [arxiv](https://arxiv.org/pdf/2404.05520) 통계 판정. **UNSTABLE을 CI 실패 상태로 취급**(단일 pass rate 대신 agreement 보고 — "95% pass at 0.6 judge agreement is noise"). judge·agent 모델 버전 pinning. 3-of-5 flip을 60% pass로 평균내면 회귀가 숨는다.
- **회귀 게이트**: 골든셋 key metric ±3% 임계 초과 시 빌드 실패(비협상 품질 게이트), canary 5% 트래픽 + online eval을 control과 비교, eval delta 통계 유의성(노이즈 초과) 확인 후에만 100% 승격. no-LLM 결정론적 replay를 CI 1차 게이트로(빠르고 저렴).
- **관측**: OpenTelemetry GenAI semantic conventions(`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens/output_tokens`; `invoke_agent`/`execute_tool`/model/workflow 스팬 + latency·token 메트릭). **단 v1.41 기준 대부분 `gen_ai.*` 속성이 Development 안정성 badge** — 속성명이 major bump 없이 바뀔 수 있으므로 semantic convention 버전 pinning 필수. OpenInference(tool_call 상관 속성) 병용. [MLflow](https://mlflow.org/articles/setting-up-llm-observability-pipelines-in-2026/) OpenLLMetry 등 auto-instrumentation으로 LLM 클라이언트 스팬 즉시 확보 → 에이전트/툴 스팬 수동 추가.
- **실패 복구**: 재시도(idempotent 보장), timeout, guardrail(입력/출력 스크리닝), fallback 모델, circuit breaker, 사용자에게 정직한 실패 통지(성공으로 위장 금지 — 에이전트는 "well-formed but wrong"으로 실패).
- **배포 후 수정 어려움 대응**: feature flag, remote config(프롬프트·모델 버전 원격 전환), canary 단계적 롤아웃, 버전 호환성 유지.


### 12. Eval/Observability 프레임워크 셀프호스팅 (폐쇄망)

| 도구 | 셀프호스팅 | 라이선스/비용 | 강점 | 폐쇄망 주의점 |
| :-- | :-- | :-- | :-- | :-- |
| **Langfuse** | ✅ Docker/K8s | 오픈소스 MIT, 무료 | 트레이싱·세션 리플레이·프롬프트 관리·비용 추적, 전 프레임워크 통합 | FOSS는 SOC2/ISO 미포함, SSO·고급 RBAC은 유료 키. ClickHouse/Redis/PostgreSQL/S3 운영 부담. eval 워크플로우는 상대적 약함 |
| **Arize Phoenix** | ✅ | 오픈소스(Elastic License 2.0), 무료 | OpenInference/OTel 네이티브, Phoenix Evals, notebook 친화 | 유료는 Arize AX(\$50/월~), 전사 UX는 span-tree 중심 |
| **Braintrust** | ✅(엔터프라이즈) | proprietary, 관대한 무료 티어(1M spans/월) | eval-gated CI/CD 최강, 회귀 감지, 릴리스 통제 연결 | 셀프호스팅은 엔터프라이즈 계약 |
| **DeepEval** | ✅(로컬) | 오픈소스 | Python 로컬 eval, CI 적합 | 관측보다 eval 중심 |
| **LangSmith** | 제한적 | proprietary, 볼륨 과금 | LangChain/LangGraph 통합 최강 | 외부 SaaS 전송, 폐쇄망 부적합 |
| **Promptfoo / Ragas** | ✅ | 오픈소스 | 프롬프트/RAG eval | 보조 도구 |

**폐쇄망 1순위 권고: Langfuse(트레이싱·비용·프롬프트 버전) + DeepEval/mcp-eval(CI eval) + OpenTelemetry 계측.** Langfuse는 2026년 1월 16일 ClickHouse가 \$400M Series D(밸류 \$15B)와 동시에 인수 발표했으나 공동창업자 Max Deichmann이 "Langfuse stays open source and self-hostable"라 확인(MIT 유지, 2025년 말 기준 GitHub 20K+ stars, 월 26M+ SDK installs). "best" 순위 상당수가 벤더 블로그(Latitude/Braintrust)이므로 자체 PoC 검증 필수.

### 13. 사내 배포 (거버넌스·채택)

- **Claude Code 플러그인/마켓플레이스**: plugin = 배포 단위(skills+agents+hooks+MCP servers+LSP 번들, `.claude-plugin/plugin.json`), marketplace = 카탈로그(repo의 `.claude-plugin/marketplace.json`). 팀 배포는 프로젝트 `.claude/settings.json`의 `extraKnownMarketplaces`+`enabledPlugins` → 팀원이 repo 신뢰 시 자동 설치 프롬프트. [Agent Wikis](https://agentwikis.com/wiki/claude-code/wiki/entities/plugin-marketplaces.md) plugin은 MCP 서버를 `.mcp.json`(plugin 루트)로 선언해 자동 기동. `claude plugin details <name>`로 always-on/per-invoke 토큰 비용 사전 확인. **plugin은 사용자 권한으로 임의 코드 실행 → 신뢰 소스만.** managed 스코프는 불변(admin 설치). Anthropic은 3rd-party plugin 내용을 검증하지 않음.
- **거버넌스**: **리스크 비례 원칙**(저위험 내부 실험은 며칠 내 승인, 후보 심사자·크리덴셜 접근·파괴적 작업은 심층 심사). MCP 레지스트리/게이트웨이로 등록·승인된 툴만 프로덕션 실행. [Obot AI](https://obot.ai/blog/ai-governance-trends-2026/) 감사로그(워크플로우 버전·사용자 액션·툴 호출). [Stackai](https://www.stackai.com/insights/enterprise-ai-adoption-2026-trends-benchmarks-and-best-practices-for-scalable-success) 리뷰 프로세스: 툴 정의 서명·해시 고정(rug pull 방지), allowlist. ISO/IEC 42001, NIST AI RMF(GOVERN/MAP/MEASURE/MANAGE), EU AI Act(일반 조항 2026-08-02 적용) [Hymalaia](https://www.hymalaia.com/blog/enterprise-ai-governance-best-practices-for-2026-en) 참조. IBM: 87% 기업이 "명확한 거버넌스" 주장하나 25% 미만만 실제 통제 구현 — 문서가 아닌 실행 규율이 관건.
- **채택률**: 프로젝트 스코프 plugin으로 팀 전원 동일 툴 자동 확보, 온보딩 문서/사용 가이드, 미승인 툴 사용 급증은 "처벌"이 아니라 "정식 도입 검토 신호"로 해석.


## Details

### MCP 서버 최소 예제 (FastMCP, Python)

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

### .mcp.json (Claude Code 프로젝트 스코프)

```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "${CRM_TOKEN}" }
    }
  }
}
```


### Gemini CLI settings.json

```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "$CRM_TOKEN" },
      "includeTools": ["search_customers"]
    }
  }
}
```


### SKILL.md 예제

```markdown
---
name: crm-report-writer
description: Generate weekly CRM retention reports from internal CRM data. Use when the user asks for a retention report, churn summary, or weekly customer health digest.
allowed-tools: ["internal-crm__search_customers"]
---

# CRM Retention Report

## When to use
사용자가 "리텐션 리포트", "이탈 요약", "주간 고객 건강도"를 요청할 때.

## Steps
1. `search_customers`로 대상 세그먼트 조회 (concise 모드).
2. references/report_template.md 형식에 맞춰 작성.
3. 수치는 반드시 툴 출력에 근거. 추정 금지.

## Validation
- 모든 고객 ID가 실제 조회 결과에 존재하는지 확인.
```

description은 "무엇을+언제"를 모두 담아 트리거 정확도 확보. body는 <500줄, 상세 문서는 `references/`로 분리.

### mcp-eval 테스트 케이스 예제

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


### CI 회귀 게이트 (GitHub Actions 골자)

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


### 3단계 로드맵 실행 계획

**1단계 (MCP 서버 생성 에이전트, 최우선)**

- 생성 에이전트 = Claude Code 기반 오케스트레이터. 입력: 대상 API/도메인 설명(+ llms.txt·SDK 문서). 산출: (a) FastMCP 서버 코드, (b) `.mcp.json`/Gemini `settings.json` 샘플, (c) mcp-eval 테스트 케이스, (d) MCP Inspector conformance 스크립트, (e) README·보안 체크리스트.
- 생성 에이전트에 Anthropic 5원칙을 시스템 프롬프트/Skill로 고정. 툴 개수 최소화·네임스페이싱·`response_format` enum·25k 토큰 제한·helpful error를 강제 규칙화.
- 게이트: 생성 직후 자동으로 Inspector 연결 + mcp-eval 실행. 통과 못 하면 배포 산출 금지("배포 후 회수 불가" 대응).

**2단계 (Skills/프롬프트팩 생성)**

- SKILL.md 생성 에이전트. description 품질 검사기(트리거 시뮬레이션: 실제 요청 문장 10개로 발화율 측정) 내장. body <500줄 강제, 상세는 `references/`.
- 프롬프트팩/스킬은 사내 GitHub repo에서 버전 관리, plugin으로 패키징해 마켓플레이스 배포. 개인→프로젝트→plugin 순으로 승격.

**3단계 (워크플로우 자동화)**

- 결정론적으로 표현 가능한 것은 워크플로우(chaining/routing)로, 예측 불가한 것만 에이전트로. LangGraph(durable checkpoint·HITL interrupt) 또는 Temporal(내구 실행) 위에 사내 API 커넥터를 MCP 툴로.
- 시크릿은 환경변수 확장·keychain·사내 secret manager. **업로드 불가 제약상 사내→외부 데이터 유출 경로를 allowlist로 차단**, 다운로드는 허용.


## Recommendations

**즉시 (0~4주)**

1. MCP 사양 버전을 **2025-11-25 stable**로 고정(pinning). 신규 서버는 stdio(로컬)+Streamable HTTP(원격), SSE 금지.
2. 생성 에이전트 v0를 Claude Code로 구축: FastMCP 서버 + mcp-eval 케이스 + Inspector 스크립트를 한 번에 산출. Anthropic 5원칙을 Skill로 고정.
3. Langfuse 셀프호스팅(Docker) + OpenTelemetry GenAI conventions 계측을 파일럿 프로젝트에 붙임. semantic convention 버전 pinning.

**단기 (1~3개월)**
4. CI 회귀 게이트 구축: 골든셋 ≥30케이스, judge temperature=0·3회 majority-vote, ±3% 임계, 모델/judge 버전 pinning. UNSTABLE=실패.
5. 사내 GitHub에 `.claude-plugin/marketplace.json` 레지스트리 생성. `managed-settings.json` + `strictKnownMarketplaces` + `managed-mcp.json`으로 IT 승인 공급망 강제.
6. 보안 통제 구현: 토큰 audience 검증(RFC 8707), [Model Context Protocol](https://modelcontextprotocol.io/specification/draft/basic/authorization) allowlist, 툴 정의 서명/해시 고정(rug pull 방지), non-deterministic 세션 ID, 감사로그, mcp-remote 등 의존성 CVE 스캔.

**중기 (3~6개월)**
7. 2단계 Skills 생성 에이전트 + description 트리거 검사기.
8. canary 롤아웃(5% + online eval), feature flag/remote config로 "배포 후 수정 불가" 완화.
9. 3단계 워크플로우: LangGraph/Temporal + 사내 API 커넥터, HITL 승인 게이트.

**변경 트리거(벤치마크)**

- 골든셋 pass rate <90% 또는 judge agreement <0.8 → 배포 중단.
- 모델 버전 업그레이드 시 회귀셋 재실행 필수(회귀 감지되면 pin 유지).
- tool-call error율 >5% → description 재작성.
- MCP 사양이 2026-07-28 RC로 정식화되면 stateless core·Roots/Sampling deprecated 대응 재평가.

**배포 전 체크리스트**

- [ ] MCP 사양 버전 pinning(2025-11-25), transport = stdio/Streamable HTTP만
- [ ] 툴 개수 최소화, 네임스페이싱, `user_id`류 명확한 파라미터명
- [ ] 응답 25k 토큰 제한, 페이지네이션/필터/truncation, helpful error 메시지
- [ ] MCP Inspector conformance 통과, 스키마 \$ref/anyOf 클라이언트 호환 확인, stdout 오염 없음
- [ ] mcp-eval 골든셋 ≥30, pass rate ≥90%, pass^k 통계 판정
- [ ] judge·agent 모델 버전 pinning, judge temperature=0, UNSTABLE=실패
- [ ] 토큰 audience 검증(RFC 8707), 세션 non-deterministic ID + user 바인딩, 로컬 원클릭 consent
- [ ] 툴 정의 서명/해시 고정(rug pull), allowlist, 최소 권한 스코프(와일드카드 금지)
- [ ] 감사로그(툴 호출·사용자·버전), OpenTelemetry 계측(semantic convention 버전 pin)
- [ ] 의존성 CVE 스캔(mcp-remote 등), 사내→외부 업로드 차단 경로 확인
- [ ] fallback 모델·timeout·circuit breaker·정직한 실패 통지
- [ ] feature flag/remote config, canary 롤아웃 경로
- [ ] plugin 배포 스코프(project), managed 거버넌스 설정(`strictKnownMarketplaces`)


## Caveats

- **최신성**: MCP 사양은 매우 빠르게 진화한다. 2026-07-28 RC(stateless core, MCP Apps, Tasks 확장) [Hidekazu-konishi](https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html) 는 조사 시점 기준 release candidate이며 정식화 시 core가 stateless로 바뀌므로 세션/전송 설계 재검토 필요. Roots/Sampling/Logging deprecated도 RC 기준 예고 사항이다.
- **OAuth 세부는 버전 민감**: RFC 8707 `resource` MUST 요구는 GitHub Issue \#1614에서 SHOULD로 완화 논의 중 [GitHub](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1614) 이고, Dynamic Client Registration은 2025-11-25에서 SHOULD→MAY로 강등되며 CIMD로 대체되었다. [MojoAuth](https://mojoauth.com/blog/how-mcp-authorization-actually-works-oauth-2-1-resource-servers-and-resource-indicators) 인증 구현 전 해당 리비전 원문 재확인 권장. (토큰 패스스루 금지·audience 검증·RFC 9728 protected-resource-metadata·OAuth 2.1 resource-server 역할은 두 리비전 공통 유지.)
- **불확실 수치**: FastMCP "70% 점유율·하루 100만 다운로드"는 FastMCP/PrefectHQ 자체 주장( [GitHub](https://github.com/PrefectHQ/fastmcp) 1차 검증 아님). Anthropic Slack/Asana MCP 개선 그래프의 정확한 수치는 이미지로만 제공되어 텍스트 추출 불가 — 인용 가능한 확정 수치는 Opus 4 49%→74%, Opus 4.5 79.5%→88.1%(Tool Search Tool), [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use) 툴 description 개선의 "40% task completion time 감소" [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) 뿐이다.
- **eval 프레임워크 비교 출처 편향**: Langfuse/Braintrust/Phoenix 비교 상당수가 벤더(Latitude, Braintrust 등) 블로그다. 셀프호스팅 무료·오픈소스 사실관계는 일치하나, "best" 평가는 마케팅 스핀 가능성 있어 자체 PoC로 검증 권장. Langfuse의 ClickHouse 인수 후 라이선스 정책도 장기적으로 재확인 필요(현재 MIT·셀프호스팅 유지 확인됨).
- **보안 통계**: arXiv:2508.12538 "배포 서버 30%+ 취약", MCPTox(arXiv:2508.14925) "o1-mini ASR 72.8%·Claude-3.7-Sonnet 거부율 <3%"는 학술 벤치 조건 기준이며, YARA 스캐너 78% false positive 보고처럼 방법론에 따라 편차가 크다. 절대 수치보다 통제 원칙(allowlist·서명·audience 검증)의 채택이 핵심.
- **CVE 특정성**: CVE-2025-6514(mcp-remote), CVE-2025-54135/54136(Cursor)은 특정 클라이언트/패키지 버전 취약점이다. 사내 구축 서버가 자동으로 취약한 것은 아니며, 해당 컴포넌트 사용 시에만 해당된다.
- **엔터프라이즈 3사 버전 사용 관점**: 본 보고서는 Claude Code·Gemini CLI 중심으로 검증했다. OpenAI Agents SDK/Codex 경로도 MCP·Agent Skills 오픈 표준을 지원하므로 이식 가능하나, 구체 config·redaction 정책은 별도 검증이 필요하다.

상기내용관련 추가 정밀 보강자료 수집
추가적으로 간단하고 사용자 입장에서 놓치기 쉬운데 적용하면 좋을 것들 정리하자.
최신 트렌드.오픈소스나 선도 기업 사례들 조사해 가지고 정리해 주고 리스크는 작은데 적용했을 때 사용자 입장에서 편리하고 좋은 것 그리고 ROI 좀 높은 것들.
기존 문서 조사했던 것처럼 다양한 방면에서 다양한 카테고리로 조사를 해 가지고 AI한테 참고 문서로 줄 수 있는 형태로 작성을 해 주면 더 좋을 거 같아.

Gemini cli claude code에서 설계 팁, 알면 좋은 단축키나 자주 쓰는 고급 프롬프트 등등(내가 준 내용에 비는 내용은 알아서 채워줘)

아래는 요청하신 내용을 바탕으로, **사내 AI 협업용 “툴 생성 에이전트”를 실제로 설계할 때 바로 참고할 수 있는 보강 리서치 메모**입니다. 최신 흐름은 MCP를 “연결 표준”으로, Skills를 “절차/도메인 지식 표준”으로, Claude Code/Gemini CLI를 “실사용 운영면”으로 분리해 다루는 방향이 강합니다. 또한 2026년 기준 실무 트렌드는 관측 가능한 품질, 최소 권한, 팀 단위 배포 거버넌스, 그리고 CLI 중심 생산성 기능의 표준화로 수렴하고 있습니다 [^1_1][^1_2][^1_3][^1_4][^1_5].

## 무엇을 더 넣을지

당장 체감 ROI가 큰 항목은 “더 많은 기능”보다 **운영·보안·재사용·관측**입니다. 특히 사내 도입에서는 툴 수를 늘리기보다, 툴 호출 품질과 실패 복구를 높이는 쪽이 효과가 큽니다 [^1_6][^1_5][^1_2].

- **툴 생성 에이전트의 기본 산출물 세트**를 고정하십시오: 서버 코드, 스키마, README, 보안 체크리스트, Inspector 검증 명령, eval 케이스, 샘플 config까지 한 번에 내게 하세요. Claude의 공식 Best Practices는 “증거를 보여주라”와 “작업을 좁혀라”를 강조하고, MCP 서버는 `/mcp`와 `claude mcp add`로 운영하기 쉽게 설계하는 것이 유리합니다 [^1_2][^1_3].
- **설계 원칙은 ‘적은 툴 + 높은 의미’**가 좋습니다. 검색형은 `list_xxx`보다 `search_xxx`, 상태 조회형은 `get_customer_context`처럼 에이전트가 바로 쓰기 쉬운 형태가 더 낫습니다 [^1_1][^1_6].
- **배포 전 검증은 Inspector + 골든셋 + 토큰 효율**을 묶어야 합니다. 특히 생성형 에이전트는 “만들기”보다 “검증 가능한 형태로 함께 만들기”가 핵심입니다 [^1_2][^1_3][^1_5].


## 빠르게 ROI 나는 항목

아래는 적용 난이도 대비 효과가 큰 것들입니다.


| 항목 | 효과 | 난이도 | 왜 좋은가 |
| :-- | --: | --: | :-- |
| `CLAUDE.md` / `GEMINI.md` 표준화 | 높음 | 낮음 | 팀 전체의 작업 규칙을 한 곳에 고정할 수 있습니다 [^1_2][^1_7] |
| scoped MCP token / read-only token | 높음 | 낮음 | 사고 반경을 바로 줄입니다 [^1_6][^1_5] |
| Inspector CI 게이트 | 높음 | 중간 | 스키마 드리프트를 초기에 잡습니다 [^1_3][^1_5] |
| Langfuse + OTel tracing | 높음 | 중간 | “왜 잘/못 됐는지”가 남아 개선이 쉬워집니다 [^1_4][^1_8] |
| slash command 템플릿화 | 중간~높음 | 낮음 | 반복 작업을 빠르게 표준화합니다 [^1_2][^1_9] |
| hooks로 금지/필수 규칙 강제 | 높음 | 중간 | 사람이 잊어도 시스템이 막습니다 [^1_2][^1_10] |
| plugins로 배포 단위 묶기 | 높음 | 중간 | 팀 배포와 롤백이 쉬워집니다 [^1_6][^1_2] |
| subagent 분리 | 중간 | 낮음 | 긴 작업의 컨텍스트 오염을 줄입니다 [^1_11][^1_7] |

## 놓치기 쉬운 실무 팁

실무에서 자주 놓치는 부분은 “기술”보다 “사용자 경험”과 “운영 마찰”입니다. 여기에 신경 쓰면 내부 채택률이 올라갑니다.

- **에러 메시지는 사람이 바로 고칠 수 있게** 쓰는 것이 좋습니다. Claude 공식 가이드도 불투명한 traceback보다 “무엇을 고쳐야 하는지”를 주는 메시지를 권장합니다 [^1_2].
- **stdout 오염 금지**는 매우 중요합니다. MCP stdio 서버는 JSON-RPC 파서가 깨지기 쉬우므로 로그는 stderr로 보내야 합니다 [^1_3][^1_5].
- **권한 요청은 한 번에 넓게 주지 말고 점진적으로** 올리세요. 2026년 보안 가이드들은 최소 스코프, resource indicators, per-server credentials를 강하게 권고합니다 [^1_5][^1_12].
- **토큰/비밀키는 환경별로 분리**하고, 서버별로 별도 credential을 두는 것이 좋습니다. 이건 보안뿐 아니라 디버깅에도 유리합니다 [^1_6][^1_5].


## Claude Code 팁

Claude Code 쪽은 “작업 범위 통제”와 “증거 기반 결과 확인”이 핵심입니다. 공식 문서와 최신 가이드들에서 반복적으로 강조되는 부분입니다 [^1_2][^1_3][^1_11].

- `/init`로 `CLAUDE.md` 초안을 만든 뒤, 팀 규칙을 거기에 고정하는 방식이 좋습니다 [^1_2].
- `/doctor`는 환경 문제를 먼저 잡는 데 유용합니다 [^1_11].
- `/plugin`으로 팀 공유 플러그인을 관리하고, `claude mcp add`로 외부 도구를 연결하는 구조가 가장 자연스럽습니다 [^1_2][^1_3].
- `claude -p` 같은 비대화형 모드는 CI, pre-commit, 자동 리팩터링 파이프라인에 잘 맞습니다 [^1_2].
- 작업 지시를 줄 때는 “파일명, 시나리오, 기대 결과”를 같이 주는 것이 좋습니다. 예: “`foo.py`에 대해 로그인이 풀린 상태의 경계 케이스 테스트 추가, mock 최소화” [^1_2].


## Gemini CLI 팁

Gemini CLI는 설정 파일과 확장 구조가 비교적 명확해서, 팀 표준화에 잘 맞습니다. 최신 참조들에서는 `gemini mcp`, `gemini extensions`, `gemini skills`를 함께 쓰는 흐름이 보입니다 [^1_13][^1_9].

- `gemini mcp add`로 MCP 서버를 등록하고, 필요하면 project scope로 묶는 방식이 안전합니다 [^1_13].
- `Ctrl+L`은 화면 정리성 측면에서 유용합니다 [^1_9].
- custom slash command와 extension을 분리하면, 개인 단축명령과 팀 표준을 깔끔히 나눌 수 있습니다 [^1_13].
- checkpointing을 활용하면 파일 수정형 작업에서 실수 복구가 쉬워집니다 [^1_13].
- `excludeTools`와 include 정책을 쓰면, 필요한 도구만 보여주는 제한적 UI를 만들 수 있습니다 [^1_13].


## 고급 프롬프트 패턴

아래 패턴은 Claude Code든 Gemini CLI든 공통으로 잘 먹힙니다. 핵심은 “결과물의 형식”과 “검증 기준”을 같이 주는 것입니다 [^1_2][^1_10].

1. **제약 우선형**
    - “먼저 설계안 3개를 비교표로 제시하고, 그다음 추천 1개만 구현해라.”
2. **검증 우선형**
    - “코드만 쓰지 말고, 실패 케이스와 확인 명령까지 함께 써라.”
3. **증거 우선형**
    - “주장 대신 로그, 테스트 결과, 스키마 출력으로 확인해라.”
4. **분리형**
    - “추론, 구현, 검증을 단계별로 분리해서 출력해라.”
5. **회귀 방지형**
    - “기존 행동을 깨는 변경이 있으면 반드시 호환성 노트를 적어라.”

이 방식은 Claude의 Best Practices가 권장하는 “scope the task”, “show evidence”, “use tools for external systems”와 잘 맞습니다 [^1_2].

## 사내 참고문서용 구성

사내 AI가 참고하기 좋게 하려면, 문서를 다음 구조로 정리하는 것이 좋습니다. 이렇게 하면 나중에 툴 생성 에이전트가 자동 생성/검증하기 쉬워집니다.

- **A. 표준 설계 원칙**
    - 툴 네이밍.
    - 입력 스키마.
    - 출력 규격.
    - 실패 응답 규칙.
- **B. 보안 기본값**
    - 최소 권한.
    - allowlist.
    - per-server credential.
    - 감사 로그.
- **C. 운영 표준**
    - Inspector.
    - eval 골든셋.
    - tracing.
    - rollback 절차.
- **D. UX 표준**
    - 응답 길이.
    - 요약/상세 모드.
    - 에러 메시지 템플릿.
- **E. CLI 작업 패턴**
    - slash command.
    - hooks.
    - plugin.
    - subagent.
    - MCP server.


## 추천하는 “추가 보강” 우선순위

지금 문서에 이어서 가장 먼저 보강하면 좋은 순서는 아래입니다.

1. **Claude Code / Gemini CLI 운영 표준화 섹션**
    - 단축키, 자주 쓰는 명령, `/init`, `/doctor`, `claude -p`, `gemini mcp`, `gemini skills`.
2. **사내 배포 거버넌스 섹션**
    - plugin registry, allowlist, managed settings, 승인 프로세스.
3. **관측/평가 섹션**
    - Langfuse, OpenTelemetry GenAI conventions, 회귀 게이트.
4. **보안 실천 체크리스트**
    - token scope, resource indicators, egress control, stdout 분리.
5. **에이전트 설계 패턴 라이브러리**
    - prompt chaining, routing, evaluator-optimizer, orchestrator-worker.

## 한 줄 결론

실무적으로 가장 ROI가 큰 건 **“툴을 잘 만드는 에이전트”보다 “검증·배포·관측까지 자동으로 붙는 에이전트”**입니다. 그리고 사용자 입장에서 편한 건 대부분 “작은 자동화”에 있습니다: 표준 프롬프트, 단축 명령, 안전한 기본값, 짧은 결과 요약, 실패 시 바로 고칠 수 있는 메시지입니다 [^1_2][^1_3][^1_4][^1_5].

원하시면 다음 단계로 바로 이어서 **“사내 참고문서 초안” 형식으로 재구성**해서,

- 1) 개요,
- 2) 추천 아키텍처,
- 3) Claude Code/Gemini CLI 운영 팁,
- 4) 체크리스트,
- 5) 샘플 `CLAUDE.md` / `GEMINI.md`,
- 6) 샘플 고급 프롬프트 템플릿

까지 한 번에 붙여 넣을 수 있게 정리해드리겠습니다.
<span style="display:none">[^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28]</span>

<div align="center">⁂</div>

[^1_1]: https://www.morphllm.com/claude-code-skills-mcp-plugins

[^1_2]: https://code.claude.com/docs/en/best-practices

[^1_3]: https://code.claude.com/docs/en/mcp

[^1_4]: https://langfuse.com/integrations/native/opentelemetry

[^1_5]: https://agentmelt.com/blog/mcp-security-2026-attacks-and-defenses/

[^1_6]: https://www.clarista.io/blog/claude-code-mcp-plugins-guide

[^1_7]: https://hidekazu-konishi.com/entry/claude_code_features_settings_reference_2026.html

[^1_8]: https://langfuse.com/self-hosting/configuration/observability

[^1_9]: https://geminicli.com/docs/reference/commands/

[^1_10]: https://www.marktechpost.com/2026/06/14/claude-code-guide-2026-25-features-with-examples-demo/

[^1_11]: https://support.claude.com/en/articles/14553413-claude-code-cheatsheet

[^1_12]: https://dreaming.press/posts/2026-06-22-mcp-authorization-oauth.html

[^1_13]: https://computingforgeeks.com/gemini-cli-cheat-sheet/

[^1_14]: https://angelo-lima.fr/en/claude-code-cheatsheet-2026-update/

[^1_15]: https://blakecrosley.com/guides/claude-code-cheatsheet

[^1_16]: https://www.linkedin.com/pulse/build-production-ready-ai-agents-2026-mcp-cli-skills-agarwaal-ox3jc

[^1_17]: https://techbytes.app/posts/claude-code-2026-cheat-sheet-hooks-mcp-commands/

[^1_18]: https://dev.to/gabrielanhaia/opentelemetry-genai-semantic-conventions-your-llm-traces-should-look-like-this-in-2026-3ff6

[^1_19]: https://john-hodge.com/blog/opentelemetry-genai-semantic-conventions/

[^1_20]: https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions

[^1_21]: https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/

[^1_22]: https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke

[^1_23]: https://effloow.com/articles/langfuse-llm-observability-self-host-guide-2026

[^1_24]: https://awesomeclaude.ai/code-cheatsheet

[^1_25]: https://claudefa.st/blog/guide/changelog

[^1_26]: https://github.com/luongnv89/claude-howto/blob/main/01-slash-commands/README.md

[^1_27]: https://explainx.ai/blog/claude-code-keyboard-shortcuts-complete-reference-2026

[^1_28]: https://toolsbase.dev/en/reference/claude-code-commands


---

# “사내 참고문서 초안” 형식으로 재구성해서,

개요,
추천 아키텍처,
Claude Code/Gemini CLI 운영 팁,
체크리스트,
샘플 CLAUDE.md / GEMINI.md,
샘플 고급 프롬프트 템플릿
까지 한 번에 붙여 넣을 수 있게 정리

아래는 바로 붙여 넣어 쓸 수 있는 형태의 **사내 참고문서 초안**입니다. Claude Code, Gemini CLI, MCP, Skills, 관측/보안, 그리고 팀 운영 팁까지 한 문서에 넣을 수 있게 구성했습니다 [^2_1][^2_2][^2_3][^2_4].

***

# 사내 AI 협업용 툴 생성 에이전트 참고문서 초안

## 1. 개요

이 문서는 사내 AI 협업 환경에서 사용할 **툴 생성 에이전트**의 운영 기준과 실무 템플릿을 정의한다. 목표는 “코드를 대신 써주는 에이전트”가 아니라, **검증 가능한 도구·문서·테스트·설정 파일까지 함께 생성하는 에이전트**를 만드는 것이다 [^2_1][^2_2].
핵심 원칙은 단순하다: 툴은 적게, 의미는 크게, 검증은 자동으로, 배포는 통제 가능하게 가져간다 [^2_5][^2_6][^2_7].
이 문서는 Claude Code와 Gemini CLI를 공통 운영축으로 삼고, MCP는 연결 계층, Skills는 절차/도메인 지식 계층, hooks와 plugins는 거버넌스/배포 계층으로 분리해 다룬다 [^2_1][^2_3][^2_4].

## 2. 추천 아키텍처

권장 구조는 **3층**이다. 1층은 MCP 서버와 외부 시스템 연결, 2층은 Skills와 slash command로 반복 업무 표준화, 3층은 hooks와 CI eval로 품질을 강제하는 운영층이다 [^2_1][^2_2][^2_4].
MCP 서버는 프로젝트별로 최소한만 넣고, 공통으로 정말 필요한 서버만 전역화한다. 최근 실무 가이드들은 “2~3개 핵심 MCP부터 시작하고 나머지는 필요할 때만 활성화”하는 방식을 권장한다 [^2_8][^2_7].
평가/관측은 Langfuse와 OpenTelemetry 계열을 붙여, 세션·툴 호출·응답 품질·비용을 추적하는 것이 좋다 [^2_9][^2_10][^2_11].

### 구조 요약

- **MCP 서버**: 사내 DB, GitHub, 문서, 이슈 트래커, 웹 검색 등 외부 시스템 연결 [^2_2][^2_4].
- **Skills**: 반복되는 절차, 체크리스트, 도메인 규칙, 산출물 템플릿 [^2_5][^2_6].
- **Hooks**: 승인, 검사, 포맷 검증, 금지 명령 차단 같은 결정론적 규칙 [^2_1][^2_8].
- **CI/Eval**: Inspector, 골든셋, 회귀 테스트, 성능/정확도 측정 [^2_2][^2_12].
- **Observability**: Langfuse + OpenTelemetry tracing [^2_9][^2_10][^2_11].


## 3. Claude Code 운영 팁

Claude Code는 “작업을 잘 나누는 것”이 중요하다. 공식 문서도 연구와 구현을 분리하고, 구체적 컨텍스트와 검증 수단을 함께 주라고 권장한다 [^2_1].
`/init`로 `CLAUDE.md` 초안을 만든 뒤, 팀 규칙과 자주 쓰는 빌드/테스트 명령을 거기에 넣는 방식이 가장 안정적이다 [^2_1].
`/doctor`는 환경 문제를 빨리 잡는 데 유용하고, `auto mode`나 allowlist 기반 권한 설정은 반복 승인 스트레스를 줄여준다 [^2_1].
플러그인과 MCP는 함께 쓰되, 프로젝트별로 분리하는 것이 좋다. 전역 MCP를 너무 많이 두면 컨텍스트와 관리 복잡도가 같이 늘어난다 [^2_6][^2_7].

### 추천 사용 습관

- 작업 전에 **목표, 제약, 검증 기준**을 짧게 적는다.
- 코드 생성 전에 **계획 → 구현 → 검증** 순서를 명시한다.
- 결과를 받을 때는 “어떻게 확인할지”까지 같이 달라고 요청한다.
- 리뷰 전에는 테스트/빌드/스냅샷 비교를 먼저 수행한다 [^2_1].


## 4. Gemini CLI 운영 팁

Gemini CLI는 설정 파일 기반 운영이 명확해서, 팀 단위 표준화에 잘 맞는다. `mcpServers`와 `mcp` 설정으로 서버 허용 범위와 실행 규칙을 통제할 수 있다 [^2_3][^2_4].
`/mcp`로 서버를 관리하고, `/settings`로 환경 설정을 확인하는 습관을 들이면 운영이 단순해진다 [^2_3].
custom slash command와 extensions를 나누면 개인용 자동화와 팀용 자동화를 분리하기 쉽다 [^2_13][^2_4].
checkpointing을 켜두면 파일 수정 작업에서 되돌리기가 편하고, `excludeTools` 같은 제한 정책은 과도한 도구 노출을 줄이는 데 유리하다 [^2_13][^2_4].

### 추천 사용 습관

- 프로젝트마다 필요한 MCP만 등록한다.
- 비밀값은 환경변수로 주고 설정 파일에 평문으로 넣지 않는다.
- 개인용 단축어와 팀 표준을 분리한다.
- 파일 수정형 작업은 checkpoint를 기본으로 둔다 [^2_13][^2_4].


## 5. 체크리스트

이 체크리스트는 실제 배포 전에 자동 점검용으로 쓰기 좋다. 특히 사내 도입에서는 “만들 수 있느냐”보다 “안전하게 반복 실행되느냐”가 더 중요하다 [^2_2][^2_12][^2_8].

### 설계 체크

- 툴 이름이 목적을 바로 드러내는가.
- `list_*`보다 `search_*`, `get_*`, `create_*`처럼 행동이 분명한가 [^2_5].
- 출력이 너무 장황하지 않고, 요약/상세 모드를 구분하는가.
- 오류 메시지가 사용자가 고칠 수 있는 정보로 되어 있는가 [^2_1].


### 보안 체크

- 토큰은 서버별로 분리되어 있는가.
- 최소 권한만 부여되어 있는가.
- 감사 로그가 남는가.
- stdout에는 로그가 섞이지 않는가.
- 위험 명령은 승인 또는 차단되는가 [^2_2][^2_12].


### 품질 체크

- Inspector로 툴 목록과 스키마가 확인되는가.
- 골든셋 회귀 테스트가 있는가.
- 실패 케이스와 경계값 테스트가 포함되어 있는가.
- 응답 시간과 tool-call 수가 측정되는가 [^2_2][^2_11].


### 운영 체크

- 프로젝트별 `.mcp.json` 또는 설정 파일로 분리했는가.
- 필요 없는 서버는 비활성화했는가.
- 문서와 구현이 함께 버전 관리되는가.
- 롤백 경로와 feature flag가 있는가 [^2_6][^2_7].


## 6. 샘플 CLAUDE.md

아래는 팀 프로젝트용 최소 예시다.

```md
# CLAUDE.md

## Project Goal
이 프로젝트는 내부 업무 자동화와 문서화를 위한 툴 생성 에이전트를 만든다.

## Working Rules
- 구현 전에 짧은 계획을 먼저 제시한다.
- 코드 변경 후 반드시 테스트 방법을 함께 제시한다.
- 불확실한 부분은 추측하지 말고 확인 질문을 한다.
- 외부 시스템 연동은 MCP 서버 또는 승인된 API만 사용한다.
- 위험한 작업은 먼저 명시적으로 경고하고 승인을 받는다.

## Code Style
- 함수명은 동작이 드러나게 쓴다.
- 툴명은 search/get/create/update 패턴을 우선 사용한다.
- 출력은 concise / detailed 같은 명확한 모드를 지원한다.

## Testing Rules
- 새 기능에는 최소 1개 성공 케이스와 1개 실패 케이스를 추가한다.
- 스키마 변경이 있으면 Inspector로 확인한다.
- 회귀 가능성이 있으면 골든셋 테스트를 추가한다.

## Build / Run
- 설치:
  - `uv sync`
- 테스트:
  - `pytest -q`
- 서버 실행:
  - `python -m app.server`

## Safety
- stdout에 디버그 로그를 출력하지 않는다.
- 비밀값은 환경변수로만 주입한다.
- 허용되지 않은 외부 전송은 하지 않는다.
```

이런 식으로 CLAUDE.md는 **짧고 실행 가능해야** 한다. 너무 긴 규칙 문서는 오히려 실제 작업에 덜 쓰인다 [^2_14][^2_15][^2_1].

## 7. 샘플 GEMINI.md

Gemini CLI 쪽은 설정과 작업 규칙을 분리해 두면 좋다.

```md
# GEMINI.md

## Project Purpose
사내 협업용 AI 툴 생성 및 검증 작업을 위한 표준 운영 문서.

## Working Rules
- 작업 시작 전에 목표, 제약, 검증 기준을 먼저 적는다.
- MCP 서버는 프로젝트 범위로 우선 등록한다.
- 결과는 요약과 상세를 구분해서 출력한다.
- 파일 수정이 필요한 작업은 checkpoint를 사용한다.
- 위험한 변경은 바로 실행하지 말고 확인을 요청한다.

## Preferred Workflow
1. 계획 작성
2. 변경안 제시
3. 검증 명령 실행
4. 결과 요약
5. 필요한 경우 롤백

## Tool Usage
- 필요한 MCP만 활성화한다.
- 쓰지 않는 서버는 끈다.
- 비밀값은 환경변수로 주입한다.
- 외부 공개용 도구와 내부 전용 도구를 분리한다.

## Output Style
- 짧은 결론 → 근거 → 실행 명령 순서로 작성한다.
- 실패 원인과 수정 방법을 분리해서 설명한다.
```

Gemini CLI는 `/mcp`, `/settings`, custom commands, extensions를 활용해 이런 규칙을 실제 환경에 맞게 고정하기 좋습니다 [^2_3][^2_4][^2_13].

## 8. 샘플 고급 프롬프트

아래 템플릿은 Claude Code/Gemini CLI 공통으로 쓸 수 있다.

### 설계 요청형

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


### 구현 요청형

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


### 검증 요청형

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


### 리팩터 요청형

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


### 운영 자동화 요청형

```text
이 작업을 운영 자동화 관점으로 정리해줘.

필수 항목:
- 반복 가능한 절차
- 실패 지점
- 로그/관측 포인트
- 승인 필요한 단계
- 롤백 방법
```


## 9. 실무적으로 바로 쓰는 권장안

가장 현실적인 시작점은 다음 순서다. 먼저 **CLAUDE.md/GEMINI.md를 얇게** 만들고, 그다음 **프로젝트별 MCP 2~3개만 붙이고**, 마지막으로 **hooks와 eval**을 얹는 방식이 좋다 [^2_8][^2_7][^2_1].
그 다음에 Skills를 추가해 반복 작업을 줄이고, plugin이나 extension으로 팀 배포 단위를 묶는다 [^2_5][^2_16][^2_4].
이 순서는 “기능 과잉”을 막고, 사용자 입장에서 가장 체감이 큰 부분부터 개선하는 데 유리하다 [^2_14][^2_7].

원하시면 다음 단계로 이어서
**“이 문서를 그대로 사내 위키에 올릴 수 있는 완성본”** 형태로

- 표지,
- 목차,
- 정책 문구,
- 운영 절차,
- 예시 config,
- FAQ

까지 포함한 버전으로 다듬어드리겠습니다.
<span style="display:none">[^2_17]</span>

<div align="center">⁂</div>

[^2_1]: https://code.claude.com/docs/en/best-practices

[^2_2]: https://code.claude.com/docs/en/mcp

[^2_3]: https://geminicli.com/docs/reference/commands/

[^2_4]: https://geminicli.com/docs/tools/mcp-server/

[^2_5]: https://www.morphllm.com/claude-code-skills-mcp-plugins

[^2_6]: https://mcp.directory/blog/claude-code-best-practices

[^2_7]: https://www.linkedin.com/pulse/claude-code-survival-guide-2026-skills-agents-mcp-servers-rob-foster-lq9we

[^2_8]: https://dev.to/valgard/claude-code-must-haves-january-2026-kem

[^2_9]: https://langfuse.com/integrations/native/opentelemetry

[^2_10]: https://langfuse.com/self-hosting/configuration/observability

[^2_11]: https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions

[^2_12]: https://agentmelt.com/blog/mcp-security-2026-attacks-and-defenses/

[^2_13]: https://computingforgeeks.com/gemini-cli-cheat-sheet/

[^2_14]: https://news.creeta.com/en/claude-code-best-practices-2026/

[^2_15]: https://github.com/shanraisshan/claude-code-best-practice

[^2_16]: https://www.clarista.io/blog/claude-code-mcp-plugins-guide

[^2_17]: https://www.superdevacademy.com/en/blogs/claude-ai-2026-guide-coding-tips-tricks


---

# 첫번째 질의 내용 포함해서

문서를 그대로 사내 위키에 올릴 수 있는 완성본” 형태로
표지,
목차,
정책 문구,
운영 절차,
예시 config,
FAQ

최대한 구체적이고 쉽고 유용하며
다양하고 사례중심으로 정리해줘

아래 문서는 그대로 사내 위키에 올릴 수 있도록 **완성본 초안** 형태로 정리했습니다. 핵심은 “툴 생성 에이전트”를 단순 코드 생성기가 아니라 **검증 가능한 산출물 생산 체계**로 운영하는 것입니다 [^3_1][^3_2][^3_3].

***

# 사내 AI 협업용 툴 생성 에이전트 운영 표준

**문서 목적**
사내 AI 협업 환경에서 Claude Code, Gemini CLI, MCP, Skills, Hooks, Plugins를 안전하고 일관되게 운영하기 위한 표준을 정의한다. 이 문서는 툴 생성, 검증, 배포, 관측, 보안을 하나의 흐름으로 묶어 팀 단위 재사용을 가능하게 하는 것을 목표로 한다 [^3_1][^3_2][^3_4].

**적용 범위**

- 사내 AI 툴 생성 에이전트
- Claude Code 기반 개발/운영 작업
- Gemini CLI 기반 개발/운영 작업
- MCP 서버, Skills, Hooks, Plugins, Subagents
- 평가(Eval), 관측(Observability), 보안 거버넌스 [^3_1][^3_5][^3_6][^3_7]

**문서 원칙**

1. 툴은 적게, 의미는 크게 설계한다.
2. 검증 가능한 결과만 채택한다.
3. 기본값은 안전해야 하며, 예외는 명시적으로 승인한다.
4. 반복되는 업무는 사람이 아니라 시스템이 기억하게 한다.
5. 배포 후 수정이 어렵다고 가정하고 처음부터 회수 가능하게 설계한다 [^3_1][^3_8][^3_3].

***

## 목차

1. 개요
2. 권장 아키텍처
3. 역할 분담: MCP / Skills / Hooks / Plugins / Subagents
4. 운영 절차
5. Claude Code 운영 가이드
6. Gemini CLI 운영 가이드
7. 정책 문구
8. 예시 설정 파일
9. 체크리스트
10. FAQ
11. 부록: 프롬프트 템플릿

***

## 1. 개요

이 체계의 목적은 AI가 “그럴듯한 답”을 내는 것이 아니라, **실행 가능한 작업 결과**를 안정적으로 만드는 데 있다. 따라서 에이전트는 코드, 설정, 테스트, 문서, 검증 절차를 한 세트로 생성해야 한다 [^3_1][^3_2].
현업에서 가장 효과가 좋은 구조는 “연결은 MCP, 지식은 Skills, 강제는 Hooks, 배포는 Plugins, 복잡 작업은 Subagents”로 나누는 방식이다 [^3_3][^3_9].
이 구조를 쓰면 팀마다 다른 업무라도 공통 운영 원칙을 유지할 수 있고, 새 사람이 와도 규칙을 빠르게 학습할 수 있다 [^3_1][^3_10].

### 핵심 효과

- 반복 작업 시간 단축.
- 잘못된 실행과 권한 오남용 감소.
- 도구 품질의 회귀 방지.
- 팀 전체 작업 방식의 표준화 [^3_1][^3_7].

***

## 2. 권장 아키텍처

권장 아키텍처는 3층 구조다.

### 2.1 연결층

MCP 서버가 사내 DB, GitHub, 문서 저장소, 이슈 트래커, 검색 시스템을 연결한다. 이 계층은 “실제 일을 하는 도구”이므로 프로젝트 범위별로 최소한만 활성화하는 것이 좋다 [^3_2][^3_3][^3_4].

### 2.2 지식층

Skills는 반복되는 업무 절차와 도메인 규칙을 담는다. 예를 들어 “주간 보고서 작성”, “릴리즈 노트 생성”, “보안 점검”, “코드 리뷰 절차” 같은 것은 Skill로 만드는 편이 훨씬 효율적이다 [^3_11][^3_3].
이 계층은 사람이 자주 잊는 규칙, 예외 처리, 템플릿, 체크리스트를 담아 둔다.

### 2.3 통제층

Hooks, permission mode, allowlist, CI eval, Inspector, logging, tracing이 이 층에 해당한다. 이 계층은 에이전트가 잘못된 행동을 하기 전에 막거나, 잘못했을 때 추적 가능하게 만든다 [^3_1][^3_2][^3_5][^3_7].
특히 “실행 전 차단”보다 “작업 완료 시 검증”이 사용자 경험에 유리한 경우가 많다. 최근 실무 가이드도 과도한 중간 차단보다 최종 검증형 훅을 선호한다 [^3_10].

***

## 3. 역할 분담

### 3.1 MCP

MCP는 외부 시스템 접근 계층이다. 데이터 조회, 작업 생성, 메시지 전송, 문서 검색처럼 **실제로 호출되어야 하는 기능**은 MCP가 맡는다 [^3_2][^3_4].
MCP 서버는 가능한 한 작고 명확해야 하며, search/get/create/update 같은 명확한 동사형 툴이 좋다 [^3_11][^3_1].

### 3.2 Skills

Skills는 지식과 절차를 담는다. “언제 이 작업을 써야 하는가”, “어떤 순서로 처리해야 하는가”, “무엇을 출력해야 하는가”를 정의한다 [^3_11][^3_3].
반복 빈도가 높은 업무는 Skill로 만들어 두면, 매번 장문의 프롬프트를 입력하지 않아도 된다.

### 3.3 Hooks

Hooks는 사내 정책을 강제한다. 예를 들어 포맷 검사, 금지 명령 차단, 경고 출력, 승인 요청, 커밋 전 검증을 자동화할 수 있다 [^3_1][^3_10].
Hooks는 “언제나 적용되어야 하는 규칙”에 적합하다.

### 3.4 Plugins

Plugins는 배포 단위다. 여러 Skills, Hooks, MCP 서버를 한 묶음으로 패키징해 팀 단위로 배포할 수 있다 [^3_12][^3_3].
플러그인 방식은 온보딩과 롤백이 쉬워서, 내부 표준 배포에 잘 맞는다.

### 3.5 Subagents

Subagents는 긴 작업을 나눌 때 유용하다. 예를 들어 설계, 구현, 검증, 문서화를 별도 에이전트로 분리할 수 있다 [^3_3][^3_9].
이 방식은 컨텍스트 오염을 줄이고, 병렬 처리로 속도를 높이는 데 유리하다.

***

## 4. 운영 절차

### 4.1 새 툴을 만들 때

1. 문제를 한 문장으로 정의한다.
2. 입력/출력 스키마를 정한다.
3. 툴 이름을 명확하게 정한다.
4. 성공 케이스와 실패 케이스를 같이 만든다.
5. Inspector로 호출 가능 여부를 확인한다.
6. 골든셋 테스트를 추가한다.
7. 문서와 샘플 config를 같이 저장한다 [^3_2][^3_1].

### 4.2 배포 전

1. 위험 권한이 있는지 확인한다.
2. 토큰과 인증 범위를 점검한다.
3. stdout 로그 오염이 없는지 확인한다.
4. 로컬과 원격 설정을 분리한다.
5. eval을 통과해야만 배포한다 [^3_2][^3_7].

### 4.3 운영 중

1. 사용자 피드백과 실패 로그를 모은다.
2. 자주 나오는 작업은 Skill로 승격한다.
3. 반복 실패는 Hook 또는 schema 수정으로 처리한다.
4. 비용이 큰 툴은 호출 횟수와 출력 길이를 점검한다.
5. 회귀가 발견되면 즉시 버전 고정 또는 롤백한다 [^3_5][^3_6][^3_13].

### 4.4 변경 관리

- 툴 정의를 바꿀 때는 반드시 버전 기록을 남긴다.
- 구조적 변경은 CI eval 재실행 후 배포한다.
- 권한/토큰/연결 설정은 문서와 함께 업데이트한다.
- 새 팀원이 들어오면 “사용법”보다 먼저 “금지 사항”을 보여준다 [^3_1][^3_7].

***

## 5. Claude Code 운영 가이드

Claude Code는 작업의 질을 높이려면 “범위와 검증”을 같이 주는 것이 중요하다 [^3_1].
`/init`로 프로젝트용 `CLAUDE.md`를 만들고, 팀 규칙과 빌드/테스트 명령을 짧게 유지한다 [^3_1].
`/doctor`는 환경 이상을 빠르게 찾는 데 유용하다 [^3_14].
프로젝트 스코프 MCP는 승인 흐름이 붙기 때문에, 민감한 내부 서버는 전역보다 프로젝트 단위로 두는 편이 안전하다 [^3_2].

### Claude Code 권장 습관

- 작업 전 “무엇을 만들지”보다 “어떻게 확인할지”를 먼저 적는다.
- 하나의 요청에 너무 많은 목표를 섞지 않는다.
- 관련 파일과 제약을 구체적으로 지정한다.
- 결과를 받을 때는 코드와 검증 방법을 같이 받는다 [^3_1].


### 자주 쓰는 패턴

- “먼저 계획만.”
- “구현은 나중.”
- “테스트 포함.”
- “실패 케이스 추가.”
- “호환성 유지.” [^3_1][^3_10].

***

## 6. Gemini CLI 운영 가이드

Gemini CLI는 설정 중심 운영에 적합하다. `mcpServers`와 command 기반 구성이 명확해서, 팀 규칙을 파일로 관리하기 좋다 [^3_15][^3_4].
custom command와 extension을 나누면 개인용 자동화와 팀용 자동화를 구분할 수 있다 [^3_16].
checkpointing이 가능한 작업은 적극 활용하는 것이 좋고, 필요한 툴만 포함시키는 방향이 운영 안정성에 유리하다 [^3_16][^3_4].

### Gemini CLI 권장 습관

- 프로젝트별 설정 파일을 사용한다.
- 비밀값은 환경변수로만 주입한다.
- 개인용 command와 팀 표준 command를 분리한다.
- 변경 전 체크포인트를 남긴다 [^3_16][^3_15].


### 자주 쓰는 운영 포인트

- MCP 서버 추가/삭제를 명시적으로 관리한다.
- tool allowlist를 최소화한다.
- output 스타일을 짧은 요약과 상세 설명으로 나눈다 [^3_15][^3_4].

***

## 7. 정책 문구

아래 문구는 위키 상단 또는 운영 규정 섹션에 그대로 넣어도 된다.

### 7.1 툴 설계 정책

- 툴은 하나의 목적만 가져야 한다.
- 하나의 툴이 너무 많은 일을 하면 분리한다.
- 툴 이름은 동작이 드러나야 한다.
- 실패 메시지는 사용자가 바로 고칠 수 있어야 한다 [^3_1][^3_11].


### 7.2 보안 정책

- 승인되지 않은 서버는 연결하지 않는다.
- 토큰은 서버별로 분리한다.
- 최소 권한 원칙을 따른다.
- 외부 콘텐츠를 가져오는 서버는 prompt injection 위험을 고려한다.
- stdout에는 로그를 섞지 않는다 [^3_2][^3_7].


### 7.3 운영 정책

- 배포는 문서, 코드, 테스트, 설정이 함께 있어야 한다.
- 회귀 테스트가 없으면 프로덕션 반영하지 않는다.
- 사용자 영향이 큰 변경은 단계적으로 롤아웃한다.
- 문제가 생기면 우선 롤백 가능성을 본다 [^3_5][^3_6].


### 7.4 품질 정책

- 설명은 짧고 명확해야 한다.
- 반복되는 업무는 Skill로 승격한다.
- 긴 작업은 Subagent 또는 단계형 워크플로우로 분리한다.
- 결과는 반드시 검증 가능한 형태여야 한다 [^3_3][^3_9].

***

## 8. 예시 설정 파일

### 8.1 Claude Code .mcp.json 예시

```json
{
  "mcpServers": {
    "internal-search": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_search.server"],
      "env": {
        "SEARCH_API_KEY": "${SEARCH_API_KEY}"
      }
    },
    "internal-docs": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_docs.server"],
      "env": {
        "DOCS_API_KEY": "${DOCS_API_KEY}"
      }
    }
  }
}
```


### 8.2 Claude Code CLAUDE.md 예시

```md
# CLAUDE.md

## Project Goal
사내 AI 협업용 툴 생성 및 검증 자동화

## Rules
- 먼저 계획을 제시한다.
- 코드는 테스트와 함께 작성한다.
- 외부 시스템은 승인된 MCP만 사용한다.
- 위험한 작업은 사전 경고를 넣는다.
- 결과는 짧은 요약과 상세로 나눈다.

## Verification
- 성공 케이스 1개 이상
- 실패 케이스 1개 이상
- 스키마 확인
- 회귀 체크리스트 포함
```


### 8.3 Gemini CLI settings 예시

```json
{
  "mcpServers": {
    "internal-search": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_search.server"],
      "env": {
        "SEARCH_API_KEY": "$SEARCH_API_KEY"
      }
    }
  },
  "excludeTools": [
    "unapproved-dangerous-tool"
  ]
}
```


### 8.4 Gemini CLI GEMINI.md 예시

```md
# GEMINI.md

## Project Goal
사내 업무 자동화 및 검증 중심 AI 협업

## Working Rules
- 작업 전 목표와 검증 기준을 먼저 적는다.
- 필요한 MCP만 사용한다.
- checkpoint 가능한 작업은 반드시 체크포인트를 남긴다.
- 비밀값은 환경변수로만 관리한다.

## Output Style
- 먼저 결론
- 다음 근거
- 마지막 실행 방법
```


### 8.5 Sample Skill 예시

```md
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


***

## 9. 체크리스트

### 도입 전

- [ ] 프로젝트별 MCP 서버만 등록했는가.
- [ ] 권한 범위를 최소화했는가.
- [ ] 팀 규칙을 CLAUDE.md / GEMINI.md로 정리했는가.
- [ ] 기본 검증 명령이 문서화되어 있는가.
- [ ] 비밀값이 평문으로 들어가지 않는가.


### 배포 전

- [ ] Inspector 검증을 통과했는가.
- [ ] 실패 케이스를 포함한 테스트가 있는가.
- [ ] 회귀를 확인했는가.
- [ ] stdout 오염이 없는가.
- [ ] 롤백 경로가 있는가.


### 운영 중

- [ ] 자주 쓰는 요청이 Skill로 승격되었는가.
- [ ] 반복 오류가 Hook 또는 정책으로 정리되었는가.
- [ ] 관측 데이터가 누적되는가.
- [ ] 사용자 불편 사항이 문서에 반영되는가.
- [ ] 정기적으로 사용하지 않는 툴을 정리하는가.

***

## 10. FAQ

### Q1. 왜 MCP를 많이 두지 말라고 하나요?

MCP가 많아질수록 어떤 툴을 언제 써야 하는지 모델이 혼동하기 쉽고, 컨텍스트와 운영 복잡도도 같이 증가한다. 실무에서는 필요한 것부터 적게 시작하는 편이 안정적이다 [^3_3][^3_9].

### Q2. Skills와 MCP 중 무엇이 먼저인가요?

먼저 MCP로 실제 연결이 필요한지 확인하고, 반복되는 절차가 보이면 Skill로 빼는 순서가 좋다. MCP는 “행동”, Skill은 “지식”에 가깝다 [^3_3].

### Q3. Hooks는 어디에 써야 하나요?

반드시 지켜야 하는 규칙에 쓰는 것이 좋다. 예를 들어 포맷 검사, 위험 명령 차단, 승인, 커밋 전 검증 같은 것들이다 [^3_1][^3_10].

### Q4. Claude Code와 Gemini CLI는 무엇이 다른가요?

Claude Code는 프로젝트 맥락과 승인 흐름을 포함한 작업형 에이전트 운영에 강하고, Gemini CLI는 설정/command 중심의 표준화 운영에 잘 맞는다 [^3_2][^3_15][^3_4].
둘 다 MCP를 쓰지만, 설정 파일과 작업 습관은 다르게 가져가는 것이 좋다.

### Q5. 어떤 팀에 가장 효과가 큰가요?

반복 업무가 많고, 여러 도구를 함께 쓰며, 검증/승인/보안이 중요한 팀에 가장 효과가 크다. 특히 개발, 운영, 데이터, 문서화, 내부 자동화 팀에서 ROI가 높다 [^3_5][^3_6][^3_7].

### Q6. 초기에 가장 먼저 해야 할 것은 무엇인가요?

`CLAUDE.md`와 `GEMINI.md`를 짧게 만들고, 프로젝트별 MCP를 2~3개만 붙인 뒤, 테스트와 관측을 추가하는 것이다. 이 순서가 가장 빨리 체감 효과를 준다 [^3_1][^3_8][^3_13].

***

## 11. 부록: 프롬프트 템플릿

### 설계 요청

```text
다음 업무를 자동화할 수 있는 툴 생성 에이전트 구조를 설계해줘.

조건:
- 실제 실행 가능한 설정 파일과 테스트 포함
- MCP, Skills, Hooks 역할을 분리
- 보안과 검증을 기본으로 둘 것

출력:
1. 권장 구조
2. 각 구성요소 역할
3. 배포 전 체크리스트
4. 실패 방지 포인트
```


### 구현 요청

```text
이 기능을 구현해줘.

필수:
- 핵심 코드
- 설정 예시
- 테스트 2개 이상
- 실패 케이스 1개
- 실행 방법
- 운영 시 주의점
```


### 검증 요청

```text
다음 결과물을 검증해줘.

검증 항목:
- 스키마 적합성
- 보안 위험
- 테스트 누락
- 회귀 가능성
- 운영성

출력 형식:
- 문제 없음 / 수정 필요
- 발견된 이슈
- 우선순위
- 바로 적용 가능한 수정안
```


### 리팩터 요청

```text
아래 내용을 리팩터링해줘.

우선순위:
1. 읽기 쉬움
2. 안정성
3. 재사용성

제약:
- 인터페이스 유지
- 기능 유지
- 바뀐 이유를 짧게 설명
```


### 운영 절차 요청

```text
이 작업을 운영 절차 문서 형식으로 정리해줘.

반드시 포함:
- 목적
- 절차
- 승인 단계
- 실패 시 대응
- 롤백 방법
- 체크리스트
```


***

원하시면 다음 단계로는 이 문서를 바로 이어서
**“사내 위키 최종본 스타일”**로 다듬어

- 제목 페이지,
- 버전 정보,
- 승인자/작성자 항목,
- 정책 등급,
- 운영 책임자,
- 관련 문서 링크,
- 변경 이력

까지 포함한 **진짜 배포용 위키 문서 포맷**으로 정리해드리겠습니다.
<span style="display:none">[^3_17][^3_18][^3_19]</span>

<div align="center">⁂</div>

[^3_1]: https://code.claude.com/docs/en/best-practices

[^3_2]: https://code.claude.com/docs/en/mcp

[^3_3]: https://mcp.directory/blog/claude-code-best-practices

[^3_4]: https://geminicli.com/docs/tools/mcp-server/

[^3_5]: https://langfuse.com/integrations/native/opentelemetry

[^3_6]: https://langfuse.com/self-hosting/configuration/observability

[^3_7]: https://agentmelt.com/blog/mcp-security-2026-attacks-and-defenses/

[^3_8]: https://news.creeta.com/en/claude-code-best-practices-2026/

[^3_9]: https://www.linkedin.com/pulse/claude-code-survival-guide-2026-skills-agents-mcp-servers-rob-foster-lq9we

[^3_10]: https://dev.to/valgard/claude-code-must-haves-january-2026-kem

[^3_11]: https://www.morphllm.com/claude-code-skills-mcp-plugins

[^3_12]: https://www.clarista.io/blog/claude-code-mcp-plugins-guide

[^3_13]: https://langfuse.com/docs/observability/sdk/instrumentation

[^3_14]: https://code.claude.com/docs/ko/whats-new/2026-w26

[^3_15]: https://geminicli.com/docs/reference/commands/

[^3_16]: https://computingforgeeks.com/gemini-cli-cheat-sheet/

[^3_17]: https://code.claude.com/docs/es/mcp

[^3_18]: https://code.claude.com/docs/de/mcp

[^3_19]: https://code.claude.com/docs/fr/mcp

