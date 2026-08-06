---
chunk_id: chunk.019
source_file: 01_concepts/03-hooks.md
title: "Hooks (훅)"
section: "보안 고여사항"
section_id: security
category: concept
tags: [hooks, automation, settings-json, pretooluse, posttooluse, guardrails]
---

# Hooks (훅) - 보안 고여사항

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
