---
chunk_id: chunk.130
source_file: 05_mcp_catalog/03-agent-frameworks-and-gateways.md
title: "에이전트 프레임워크 및 게이트웨이"
section: "에이전트 프레임워크 비교"
section_id: agent-frameworks
category: catalog
tags: [agent-framework, langgraph, claude-agent-sdk, temporal, mcp-gateway, fastmcp]
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