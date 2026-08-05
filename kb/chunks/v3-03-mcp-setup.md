---
chunk_id: "v3-03-mcp-setup"
title: "MCP 설정법"
category: "reference"
section_path: "02_setup > MCP 설정법"
audience: ["개발자", "운영자"]
tags: ["configuration", "mcp", "mcp-servers", "setup", "transport"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["02_setup/03-mcp-setup.md"]
source_urls: ["https://code.claude.com/docs/en/mcp-quickstart", "https://github.com/ericbuess/claude-code-docs/blob/main/docs/mcp.md", "https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/"]
retrieval_questions: ["MCP 설정법란 무엇인가?", "MCP 설정법의 핵심 개념은?", "MCP 설정법는 어떻게 설정하는가?", "MCP 설정법 초기 구성 절차는?", "MCP 설정법 운영 시 주의점은?"]
related_chunks: ["v3-04-mcp-01", "v3-04-mcp-02", "v3-04-mcp-03"]
supersedes: ["chunk.053", "chunk.054", "chunk.055", "chunk.056"]
---

# MCP 설정법

> **범위**: 정의, 설정법, 운영 가이드, 예외 사례 · **출처 문서**: `02_setup/03-mcp-setup.md`

## 정의

MCP 설정은 `claude mcp add` 명령 또는 `.mcp.json` 파일을 통해 외부 도구 서버를 Claude Code에 등록하는 과정입니다. 전송 방식, 스코프, 인증 방식을 선택하여 구성합니다.

## 설정법

### 1. HTTP 서버 추가 (원격)

```bash
# 기본 문법
claude mcp add --transport http <name> <url>

# 예: Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Bearer 토큰
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

### 2. stdio 서버 추가 (로컬)

```bash
# Playwright
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Context7
claude mcp add context7 -- npx -y @upstash/context7-mcp

# 환경 변수와 함께
claude mcp add github -e GITHUB_TOKEN=ghp_xxx -- npx -y @modelcontextprotocol/server-github

# Python 서버
claude mcp add my-server -- python3 -m my_mcp_server
```

### 3. SSE 서버 추가 (레거시)

```bash
claude mcp add my-remote -t sse -- https://mcp.example.com/sse

# 인증 헤더와 함께
claude mcp add secure-server -t sse -h "Authorization: Bearer token123" -- https://api.example.com/sse
```

### 4. 스코프 지정

```bash
# local (기본값)
claude mcp add --transport http stripe https://mcp.stripe.com

# project (.mcp.json에 저장, 팀 공유)
claude mcp add --scope project --transport http docs https://code.claude.com/docs/mcp

# user (모든 프로젝트)
claude mcp add --scope user --transport http docs https://code.claude.com/docs/mcp
```

### 5. .mcp.json 직접 작성

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
    },
    "postgres": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "postgres://..."
      },
      "timeout": 600000
    }
  }
}
```

### 6. 관리 명령

```bash
claude mcp list                    # 서버 목록 및 상태
claude mcp get <name>              # 특정 서버 정보
claude mcp remove <name>           # 서버 제거
claude mcp remove <name> --scope local  # 스코프 지정 제거
claude mcp reset-project-choices   # 프로젝트 승인 초기화
claude mcp add-json '<json>'       # JSON으로 직접 추가
claude mcp add-from-claude-desktop # Claude Desktop에서 가져오기
claude mcp serve                   # Claude Code를 MCP 서버로 실행
```

## 운영 가이드

- 가장 큰 컨텍스트 스위칭을 해결하는 서버를 먼저 추가
- 한 서버 추가 후 올바르게 사용되는지 확인 후 다음 추가
- 미사용 서버는 제거하여 컨텍스트 창 절약
- `MCP_TIMEOUT` 환경 변수로 시작 타임아웃 조정
- `.mcp.json`의 `timeout` 필드로 서버별 도구 실행 타임아웃 설정

## 예외 사례

- local 스코프는 프로젝트별이므로 다른 프로젝트에서는 미표시
- `.mcp.json` 변경 후 세션 재시작 필요
- OAuth 서버는 `/mcp`에서 Authenticate 선택하여 브라우저 로그인
- 서버 이름 중복 시 `--scope`로 구분하여 제거
