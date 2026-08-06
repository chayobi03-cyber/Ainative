---
chunk_id: chunk.083
source_file: 05_mcp_catalog/01-open-source-mcp-servers.md
title: "오픈소스 MCP 서버 카탈로그"
section: "Claude Code 권장 MCP 서버 (2026년)"
section_id: recommended-servers
category: mcp-catalog
tags: [mcp-servers, open-source, catalog, reference-implementations, community]
---

# 오픈소스 MCP 서버 카탈로그 - Claude Code 권장 MCP 서버 (2026년)

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
