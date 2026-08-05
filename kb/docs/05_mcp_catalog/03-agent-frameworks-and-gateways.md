# 에이전트 프레임워크 및 게이트웨이

> **카테고리**: catalog
> **태그**: agent-framework, langgraph, claude-agent-sdk, temporal, mcp-gateway, fastmcp

---

# 에이전트 프레임워크 및 게이트웨이 - 정의

에이전트 프레임워크는 LLM 기반 에이전트 시스템을 구축하기 위한 소프트웨어 프레임워크이며, MCP 게이트웨이는 여러 MCP 서버를 단일 엔드포인트 뒤로 통합하여 인증·권한·감사를 중앙화하는 프록시 계층입니다.

### 프레임워크 vs 게이트웨이

| 구분 | 역할 | 예시 |
|------|------|------|
| 에이전트 프레임워크 | LLM·툴 오케스트레이션, 상태 관리, HITL | LangGraph, Claude Agent SDK, OpenAI Agents SDK |
| MCP 게이트웨이 | 다수 MCP 서버 통합, 인증/권한/감사 중앙화 | MCPX, Bifrost, MetaMCP, IBM ContextForge |
| SDK | MCP 서버 개발 라이브러리 | FastMCP, 공식 MCP Python/TypeScript SDK |

모든 주요 프레임워크가 2025-2026에 MCP를 툴 통합 표준으로 수렴하여 MCP 툴은 프레임워크 간 이식 가능합니다.

---

# 에이전트 프레임워크 및 게이트웨이 - 에이전트 프레임워크 비교

| 프레임워크 | 아키텍처 | 내구성/상태 | HITL | 사내 배포 적합성 | 비고 |
|------------|----------|-------------|------|-------------------|------|
| LangGraph | 그래프(명시적 state) | durable checkpointing, resume, time-travel | 일급 interrupt | 규제/승인 많은 장기 워크플로우 1순위 | 모델 무관, Klarna/Uber/LinkedIn 프로덕션 |
| Claude Agent SDK | Claude Code 엔진 | 내장 상태 persistence 없음 | 권한 프롬프트/hooks | repo/filesystem에서 일하는 Claude에 최적 | MCP 통합 최심, TS/Python 패키지 |
| OpenAI Agents SDK | handoff 체인 | 상태 persistence 없음 | harness 승인/resume | OpenAI 스택 팀 | 2026-04 sandbox 실행 추가 |
| Google ADK | A2A 프로토콜 | — | — | GCP/Vertex 팀 | 1.0(Java/Go) |
| Microsoft Agent Framework | SK+AutoGen 통합 | — | — | Azure/.NET 팀 | 1.0 GA 2026-04-03 |
| CrewAI | role-based crew | 상대적 약함 | — | 빠른 프로토타입 | MCP 네이티브(crewai-tools[mcp]) |
| Temporal | durable execution 엔진 | 최강 내구·재시도·재생 | 워크플로우 신호 | 장기·fault-tolerant 자동화 | 에이전트 프레임워크와 병용 |

### 권고

- 결정론적 장기 승인 흐름: LangGraph 또는 Temporal
- 코드/파일 조작형: Claude Agent SDK
- 단순 분류/추출/2-툴 조회: 프레임워크 없이 단일 API 호출 (하네스는 오버헤드)

---

# 에이전트 프레임워크 및 게이트웨이 - MCP 게이트웨이

### MCP Gateway 도입 시점

1단계(MCP 서버 몇 개)에서는 불필요. 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입을 검토합니다.

### 오픈소스 후보 (벤더 블로그 기준, 자체 PoC 필수)

| 게이트웨이 | 특징 | 비고 |
|------------|------|------|
| MCPX (Lunar) | Tool Groups, 툴 커스터마이징, 로컬/원격 MCP 인증 | 팀별 다른 툴 부분집합 |
| Bifrost (Maxim AI, Go) | MCP 클라이언트이자 서버, STDIO/HTTP/SSE 진재, 단일 /mcp 노출 | ⚠️ 자사 콘텐츠에서 자사 1위 |
| MetaMCP | 단일 엔드포인트 라우팅 + BM25 툴 필터링, 활동 로깅, 격리 보안, 웹 UI | BM25 툴 필터링이 툴 폭발에 유효 |
| IBM ContextForge | K8s 환경 세션 인식 라우팅 | 목록: e2b-dev/awesome-mcp-gateways |
| MCPJungle / Obot / Open Edison / Microsoft MCP Gateway | 데이터 유출 방지, 실행 통제 | 목록: e2b-dev/awesome-mcp-gateways |

### 평가 기준

