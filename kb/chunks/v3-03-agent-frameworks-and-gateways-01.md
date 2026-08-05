---
chunk_id: "v3-03-agent-frameworks-and-gateways-01"
title: "에이전트 프레임워크 및 게이트웨이 — 정의"
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
retrieval_questions: ["에이전트 프레임워크 및 게이트웨이란 무엇인가?", "에이전트 프레임워크 및 게이트웨이의 핵심 개념은?"]
related_chunks: ["v3-03-agent-frameworks-and-gateways-02", "v3-03-agent-frameworks-and-gateways-03"]
supersedes: ["chunk.129", "chunk.130"]
---

# 에이전트 프레임워크 및 게이트웨이 (1/3)

> **범위**: 정의, 에이전트 프레임워크 비교 · **출처 문서**: `05_mcp_catalog/03-agent-frameworks-and-gateways.md`

## 정의

에이전트 프레임워크는 LLM 기반 에이전트 시스템을 구축하기 위한 소프트웨어 프레임워크이며, MCP 게이트웨이는 여러 MCP 서버를 단일 엔드포인트 뒤로 통합하여 인증·권한·감사를 중앙화하는 프록시 계층입니다.

### 프레임워크 vs 게이트웨이

| 구분 | 역할 | 예시 |
|------|------|------|
| 에이전트 프레임워크 | LLM·툴 오케스트레이션, 상태 관리, HITL | LangGraph, Claude Agent SDK, OpenAI Agents SDK |
| MCP 게이트웨이 | 다수 MCP 서버 통합, 인증/권한/감사 중앙화 | MCPX, Bifrost, MetaMCP, IBM ContextForge |
| SDK | MCP 서버 개발 라이브러리 | FastMCP, 공식 MCP Python/TypeScript SDK |

모든 주요 프레임워크가 2025-2026에 MCP를 툴 통합 표준으로 수렴하여 MCP 툴은 프레임워크 간 이식 가능합니다.

## 에이전트 프레임워크 비교

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
