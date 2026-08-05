# 툴 생성 에이전트

> **카테고리**: concept
> **태그**: tool-generation-agent, mcp, skills, workflow, roadmap

---

# 툴 생성 에이전트 - 정의

툴 생성 에이전트는 사내 개발팀이 필요로 하는 MCP 서버, Skills, Hooks, 워크플로우 자동화를 자동으로 생성·검증·배포하는 AI 에이전트입니다. 단순한 "코드 생성기"가 아니라, 검증 하네스가 내장된 생성기로 설계되어야 합니다.

Anthropic 공식 가이드(2025-09-11 "Writing effective tools for agents — with agents")는 툴을 "결정론적 시스템과 비결정론적 에이전트 간의 계약"으로 규정하며, 툴 품질은 프롬프트 엔지니어링과 eval 반복으로만 확보된다고 결론짓습니다. 따라서 생성 에이전트는 MCP 서버 코드와 함께 mcp-eval 테스트 케이스, MCP Inspector 계약 테스트를 동시에 산출해야 "배포 후 회수 불가" 제약을 견딜 수 있습니다.

### 3단계 로드맵

| 단계 | 내용 | 산출물 |
|------|------|--------|
| 1단계 | MCP 서버 생성 에이전트 (최우선) | FastMCP 서버 코드, .mcp.json/Gemini settings, mcp-eval 케이스, Inspector 스크립트, README/보안 체크리스트 |
| 2단계 | Skills/프롬프트팩 생성 | SKILL.md, description 품질 검사기, plugin 패키징, 마켓플레이스 배포 |
| 3단계 | 워크플로우 자동화 | LangGraph/Temporal 기반 결정론적 워크플로우, HITL 승인 게이트 |

### Skills vs MCP vs Subagent vs Slash Command 선택 기준

| 도구 | 역할 | 적합한 용도 |
|------|------|------------|
| MCP | 배관 (외부 시스템/DB/사내 API 연결) | live 서버, 실제 tools/resources/prompts. 세션 시작 시 툴 정의가 컨텍스트 소비 |
| Skill | 지식/절차 (체크리스트, 하우스 스타일, 반복 워크플로우) | 대형 도메인 지식. progressive disclosure로 70-90% 토큰 절감 |
| Slash command | 사용자가 통제하는 명시적 트리거 (/name) | 서브에이전트/스킬을 파이프라인으로 호출 |
| Subagent | 격리된 컨텍스트 창의 병렬 워커 | 긴 코드리뷰, 깊은 리서치, 컨텍스트 오염 방지 |

흔한 실수: 커밋 메시지 포맷을 Skill로 (→ CLAUDE.md), 배포 체크리스트를 Skill로 (→ slash command), GitHub 접근을 Skill에 기대 (→ MCP).

---

# 툴 생성 에이전트 - 설정법

### 생성 에이전트 기본 구성

생성 에이전트는 Claude Code 기반 오케스트레이터로 구축합니다. 입력: 대상 API/도메인 설명(+ llms.txt, SDK 문서). 산출물: (a) FastMCP 서버 코드, (b) .mcp.json/Gemini settings.json 샘플, (c) mcp-eval 테스트 케이스, (d) MCP Inspector conformance 스크립트, (e) README, 보안 체크리스트.

### Anthropic 5원칙 시스템 프롬프트 고정

생성 에이전트에 Anthropic 5원칙을 시스템 프롬프트/Skill로 고정합니다:
1. 올바른 툴 선택: API를 얇게 래핑하지 말고 고레버리지 툴을 소수만 구현
2. 네임스페이싱: 서비스·리소스별 prefix (asana_search, asana_projects_search)
3. 의미 있는 컨텍스트 반환: uuid 대신 name, file_type
4. 토큰 효율: 페이지네이션, range, 필터, truncation 기본값 포함. 응답 25,000 토큰 제한
5. 툴 description 프롬프트 엔지니어링: 신입에게 설명하듯 암묵지 명시화

### 배포 전 자동 게이트

생성 직후 자동으로 Inspector 연결 + mcp-eval 실행. 통과 못 하면 배포 산출 금지 ("배포 후 회수 불가" 대응).

---

# 툴 생성 에이전트 - 운영 가이드

### 워크플로우 아키텍처 패턴

Anthropic "Building Effective Agents" 핵심: 워크플로우(LLM·툴가 사전 정의된 코드 경로로 오케스트레이션) vs 에이전트(LLM이 자기 프로세스·툴 사용을 동적 지휘). "가장 단순한 해법부터, 필요할 때만 복잡도 추가" — 에이전트 시스템을 안 만드는 것도 선택지.

워크플로우 패턴:
- Prompt chaining: 각 LLM 호출이 앞 출력을 처리. 결정론적 순차 태스크
- Routing: 입력 분류 → 전문 후속 태스크. 입력 카테고리가 뚜렷할 때
- Parallelization: sectioning(독립 서브태스크 병렬), voting(동일 태스크 다회 실행 후 집계)
- Orchestrator-workers: 중앙 LLM이 동적 분해·위임·종합. 예측 불가한 멀티파일 코딩/리서치
- Evaluator-optimizer: 생성-평가 피드백 루프

