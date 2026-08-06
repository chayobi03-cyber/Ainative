---
chunk_id: chunk.018
source_file: 01_concepts/03-hooks.md
title: "Hooks (훅)"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [hooks, automation, settings-json, pretooluse, posttooluse, guardrails]
---

# Hooks (훅) - 예외 사례

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
