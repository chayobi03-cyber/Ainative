---
chunk_id: chunk.061
source_file: 03_operations/01-security-governance.md
title: "보안 및 거버넌스"
section: "예외 사례"
section_id: exceptions
category: operations
tags: [security, governance, permissions, secrets, deny-list]
---

# 보안 및 거버넌스 - 예외 사례

- `permissions.deny`가 PreToolUse 훅보다 우선 적용
- 환경 변수가 Claude Code 프로세스에 전달되었는지 확인 (셸뿐 아니라 프로세스 자체)
- 프로젝트 스코프 서버를 거부한 후 재승인하려면 `claude mcp reset-project-choices`