### 점진적 자율성 로드맵

완전 자율성으로 시작하지 마세요. 더 안전한 채택 경로:
1. 에이전트가 테스트를 추가하고 작은 버그를 고치게 한다
2. 저위험 리팩터를 하게 한다
3. 의존성 업데이트와 문서 동기화를 맡긴다
4. 그 다음에야 모듈 간 기능 작업을 시도한다

### 선도 기업 사례

- Block(Goose): 12,000명 직원 전사 배포. 자동 설치·자동 업데이트가 채택률의 근본 해법. LLM 비종속 설계, 동적 MCP 서버 활성화
- Coinbase(Forge): 머지된 PR의 5%, PR 사이클 타임 150시간→15시간
- Uber: LangGraph 기반 Validator·Autocover로 21,000 개발자 시간 절감
- 공통 아키텍처: Slack 호출 → 격리 샌드박스 → CI 루프 → PR-ready 산출물

---

# 툴 생성 에이전트 - 예외 사례

### 실패·안티패턴

- Gartner는 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망. McKinsey는 23%의 기업만이 AI 에이전트를 스케일한다고 봄
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과. 파일럿의 88%는 출시되지 못함
- 내부 헬프데스크가 강력한 첫 에이전트인 이유: 데이터를 소유하고 있고 실패 비용이 낮기 때문
- 비용 사고: 한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금을 기록. Microsoft는 비용 초과로 롤아웃 공개 철회
- 가장 흔한 비용 급증 원인: 서브에이전트 팬아웃(하나의 태스크가 20개 이상 병렬 에이전트 스폰)과 autocompact 루프

### 흔한 실수

- 커밋 메시지 포맷을 Skill로 만들기 (→ CLAUDE.md가 적합)
- 배포 체크리스트를 Skill로 만들기 (→ slash command가 적합)
- GitHub 접근을 Skill에 기대기 (→ MCP가 적합)
- "plugin vs skill"을 갈림길로 보기 — skill은 역량 단위, plugin은 배포 단위

### 주의사항

- 커뮤니티 블로그 비중이 높음. hook 이벤트 개수, 버전 번호, 모델 가격 등은 출처마다 상이
- MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심함. 자체 PoC 필수
- 기업 도입 수치는 대부분 2차 인용. 1차 발표 확인 전까지 참고 수준만
- 가격은 도입기 할인이 걸려 있어 재확인 필요

---

# 툴 생성 에이전트 - 보안 고려사항

### MCP 보안 통제 (사양 필수)

- 토큰 패스스루 금지: "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server."
- RFC 8707 Resource Indicators: resource 파라미터는 authorization·token 요청 모두에 포함
- 세션: "MCP servers MUST NOT use sessions for authentication", secure non-deterministic session IDs (UUID), user-specific binding
- 로컬 서버 원클릭 설정: 실행 명령 전 consent 메커니즘 MUST 구현, 위험 작업 경고
- Confused deputy 방지: per-client consent, client_id 레지스트리, redirect_uri 정확 문자열 일치
- 스코프 최소화: 최소 초기 스코프 + WWW-Authenticate scope 챌린지로 증분 상승. 와일드카드/omnibus 스코프 금지

### 실제 보안 사고

- mcp-remote CVE-2025-6514: CVSS 9.6 OS 커맨드 인젝션, 437,000+ 다운로드
- Cursor CVE-2025-54136(MCPoison), CVE-2025-54135(CurXecute): config swap/rug pull
- Postmark MCP 백도어: 유지관리자가 공식 패키지에 BCC 로직 추가로 전 메일 탈취
- arXiv:2508.12538: 배포된 1,800+ MCP 서버 중 30%+가 최소 하나 이상의 취약점
- MCPTox 벤치: 최고 공격성공률 o1-mini 72.8%, 강한 모델이 오히려 더 취약. Claude-3.7-Sonnet조차 거부율 3% 미만

### rug pull 완화

ETDI(서명된 JWT에 툴 정의 바인딩, 정의 변경 시 서명 무효화) 제안. 툴 정의 서명/해시 고정으로 방지.

---

# 툴 생성 에이전트 - 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [Skills (스킬)](./02-skills.md)
- [Hooks (훅)](./03-hooks.md)
- [MCP (Model Context Protocol)](./04-mcp.md)
- [Subagents (서브에이전트)](./06-subagents.md)
- [컨텍스트 엔지니어링](./08-context-engineering.md)
- [툴 생성 에이전트 설정법 (상세)](../02_setup/04-tool-generation-agent-setup.md)
- [품질 평가 및 CI](../03_operations/04-quality-evaluation-ci.md)
- [비용·성능 최적화](../03_operations/05-cost-performance-optimization.md)
- [배포·채택·거버넌스](../03_operations/06-deployment-adoption-governance.md)
- [에이전트 프레임워크 및 게이트웨이](../05_mcp_catalog/03-agent-frameworks-and-gateways.md)

---

# 툴 생성 에이전트 - 출처

- [Anthropic - Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic - Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic - Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)
- [Anthropic - Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Anthropic - Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Code 공식 문서 - Best Practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code 공식 문서 - MCP](https://code.claude.com/docs/en/mcp)

---

