---
id: concept.mcp
title: MCP (Model Context Protocol)
category: concepts
tags: [mcp, model-context-protocol, external-tools, mcp-servers, transport]
source_urls:
  - https://code.claude.com/docs/en/mcp-quickstart
  - https://github.com/modelcontextprotocol/servers
  - https://techsy.io/en/blog/best-mcp-servers-claude-code
  - https://www.totalum.app/blog/best-mcp-for-claude-code-2026
last_reviewed: 2026-08-05
chunking_policy: section-based
---

# MCP (Model Context Protocol)

## 정의

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

## 설정법

### 1. 원격 HTTP 서버 추가

```bash
# 기본 문법
claude mcp add --transport http <name> <url>

# 실제 예: Notion 연결
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Bearer 토큰과 함께
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"

# GitHub 연결 (원격)
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

### 2. 로컬 stdio 서버 추가

```bash
# Playwright (브라우저 자동화)
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Context7 (라이브러리 문서)
claude mcp add context7 -- npx -y @upstash/context7-mcp

# GitHub (stdio)
claude mcp add github -e GITHUB_TOKEN=ghp_xxx -- npx -y @modelcontextprotocol/server-github

# PostgreSQL
claude mcp add postgres --command "uvx mcp-server-postgres" --env "DATABASE_URL=postgres://..."

# Python 서버
claude mcp add my-server -- python3 -m my_mcp_server
```

### 3. 스코프 지정

```bash
# 로컬 스코프 (기본값)
claude mcp add --transport http stripe https://mcp.stripe.com

# 프로젝트 스코프 (팀 공유)
claude mcp add --scope project --transport http docs https://code.claude.com/docs/mcp

# 사용자 스코프 (모든 프로젝트)
claude mcp add --scope user --transport http docs https://code.claude.com/docs/mcp
```

### 4. .mcp.json 직접 편집

프로젝트 루트에 `.mcp.json` 파일 생성:

```json
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### 5. 서버 관리 명령

```bash
# 서버 목록 및 상태 확인
claude mcp list

# 특정 서버 정보 조회
claude mcp get <name>

# 서버 제거
claude mcp remove <name>

# 스코프 지정 제거
claude mcp remove <name> --scope local

# 프로젝트 승인 초기화
claude mcp reset-project-choices

# JSON 설정으로 직접 추가
claude mcp add-json '<json-string>'

# Claude Desktop에서 설정 가져오기 (macOS/WSL)
claude mcp add-from-claude-desktop

# Claude Code 자체를 MCP 서버로 실행
claude mcp serve
```

### 6. 연결 상태 확인

`claude mcp list` 출력 상태:

| 상태 | 의미 |
|------|------|
| `✔ Connected` | 사용 준비 완료 |
| `! Connected · tools fetch failed` | 연결됨, 도구 목록 조회 실패 |
| `! Needs authentication` | 인증 필요 (브라우저 로그인 또는 토큰) |
| `✘ Failed to connect` | 서버 응답 없음 |
| `✘ Connection error` | 연결 시도 중 에러 발생 |
| `⏸ Pending approval` | 프로젝트 스코프 서버 미승인 |

### 7. OAuth 인증이 필요한 서버

```bash
# Sentry 연결 (OAuth)
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 세션 내에서 인증
# /mcp 명령 실행 → 서버 선택 → Authenticate
```

## 운영 가이드

### MCP 서버 선택 기준

1. **가장 큰 수동 컨텍스트 스위칭을 해결하는 서버를 먼저 추가**
2. 한 서버를 추가하고 Claude가 올바르게 사용하는지 확인한 후 다음 서버 추가
3. 각 연결된 서버는 컨텍스트 창 공간을 소모하므로 미사용 서버는 제거

### 2026년 권장 핵심 MCP 서버 스택

| 서버 | 용도 | 권장 스코프 | 설치 난이도 |
|------|------|-------------|-------------|
| Context7 | 라이브 라이브러리 문서 주입 | user | 낮음 |
| GitHub | 저장소, PR, 이슈 관리 | user | 낮음 |
| Playwright | 브라우저 자동화 및 테스트 | project | 낮음 |
| PostgreSQL/Supabase | DB 쿼리 및 스키마 조회 | project | 중간 |
| Sentry | 에러 추적 및 성능 분석 | project | 중간 |

### 환경 변수 관리

```bash
# --env 플래그로 환경 변수 전달
claude mcp add github -e GITHUB_TOKEN=ghp_xxx -- npx -y @modelcontextprotocol/server-github

# .mcp.json에서 환경 변수 참조
"env": {
  "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
}
```

### 타임아웃 설정

| 설정 방식 | 설명 |
|-----------|------|
| `MCP_TIMEOUT` 환경 변수 | 서버 시작 타임아웃 (밀리초). 예: `MCP_TIMEOUT=60000 claude` |
| `timeout` 필드 (`.mcp.json`) | 서버별 도구 실행 타임아웃 (밀리초). 예: `"timeout": 600000` |
| `MCP_TOOL_TIMEOUT` 환경 변수 | 전역 도구 실행 타임아웃. 서버별 `timeout` 필드가 우선 |

### 다양한 연결 표면

Claude Code의 모든 표면에서 MCP 서버 연결 가능:

| 표면 | 연결 방법 |
|------|-----------|
| Claude Code CLI | `claude mcp add` 명령 |
| Claude Code 데스크톱 앱 | Connectors UI |
| Claude Desktop 채팅 앱 | `claude mcp add-from-claude-desktop`으로 복사 |
| VS Code | MCP 확장 통해 연결 |
| Claude Code on the web | 저장소의 `.mcp.json` 읽기 |
| Claude.ai | claude.ai/customize/connectors에서 추가 시 자동 동기화 |

