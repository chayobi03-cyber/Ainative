---
chunk_id: "v3-03-hooks-03"
title: "Hooks (훅) — 운영 가이드"
category: "concept"
section_path: "01_concepts > Hooks (훅)"
audience: ["개발자", "신규입사자"]
tags: ["automation", "guardrails", "hooks", "posttooluse", "pretooluse", "settings-json"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/03-hooks.md"]
source_urls: ["https://code.claude.com/docs/en/hooks", "https://code.claude.com/docs/en/hooks-guide", "https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/", "https://www.heyuan110.com/posts/ai/2026-02-28-claude-code-hooks-guide/", "https://www.morphllm.com/claude-code-hooks"]
retrieval_questions: ["Hooks (훅) 운영 시 주의점은?", "Hooks (훅)의 모범 사례는?", "Hooks (훅)에서 자주 발생하는 문제는?", "Hooks (훅) 트러블슈팅 방법은?", "Hooks (훅)의 보안 고려사항은?"]
related_chunks: ["v3-03-hooks-01", "v3-03-hooks-02"]
supersedes: ["chunk.017", "chunk.018", "chunk.019"]
---

# Hooks (훅) (3/3)

> **범위**: 운영 가이드, 예외 사례, 보안 고여사항 · **출처 문서**: `01_concepts/03-hooks.md`

## 운영 가이드

### Hook 핸들러 필드

| 필드 | 설명 |
|------|------|
| `type` | `command`, `http`, `mcp_tool`, `prompt`, `agent` 중 하나 |
| `command` | `type: "command"`일 때 실행할 셸 명령 |
| `timeout` | 타임아웃 (초 단위, 기본값: 30) |
| `async` | `true` 시 비동기 실행 (결과 대기 안 함) |

### 매처 패턴

매처는 도구 이름을 정규식으로 매칭:

| 매처 패턴 | 매칭 도구 |
|-----------|-----------|
| `Bash` | Bash 도구만 |
| `Edit\|Write` | Edit 또는 Write 도구 |
| `mcp__.*` | 모든 MCP 도구 |
| (빈 문자열) | 모든 도구 |

### Exit 코드 동작

| Exit 코드 | 의미 |
|-----------|------|
| `0` | 정상 완료, 계속 진행 |
| `2` | PreToolUse에서 도구 실행 차단 |
| 기타 0이 아닌 값 | 에러, Claude에게 피드백 전달 |

### 무인 운영을 위한 필수 훅

- **사전 커밋 보호**: 민감 파일(`.env`, `.key`, `.pem`) 커밋 차단
- **위험 명령 차단**: `rm -rf`, `DROP TABLE` 등 실행 전 차단
- **자동 포맷팅**: 편집 후 Prettier/ESLint 자동 실행
- **세션 로깅**: 작업 완료 시 로그 파일에 기록

## 예외 사례

### 훅이 실행되지 않는 경우

- `settings.json` 문법 오류 시 해당 항목 스킵 (경고는 `/hooks` 명령으로 확인)
- 매처 패턴이 도구 이름과 불일치 시 실행 안 됨
- 비동기 훅(`async: true`)은 결과를 기다리지 않으므로 실패해도 세션 계속

### .mcp.json 변경 사항이 반영되지 않는 경우

- Claude Code는 세션 시작 시 `.mcp.json`을 읽으므로, 파일 편집 후 세션 재시작 필요
- 이전에 서버를 거부한 경우: `claude mcp reset-project-choices` 실행

### 권한 충돌

- `permissions.deny` 배열과 PreToolUse 훅이 모두 설정된 경우, deny가 우선 적용
- PermissionDenied 이벤트에서 `{retry: true}` 반환 시 모델이 재시도 가능

### 2026년 "MCP Hooks" 오해

"MCP hooks"라는 용어가 검색되지만, MCP 서버와 Claude Code Hooks는 별개의 계층입니다:
- MCP 서버: 외부 도구와 데이터를 노출
- Claude Code Hooks: 이벤트 주변에서 결정론적 명령 실행

## 보안 고여사항

- 훅 스크립트는 `$CLAUDE_PROJECT_DIR` 환경 변수를 사용하여 경로 해석
- 훅 명령에 사용자 입력이 포함될 수 있으므로 인젝션 방지 필요
- `permissions.deny` 배열로 파일 접근 차단:
  ```json
  {
    "permissions": {
      "deny": [
        "Read(./.env)",
        "Read(./.env.*)",
        "Read(./secrets/**)",
        "Bash(cat ./.env *)"
      ]
    }
  }
  ```
- 무인 운영 시 사전 커밋 훅 필수 — 민감 파일 유출 방지
