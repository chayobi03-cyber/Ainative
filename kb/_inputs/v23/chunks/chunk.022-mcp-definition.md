---
chunk_id: chunk.022
source_file: 01_concepts/04-mcp.md
title: "MCP (Model Context Protocol)"
section: "정의"
section_id: definition
category: concept
tags: [mcp, model-context-protocol, external-tools, mcp-servers, transport]
---

# MCP (Model Context Protocol) - 정의

MCP(Model Context Protocol)는 Anthropic이 개발한 오픈 소스 표준으로, Claude Code가 외부 도구 및 데이터 소스와 연결할 수 있게 합니다. MCP 서버는 작은 프로세스로, 타입이 지정된 도구(tools)와 리소스(resources)를 노출합니다. Claude Code가 연결하면 도구 목록을 조회하고, 도구 호출을 라우팅합니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 전송 방식 | HTTP (원격), stdio (로컬), SSE (레거시) |
| 스코프 | local, project, user — 3가지 범위 |
| 도구 이름 형식 | `mcp__<서버이름>__<도구이름>` |
| 설정 파일 | `.mcp.json` (프로젝트), `~/.claude.json` (local/user) |
| 인증 방식 | OAuth 브라우저 로그인, Bearer 토큰, 환경 변수 |

### 스코프 시스템

| 스코프 | 파일 위치 | 사용 가능 범위 |
|--------|----------|----------------|
| `local` (기본값) | `~/.claude.json` (해당 프로젝트 항목 하) | 본인만, 현재 프로젝트만 |
| `project` | `.mcp.json` (프로젝트 루트) | 저장소를 클론하는 모든 사람 |
| `user` | `~/.claude.json` (최상위 `mcpServers` 키) | 본인만, 모든 프로젝트 |

### 전송 방식 비교

| 전송 방식 | 용도 | 권장 시기 |
|-----------|------|-----------|
| HTTP (streamable-http) | 원격 서버 연결 | 2026년 신규 배포 시 권장 |
| stdio | 로컬 프로세스 실행 | 파일시스템, 브라우저, DB 소켓 접근 시 |
| SSE (레거시) | 원격 서버 | 기존 서버 호환용 only |
