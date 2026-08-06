---
chunk_id: rag-mcp-sdk-001
title: MCP 개발 SDK와 FastMCP
category: development
section_path: "MCP > SDK"
audience: ['개발자']
use_cases: ['MCP 서버 구현 언어/SDK 선택', 'FastMCP 도입 결정']
tags: ['MCP', 'SDK', 'FastMCP', 'Python', 'TypeScript', 'PrefectHQ']
priority: medium
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: mixed
retrieval_questions: ['MCP Python SDK와 FastMCP의 차이는?', 'FastMCP는 공식 SDK인가?', 'TypeScript MCP SDK는 무엇이 있는가?']
related_chunks: ['rag-mcp-spec-001', 'rag-mcp-dev-rules-001']
---
# MCP 개발 SDK와 FastMCP

## 한 줄 요약
공식 MCP SDK는 Python, TypeScript 등 주요 언어에 존재한다. FastMCP 1.0은 2024년 공식 MCP Python SDK에 통합되었으며, 별도 프로젝트인 FastMCP 2.0(PrefectHQ)은 다른 것이다.

## 핵심 내용

### Python
- 공식 SDK 내장 `mcp.server.fastmcp.FastMCP` (FastMCP 1.0 계열): `lifespan` 파라미터 사용, `dependencies` 파라미터 없음.
- 별도 프로젝트 FastMCP 2.0 (jlowin/PrefectHQ): 자체 주장으로 하루 100만+ 다운로드, 전 언어 MCP 서버의 약 70% 구동 (1차 검증 불가 — 벤더 주장).
- 공식 SDK는 **Python >=3.10 필수** (3.7~3.9 설치 실패).
- 2025-11-11 감사 기준 공식 SDK 버전 1.21.0, 프로토콜 2025-06-18 지원.

### TypeScript
- 공식: `modelcontextprotocol/typescript-sdk` (스펙 동기).
- 고수준 프레임워크: `punkpeye/fastmcp`.
- FastMCP TS 공식 카운터파트: `@prefecthq/fastmcp-ts`.
- FastAPI-MCP (기존 FastAPI 앱을 브리지)도 옵션.

## 주의사항
- 공식 SDK의 FastMCP와 별도 프로젝트 FastMCP 2.0은 **다른 것**이다. 혼동 주의.
- FastMCP "70% 점유율·하루 100만 다운로드"는 벤더 자체 주장이며 1차 검증되지 않았다.
