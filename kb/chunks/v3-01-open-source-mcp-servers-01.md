---
chunk_id: "v3-01-open-source-mcp-servers-01"
title: "오픈소스 MCP 서버 카탈로그 — 정의"
category: "reference"
section_path: "05_mcp_catalog > 오픈소스 MCP 서버 카탈로그"
audience: ["개발자", "운영자"]
tags: ["catalog", "community", "mcp-servers", "open-source", "reference-implementations"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["05_mcp_catalog/01-open-source-mcp-servers.md"]
source_urls: ["https://deepwiki.com/modelcontextprotocol/servers/2-reference-servers-overview", "https://github.com/modelcontextprotocol/servers", "https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/", "https://mcpplaygroundonline.com/blog/awesome-mcp-servers", "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md", "https://techsy.io/en/blog/best-mcp-servers-claude-code", "https://www.totalum.app/blog/best-mcp-for-claude-code-2026"]
retrieval_questions: ["오픈소스 MCP 서버 카탈로그란 무엇인가?", "오픈소스 MCP 서버 카탈로그의 핵심 개념은?"]
related_chunks: ["v3-01-open-source-mcp-servers-02", "v3-01-open-source-mcp-servers-03"]
supersedes: ["chunk.080", "chunk.081", "chunk.082"]
---

# 오픈소스 MCP 서버 카탈로그 (1/3)

> **범위**: 정의, 공식 참조 서버 (MCP Steering Group 관리), 아카이브된 공식 서버 · **출처 문서**: `05_mcp_catalog/01-open-source-mcp-servers.md`

## 정의

본 카탈로그는 Claude Code와 호환되는 MCP 서버 목록을 카테고리별로 정리한 것입니다. 공식 참조 구현체와 커뮤니티 서버를 모두 포함합니다.

## 공식 참조 서버 (MCP Steering Group 관리)

[GitHub: modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)에서 관리하는 7개 참조 서버:

| 서버 | 언어 | 패키지명 | 주요 용도 |
|------|------|----------|-----------|
| Everything | TypeScript | `@modelcontextprotocol/server-everything` | 프로토콜 기능 종합 데모 |
| Fetch | Python | `mcp-server-fetch` | 웹 콘텐츠 가져오기 및 마크다운 변환 |
| Filesystem | TypeScript | `@modelcontextprotocol/server-filesystem` | 구성 가능한 접근 제어 파일 작업 |
| Git | Python | `mcp-server-git` | Git 저장소 읽기, 검색, 조작 |
| Memory | TypeScript | `@modelcontextprotocol/server-memory` | 지식 그래프 기반 영구 메모리 |
| Sequential Thinking | TypeScript | `@modelcontextprotocol/server-sequential-thinking` | 순차적 사고를 통한 문제 해결 |
| Time | Python | `mcp-server-time` | 시간 및 타임존 변환 |

## 아카이브된 공식 서버

[GitHub: modelcontextprotocol/servers-archived](https://github.com/modelcontextprotocol/servers-archived)에서 관리:

| 서버 | 용도 | 현재 관리자 |
|------|------|-------------|
| GitLab | GitLab API 프로젝트 관리 | 아카이브 |
| Google Drive | Google Drive 파일 접근 및 검색 | 아카이브 |
| Google Maps | 위치 서비스, 경로, 장소 상세 | 아카이브 |
| PostgreSQL | 읽기 전용 DB 접근 및 스키마 조회 | 아카이브 |
| Puppeteer | 브라우저 자동화 및 웹 스크래핑 | 아카이브 |
| Redis | Redis 키-값 저장소 상호작용 | 아카이브 |
| Sentry | Sentry.io 이슈 조회 및 분석 | 아카이브 |
| Slack | 채널 관리 및 메시징 | Zencoder |
| SQLite | DB 상호작용 및 BI 기능 | 아카이브 |
| Brave Search | 실시간 웹 검색 | 아카이브 |
