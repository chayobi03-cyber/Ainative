---
chunk_id: chunk.133
source_file: 05_mcp_catalog/03-agent-frameworks-and-gateways.md
title: "에이전트 프레임워크 및 게이트웨이"
section: "선택 가이드"
section_id: selection-guide
category: catalog
tags: [agent-framework, langgraph, claude-agent-sdk, temporal, mcp-gateway, fastmcp]
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