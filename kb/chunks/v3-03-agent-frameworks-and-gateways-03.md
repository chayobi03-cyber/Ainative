---
chunk_id: "v3-03-agent-frameworks-and-gateways-03"
title: "에이전트 프레임워크 및 게이트웨이 — 선택 가이드"
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
retrieval_questions: ["프레임워크 선택 결정 트리에 대해 알려줘", "MCP Gateway 도입 결정에 대해 알려줘", "SDK 선택에 대해 알려줘", "에이전트 프레임워크 및 게이트웨이에는 무엇이 있는가?"]
related_chunks: ["v3-03-agent-frameworks-and-gateways-01", "v3-03-agent-frameworks-and-gateways-02"]
supersedes: ["chunk.133", "chunk.134"]
---

# 에이전트 프레임워크 및 게이트웨이 (3/3)

> **범위**: 선택 가이드, 관련 자료 · **출처 문서**: `05_mcp_catalog/03-agent-frameworks-and-gateways.md`

## 선택 가이드

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

## 관련 자료

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
