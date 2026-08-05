---
id: catalog.mcp-servers
title: 오픈소스 MCP 서버 카탈로그
category: mcp-catalog
tags: [mcp-servers, open-source, catalog, reference-implementations, community]
source_urls:
  - https://github.com/modelcontextprotocol/servers
  - https://mcpplaygroundonline.com/blog/awesome-mcp-servers
  - https://techsy.io/en/blog/best-mcp-servers-claude-code
  - https://www.totalum.app/blog/best-mcp-for-claude-code-2026
  - https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/
last_reviewed: 2026-08-05
chunking_policy: table-based
---

# 오픈소스 MCP 서버 카탈로그

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

## Claude Code 권장 MCP 서버 (2026년)

### 핵심 스택 (3개 우선 설치)

| 순위 | 서버 | 전송 방식 | 권장 스코프 | 패키지 / URL |
|------|------|-----------|-------------|--------------|
| 1 | Context7 | stdio 또는 remote | user | `@upstash/context7-mcp` 또는 `https://mcp.context7.com/mcp` |
| 2 | GitHub | remote HTTP | user | `https://api.githubcopilot.com/mcp/` |
| 3 | Playwright | stdio | project | `@playwright/mcp@latest` |

### 전체 권장 서버

| 서버 | 전송 | 패키지 / URL | 주요 도구 | 토큰 필요 |
|------|------|--------------|-----------|-----------|
| Context7 | stdio/remote | `@upstash/context7-mcp` / `https://mcp.context7.com/mcp` | 라이브 라이브러리 문서 주입 | 없음 |
| GitHub | HTTP | `@modelcontextprotocol/server-github` / `https://api.githubcopilot.com/mcp/` | 이슈, PR, 저장소 관리 | GITHUB_TOKEN |
| Playwright | stdio | `@playwright/mcp@latest` | 브라우저 자동화, 스크린샷, 테스트 | 없음 |
| Filesystem | stdio | `@modelcontextprotocol/server-filesystem` | 프로젝트 외부 파일 읽기/쓰기 | 없음 |
| PostgreSQL | stdio | `mcp-server-postgres` | SQL 쿼리, DB 스키마 | DATABASE_URL |
| Supabase | HTTP | `https://mcp.supabase.com/mcp` | DB, Auth, Storage, Realtime | OAuth |
| Sentry | HTTP | `https://mcp.sentry.dev/mcp` | 에러 추적, 릴리스, 성능 | OAuth |
| Slack | HTTP | `@anthropic/mcp-server-slack` / `https://mcp.slack.com/mcp` | 채널, 메시지, 검색 | SLACK_TOKEN / OAuth |
| Brave Search | stdio | `@anthropic/mcp-server-brave-search` | 실시간 웹 검색 | BRAVE_API_KEY |
| Notion | HTTP | `https://mcp.notion.com/mcp` | 페이지, DB, 워크스페이스 | OAuth |
| Stripe | HTTP | `https://mcp.stripe.com` | 결제, 구독, 인보이스 | OAuth |
| Figma | HTTP | `https://mcp.figma.com/mcp` | 디자인 파일, 컴포넌트, 코멘트 | OAuth |
| Linear | HTTP | `https://mcp.linear.app/mcp` | 이슈, 프로젝트, 사이클 | OAuth |
| Atlassian | HTTP | `https://mcp.atlassian.com/v1/mcp` | Jira 이슈, Confluence 페이지 | OAuth |
| HubSpot | HTTP | `https://mcp.hubspot.com` | CRM 연락처, 거래, 파이프라인 | OAuth |
| Neon | HTTP | `https://mcp.neon.tech/mcp` | 서버리스 Postgres, 브랜칭, 마이그레이션 | OAuth |
| Vercel | HTTP | `https://mcp.vercel.com` | 배포, 로그, 환경 | OAuth |
| Cloudflare | HTTP | `https://mcp.cloudflare.com/mcp` | Workers, KV, R2, DNS | OAuth |
| Exa | HTTP | `https://mcp.exa.ai/mcp` | AI 기반 시맨틱 웹 검색 | API 키 |
| Ahrefs | HTTP | `https://api.ahrefs.com/mcp/mcp` | 백링크, 키워드, SEO | API 키 |
| Semrush | HTTP | `https://mcp.semrush.com/v1/mcp` | SEO 데이터, 트래픽, 경쟁사 | API 키 |
| PayPal | HTTP | `https://mcp.paypal.com/http` | 인보이스, 결제, 거래 | OAuth |
| Asana | HTTP | `https://mcp.asana.com/mcp` | 프로젝트, 작업, 타임라인 | OAuth |
| Box | HTTP | `https://mcp.box.com/mcp` | 엔터프라이즈 파일 스토리지 | OAuth |
| Hex | HTTP | `https://mcp.hex.tech/mcp` | 데이터 노트북, 분석, 차트 | OAuth |
| Salesforce | HTTP | `https://mcp.salesforce.com/mcp` | CRM, 리드, 기회, 연락처 | OAuth |
| Amplitude | HTTP | `https://mcp.amplitude.com/mcp` | 제품 분석, 사용자 여정, A/B 테스트 | OAuth |
| Monday.com | HTTP | `https://mcp.monday.com/mcp` | 보드, 아이템, 프로젝트 | OAuth |
| Clay | HTTP | `https://mcp.clay.com/mcp` | 데이터 보강, 리드 목록, CRM 동기화 | OAuth |

