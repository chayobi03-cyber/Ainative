---
chunk_id: "v3-03-agent-frameworks-and-gateways-02"
title: "에이전트 프레임워크 및 게이트웨이 — MCP 게이트웨이"
category: "reference"
section_path: "05_mcp_catalog > 에이전트 프레임워크 및 게이트웨이"
audience: ["개발자", "운영자"]
tags: ["agent-framework", "claude-agent-sdk", "fastmcp", "langgraph", "mcp-gateway", "temporal"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["05_mcp_catalog/03-agent-frameworks-and-gateways.md"]
source_urls: ["https://github.com/PrefectHQ/fastmcp", "https://github.com/anthropics/claude-agent-sdk", "https://github.com/e2b-dev/awesome-mcp-gateways", "https://github.com/langchain-ai/langgraph", "https://modelcontextprotocol.io/specification", "https://temporal.io", "https://www.anthropic.com/engineering/building-effective-agents"]
retrieval_questions: ["MCP Gateway 도입 시점에 대해 알려줘", "오픈소스 후보 (벤더 블로그 기준, 자체 PoC 필수)에 대해 알려줘", "평가 기준에 대해 알려줘", "에이전트 프레임워크 및 게이트웨이에는 무엇이 있는가?"]
related_chunks: ["v3-03-agent-frameworks-and-gateways-01", "v3-03-agent-frameworks-and-gateways-03"]
supersedes: ["chunk.131", "chunk.132"]
---

# 에이전트 프레임워크 및 게이트웨이 (2/3)

> **범위**: MCP 게이트웨이, SDK 및 FastMCP · **출처 문서**: `05_mcp_catalog/03-agent-frameworks-and-gateways.md`

## MCP 게이트웨이

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

## SDK 및 FastMCP

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
