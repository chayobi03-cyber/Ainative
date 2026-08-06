---
chunk_id: chunk.075
source_file: 04_exceptions/01-troubleshooting.md
title: "트러블슈팅 가이드"
section: "운영 가이드"
section_id: operations
category: exceptions
tags: [troubleshooting, mcp-errors, hooks-errors, connection-issues, debugging]
---

# 트러블슈팅 가이드 - 운영 가이드

### MCP 서버 문제

#### 증상: `/mcp`에 "No MCP servers configured"

| 원인 | 해결 |
|------|------|
| 다른 프로젝트에서 `claude mcp add` 실행 | 현재 프로젝트에서 재추가 또는 `--scope user` 사용 |
| 잘못된 경로에 설정 파일 | 올바른 경로: `~/.claude.json`, `<project>/.mcp.json` |
| 잘못된 파일 경로 패턴 | `~/.claude/.mcp.json` 등은 무시됨 |

#### 증상: "Failed to connect" 또는 "Connection error"

```bash
# HTTP 서버 응답 확인
curl -I https://mcp.sentry.dev/mcp

# 404/405: URL 경로 확인
# 401/403: 인증 필요 (브라우저 로그인 또는 --header 토큰)
# 응답 없음: URL 또는 네트워크 확인
```

```bash
# stdio 서버 직접 테스트
npx -y @playwright/mcp@latest
# 대기 상태: 서버 정상
# 에러: 누락된 의졍성 확인
```

#### 증상: 연결되었지만 도구가 나타나지 않음

- 필수 환경 변수(예: API 키) 누락
- `--env KEY=value` 또는 `.mcp.json`의 `env` 필드로 전달

#### 증상: `.mcp.json` 변경 사항이 반영되지 않음

- 세션 재시작 필요
- `/mcp`에서 파싱 경고 확인
- 이전 거부 시 `claude mcp reset-project-choices`

#### 증상: 시작 시 연결 타임아웃

```bash
# 타임아웃 증가
MCP_TIMEOUT=60000 claude

# PowerShell
$env:MCP_TIMEOUT = "60000"; claude
```

#### 증상: 서버 이름 중복

```bash
# 스코프 확인
claude mcp get <name>

# 스코프 지정 제거
claude mcp remove <name> --scope local
```

#### 증상: OAuth 로그인 실패

- `/mcp`에서 서버 선택 후 Authenticate 재시도
- 브라우저가 자동으로 열리지 않으면 URL 수동 복사

### Hooks 문제

#### 증상: 훅이 실행되지 않음

| 원인 | 해결 |
|------|------|
| `settings.json` 문법 오류 | `/hooks` 명령으로 경고 확인 |
| 매처 패턴 불일치 | 도구 이름과 정규식 확인 (예: `Edit\|Write`) |
| 스크립트 경로 오류 | `$CLAUDE_PROJECT_DIR` 사용 |
| 권한 부족 | 스크립트 실행 권한 확인 (`chmod +x`) |

#### 증상: PreToolUse가 도구를 차단하지 않음

- Exit 코드 2 반환 확인
- 매처가 대상 도구와 일치하는지 확인

#### 증상: 권한 충돌

- `permissions.deny`가 PreToolUse 훅보다 우선
- `PermissionDenied` 이벤트에서 `{retry: true}` 반환 시 재시도 가능

### Skills 문제

#### 증상: 스킬이 자동 로드되지 않음

- `description` 필드 확인 — 구체적이고 명확해야 함
- 파일 위치 확인: `~/.claude/skills/<name>/SKILL.md` 또는 `.claude/skills/<name>/SKILL.md`
- 세션 재시작

#### 증상: `context: fork` 스킬이 대화 기록에 접근하지 못함

- 의도된 동작 — 격리된 서브에이전트로 실행
- 필요한 컨텍스트는 스킬 본문에 포함

### Subagents 문제

#### 증상: 서브에이전트가 자동으로 호출되지 않음

- `description` 필드가 너무 모호한지 확인
- 구체적인 용도와 사용 시기 명시

#### 증상: 파일 수정 후 에이전트가 로드되지 않음

- 세션 재시작 필요
- `/agents` 명령으로 생성한 에이전트는 즉시 적용

#### 증상: `isolation: "worktree"` 변경 사항이 메인에 보이지 않음

- 격리된 워크트리에서 수정됨 — 머지 프로세스 필요

### 일반 문제

#### 증상: 컨텍스트 창 부족

- `/compact`로 컨텍스트 압축
- 미사용 MCP 서버 제거
- 무거운 작업은 서브에이전트로 위임
- CLAUDE.md를 가볍게 유지, 긴 절차는 Skills로 분산

#### 증상: MCP 도구 출력이 너무 큼

- 좁은 범위 쿼리 요청
- 요약 요청
- 서버가 많은 도구를 노출하는 경우 tool search 활용