## MCP 서버 디렉토리 및 검색

| 디렉토리 | URL | 특징 |
|-----------|-----|------|
| MCP Registry | [GitHub: modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 공식 참조 구현체 |
| Awesome MCP Servers | [mcpservers.org](https://mcpservers.org/) | 커뮤니티 서버 컬렉션 |
| MCP Server Directory | [codehelper.me](https://codehelper.me/tools/mcp-server-directory/) | 검색 가능 디렉토리 (2206+ 서버) |
| MCP Server Finder | [mcpserverfinder.com](https://www.mcpserverfinder.com/servers) | 포괄적 카탈로그 |
| MCP Market | [mcpmarket.com](https://mcpmarket.com/) | 일일 갱신 신규 서버 목록 |
| Model Context Protocol Directory | [model-context-protocol.com](https://model-context-protocol.com/) | MCP 서버/클라이언트 디렉토리 |

## 빠른 설치 명령

### 3개 필수 서버 설치

```bash
# Context7 - 라이브 문서
claude mcp add context7 -- npx -y @upstash/context7-mcp

# GitHub - 저장소 관리
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

# Playwright - 브라우저 자동화
claude mcp add playwright -- npx @playwright/mcp@latest
```

### 데이터베이스 서버 설치

```bash
# PostgreSQL
claude mcp add postgres --command "uvx mcp-server-postgres" --env "DATABASE_URL=postgres://..."

# Supabase (원격)
claude mcp add --transport http supabase https://mcp.supabase.com/mcp
```

### 개발 도구 서버 설치

```bash
# Sentry (에러 추적)
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# Notion (문서)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Filesystem (파일 접근)
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/files

# Sequential Thinking (문제 해결)
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```

## 출처

- [modelcontextprotocol/servers - GitHub](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers List (70+) — MCP Playground](https://mcpplaygroundonline.com/blog/awesome-mcp-servers)
- [11 Best MCP Servers for Claude Code (2026) — TECHSY](https://techsy.io/en/blog/best-mcp-servers-claude-code)
- [Best MCP for Claude Code in 2026 — Totalum](https://www.totalum.app/blog/best-mcp-for-claude-code-2026)
- [MCP Cheatsheet — SFEIR Institute](https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/)
- [modelcontextprotocol/servers README - GitHub Raw](https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md)
- [Reference Servers Overview — DeepWiki](https://deepwiki.com/modelcontextprotocol/servers/2-reference-servers-overview)
