---
chunk_id: chunk.129
source_file: 05_mcp_catalog/03-agent-frameworks-and-gateways.md
title: "에이전트 프레임워크 및 게이트웨이"
section: "정의"
section_id: definition
category: catalog
tags: [agent-framework, langgraph, claude-agent-sdk, temporal, mcp-gateway, fastmcp]
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