- 런타임·언어 (Go vs Python 요청당 오버헤드 차이)
- 프로토콜 범위 (단순 진재만 하는지, REST/gRPC를 MCP 툴로 변환하는지)
- 레이트리밋·쿼터를 툴별/테넌트별/에이전트역할별로 걸 수 있는지
- 관측성 깊이 (툴 호출 활동이 쿼리 가능하고 SIEM으로 내보낼 수 있는지)

---

# 에이전트 프레임워크 및 게이트웨이 - SDK 및 FastMCP

### 공식 MCP SDK

공식 SDK는 전 주요 언어에 존재합니다 (Python, TypeScript 등). 공식 SDK 내장 mcp.server.fastmcp.FastMCP (FastMCP 1.0 계열, lifespan 파라미터 사용, dependencies 파라미터 없음). 공식 SDK는 Python >=3.10 필수 (3.7~3.9 설치 실패).

### FastMCP

FastMCP 1.0은 2024년 공식 MCP Python SDK에 통합되었습니다. 독립 프로젝트 FastMCP(현재 PrefectHQ 유지)는 자체 주장으로 하루 100만+ 다운로드, 전 언어 MCP 서버의 약 70%를 구동한다고 하나 1차 검증 불가 (벤더 주장).

중요 구분: 공식 SDK 내장 FastMCP(lifespan 사용, dependencies 없음) vs 별도 프로젝트 FastMCP 2.0(jlowin/PrefectHQ)은 다릅니다.

### TypeScript 진영

- 공식 modelcontextprotocol/typescript-sdk (스펙 동기)
- punkpeye/fastmcp (고수준 프레임워크)
- @prefecthq/fastmcp-ts (FastMCP TS 공식 카운터파트)
- FastAPI-MCP (기존 FastAPI 앱을 브리지)

### MCP 사양 버전

- 2025-11-25 (최신 stable): OpenID Connect Discovery, icons, incremental scope consent
- 2026-07-28 RC: stateless core, MCP Apps, Roots/Sampling/Logging deprecated 예정
- Transport: stdio(로컬) + Streamable HTTP(원격)만 사용. SSE는 deprecated

---

# 에이전트 프레임워크 및 게이트웨이 - 선택 가이드

### 프레임워크 선택 결정 트리

1. 단순 분류/추출/2-툴 조회 → 프레임워크 없이 단일 API 호출
2. 결정론적 순차 태스크 → Prompt chaining (직접 구현)
3. 입력 카테고리가 뚜렷 → Routing 패턴
4. 예측 불가한 멀티파일 코딩/리서치 → Orchestrator-workers (Claude Agent SDK)
5. 장기 승인 워크플로우 → LangGraph (durable checkpointing, HITL interrupt)
6. 최강 내구·재시도 필요 → Temporal (에이전트 프레임워크와 병용)
7. 빠른 프로토타입 → CrewAI (프로덕션은 LangGraph 재구현 권장)

### MCP Gateway 도입 결정

- MCP 서버 5개 미만, 단일 팀 → 불필요. managed-mcp.json 거버넌스로 충분
- MCP 서버 5개 초과 또는 다중 팀 → 도입 검토
- 되돌리기 어려운 결정이므로 거버넌스로 먼저 버티고 필요가 실증되면 도입

### SDK 선택

- Python 신규 서버 → 공식 MCP Python SDK (내장 FastMCP)
- TypeScript 신규 서버 → 공식 TypeScript SDK 또는 punkpeye/fastmcp
- 기존 FastAPI 앱 → FastAPI-MCP 브리지
- 주의: 공식 SDK 내장 FastMCP와 별도 FastMCP 2.0은 다름

---

# 에이전트 프레임워크 및 게이트웨이 - 관련 자료

### 관련 문서

- [오픈소스 MCP 서버](./01-open-source-mcp-servers.md)
- [라이브러리 및 SDK](./02-libraries-and-sdks.md)
- [MCP (Model Context Protocol)](../01_concepts/04-mcp.md)
- [툴 생성 에이전트](../01_concepts/07-tool-generation-agent.md)
- [툴 생성 에이전트 설정법](../02_setup/04-tool-generation-agent-setup.md)
- [배포·채택·거버넌스](../03_operations/06-deployment-adoption-governance.md)

### 외부 자료

- [awesome-mcp-gateways (e2b-dev)](https://github.com/e2b-dev/awesome-mcp-gateways)
- [Anthropic - Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [FastMCP (PrefectHQ)](https://github.com/PrefectHQ/fastmcp)

---

# 에이전트 프레임워크 및 게이트웨이 - 출처

- [Anthropic - Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [FastMCP (PrefectHQ)](https://github.com/PrefectHQ/fastmcp)
- [awesome-mcp-gateways (e2b-dev)](https://github.com/e2b-dev/awesome-mcp-gateways)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
- [Temporal](https://temporal.io)
- [MCP 사양](https://modelcontextprotocol.io/specification)

---

