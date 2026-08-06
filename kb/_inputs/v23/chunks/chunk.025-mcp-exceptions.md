---
chunk_id: chunk.025
source_file: 01_concepts/04-mcp.md
title: "MCP (Model Context Protocol)"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [mcp, model-context-protocol, external-tools, mcp-servers, transport]
---

# MCP (Model Context Protocol) - 예외 사례

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
