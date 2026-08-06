---
chunk_id: chunk.132
source_file: 05_mcp_catalog/03-agent-frameworks-and-gateways.md
title: "에이전트 프레임워크 및 게이트웨이"
section: "SDK 및 FastMCP"
section_id: sdks
category: catalog
tags: [agent-framework, langgraph, claude-agent-sdk, temporal, mcp-gateway, fastmcp]
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