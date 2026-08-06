---
chunk_id: chunk.076
source_file: 04_exceptions/01-troubleshooting.md
title: "트러블슈팅 가이드"
section: "예외 사례"
section_id: exceptions
category: exceptions
tags: [troubleshooting, mcp-errors, hooks-errors, connection-issues, debugging]
---

# 트러블슈팅 가이드 - 예외 사례

- HTTP 서버가 404 반환 시 `MCP endpoint not found at <url>` 메시지 표시 (v2.1.191+)
- 이전 버전은 `Error POSTing to endpoint` 일반 메시지
- `FileChanged` 훅의 `matcher` 필드는 파일명을 지정하여 감시 대상 필터링
- `WorktreeCreate`/`WorktreeRemove`는 `--worktree` 또는 `isolation: "worktree"` 사용 시 발생