### 플러그인 기반 MCP 서버

```bash
# 플러그인을 통한 MCP 서버 관리
# 플러그인이 활성화되면 해당 MCP 서버가 자동 시작
# .mcp.json 또는 plugin.json에 정의
```

## 예외 사례

### `/mcp`에 "No MCP servers configured"가 표시되는 경우

- 다른 프로젝트에서 `claude mcp add`를 실행한 경우 (local 스코프는 프로젝트별)
- 잘못된 경로에 설정 파일을 작성한 경우
  - 올바른 경로: `~/.claude.json`, `<project>/.mcp.json`
  - 잘못된 경로: `~/.claude/.mcp.json`, `~/.claude/config/mcp.json`, `~/.claude/mcp.json`

### "Failed to connect" 또는 "Connection error"

```bash
# HTTP 서버 응답 확인
curl -I https://mcp.sentry.dev/mcp

# 응답 코드별 진단:
# 404/405: 서버는 실행 중, URL 경로 확인
# 401/403: 인증 필요 (브라우저 로그인 또는 토큰)
# 응답 없음: URL 또는 네트워크 확인
```

### stdio 서버 디버깅

```bash
# 명령을 직접 실행하여 테스트
npx -y @playwright/mcp@latest

# 명령이 대기 상태로 시작: 서버 정상, claude mcp get으로 명령 확인
# 에러 발생: 메시지에서 누락된 의존성 확인 (Node.js, 브라우저 등)
```

### 서버는 연결되지만 도구가 나타나지 않는 경우

- 필수 환경 변수(예: API 키) 누락이 가장 흔한 원인
- `--env KEY=value` 플래그 또는 `.mcp.json`의 `env` 필드로 전달
- `/mcp` 명령으로 서버 선택 후 도구 목록 확인

### `.mcp.json` 변경 사항이 반영되지 않는 경우

- 세션 시작 시에만 `.mcp.json`을 읽으므로 세션 재시작 필요
- 이전에 서버를 거부한 경우: `claude mcp reset-project-choices`
- 구문 오류 시 해당 항목 스킵, `/mcp`에서 경고 확인

### 서버 이름 중복

- 동일한 이름이 여러 스코프에 존재할 수 있음
- `claude mcp remove <name>` 시 "exists in multiple scopes" 메시지 표시
- `--scope` 플래그로 특정 스코프의 항목 삭제

## 보안 고려사항

- **시크릿 관리**: 토큰은 환경 변수로 관리, JSON에 평문 금지
- **GitHub 토큰 스코프**: 최소 권한 원칙, 필요한 경우에만 `repo` 스코프 부여
- **프로젝트 스코프 서버 승인**: 저장소 클론 시 자동 실행 방지를 위해 승인 프롬프트 표시
- **서버 신뢰 검증**: 연결 전 각 서버의 신뢰성 확인
- **관리 설정**: 엔터프라이즈 환경에서 관리자가 MCP 접근 정책 관리 가능

## 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [Hooks (훅)](./03-hooks.md)
- [MCP 설정법 (상세)](../02_setup/03-mcp-setup.md)
- [오픈소스 MCP 서버 카탈로그](../05_mcp_catalog/01-open-source-mcp-servers.md)
- [라이브러리 및 SDK](../05_mcp_catalog/02-libraries-and-sdks.md)
- [트러블슈팅](../04_exceptions/01-troubleshooting.md)

## 출처

- [Claude Code 공식 문서 - MCP 퀵스타트](https://code.claude.com/docs/en/mcp-quickstart)
- [Claude Code Docs - Connect to tools via MCP (GitHub mirror)](https://github.com/ericbuess/claude-code-docs/blob/main/docs/mcp.md)
- [modelcontextprotocol/servers - GitHub](https://github.com/modelcontextprotocol/servers)
- [11 Best MCP Servers for Claude Code (2026) — TECHSY](https://techsy.io/en/blog/best-mcp-servers-claude-code)
- [Best MCP for Claude Code in 2026 — Totalum](https://www.totalum.app/blog/best-mcp-for-claude-code-2026)
- [MCP: Model Context Protocol Cheatsheet — SFEIR Institute](https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/)
- [My Claude Code Setup After 4 Months of Daily Use (2026)](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)

---

## 신규 관련 문서 (2026-08-05 보강)

- [툴 생성 에이전트](./07-tool-generation-agent.md) — MCP 서버 생성 에이전트, Anthropic 5원칙, 3단계 로드맵
- [컨텍스트 엔지니어링](./08-context-engineering.md) — llms.txt로 사내 API 문서 에이전트 친화화
- [툴 생성 에이전트 설정법](../02_setup/04-tool-generation-agent-setup.md) — FastMCP 예제, .mcp.json, Gemini settings, MCPB 번들
- [품질 평가 및 CI](../03_operations/04-quality-evaluation-ci.md) — MCP Inspector, mcp-eval, mcp-compliance, 계약 테스트
- [에이전트 프레임워크 및 게이트웨이](../05_mcp_catalog/03-agent-frameworks-and-gateways.md) — MCP 사양 버전(2025-11-25 stable, 2026-07-28 RC), transport(stdio/Streamable HTTP), SDK/FastMCP 비교

> **최신 MCP 사양 요약**: 2025-11-25 stable(OpenID Connect, icons, incremental scope). 2026-07-28 RC(stateless core, MCP Apps, Roots/Sampling/Logging deprecated 예정). Transport는 stdio(로컬) + Streamable HTTP(원격)만 사용, SSE는 deprecated.
