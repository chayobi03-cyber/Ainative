---
chunk_id: chunk.017
source_file: 01_concepts/03-hooks.md
title: "Hooks (훅)"
section: "운영 가이드"
section_id: operations
category: concept
tags: [hooks, automation, settings-json, pretooluse, posttooluse, guardrails]
---

# Hooks (훅) - 운영 가이드

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
