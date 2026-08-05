---
chunk_id: "v3-03-observability"
title: "관측성 및 유지보수"
category: "operations"
section_path: "03_operations > 관측성 및 유지보수"
audience: ["운영자"]
tags: ["debugging", "logging", "maintenance", "monitoring", "observability"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/03-observability.md"]
source_urls: ["https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/"]
retrieval_questions: ["관측성 및 유지보수란 무엇인가?", "관측성 및 유지보수의 핵심 개념은?", "관측성 및 유지보수는 어떻게 설정하는가?", "관측성 및 유지보수 초기 구성 절차는?", "관측성 및 유지보수 운영 시 주의점은?"]
related_chunks: ["v3-01-troubleshooting", "v3-cost-visibility"]
supersedes: ["chunk.068", "chunk.069", "chunk.070", "chunk.071"]
---

# 관측성 및 유지보수

> **범위**: 정의, 설정법, 운영 가이드, 예외 사례 · **출처 문서**: `03_operations/03-observability.md`

## 정의

Claude Code 운영 환경에서 관측성은 Hooks를 통한 로깅, MCP 서버 상태 모니터링, 세션 컨텍스트 관리를 포함합니다.

## 설정법

### 1. 세션 로깅 (Stop 훅)

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date): session completed\" >> ~/claude-work.log",
            "async": true
          }
        ]
      }
    ]
  }
}
```

### 2. MCP 서버 상태 모니터링

```bash
# 서버 목록 및 상태
claude mcp list

# 세션 내에서
/mcp
```

### 3. 컨텍스트 사용량 확인

```bash
/context  # 토큰 사용량 분석
```

### 4. 도구 호출 로깅 (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date): tool used - $(jq -r '.tool_name')\" >> ~/claude-tools.log"
          }
        ]
      }
    ]
  }
}
```

## 운영 가이드

- 긴 세션에서는 `/compact`를 사용하여 컨텍스트 압축
- 작업 경계에서 컴팩션 수행
- 미사용 MCP 서버는 제거하여 컨텍스트 창 절약
- `PreCompact`/`PostCompact` 훅으로 압축 전후 상태 관리
- `InstructionsLoaded` 훅으로 CLAUDE.md/Rules 로드 시점 추적

## 예외 사례

- 컨텍스트 압축 시 중요한 상태가 숨겨질 수 있음 — 내구성 있는 규칙은 CLAUDE.md에 유지
- MCP 서버가 많은 도구를 노출하면 컨텍스트 창 소모 증가 — tool search 활용
- MCP 도구 출력이 과도한 경우 좁은 범위 쿼리 또는 요약 요청
