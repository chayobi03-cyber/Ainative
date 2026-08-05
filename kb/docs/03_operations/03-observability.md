---
id: operations.observability
title: 관측성 및 유지보수
category: operations
tags: [observability, logging, monitoring, maintenance, debugging]
source_urls:
  - https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/
  - https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html
last_reviewed: 2026-08-05
chunking_policy: whole-document
---

# 관측성 및 유지보수

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

## 출처

- [My Claude Code Setup After 4 Months of Daily Use (2026)](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)
- [Claude Code Hooks Complete Guide — Hidekazu Konishi](https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html)

---

## 신규 관련 문서 (2026-08-05 보강)

- [품질 평가 및 CI](./04-quality-evaluation-ci.md) — Langfuse 셀프호스팅, OpenTelemetry GenAI semantic conventions, 골든셋 회귀 게이트, eval 프레임워크 셀프호스팅 비교
- [비용·성능 최적화](./05-cost-performance-optimization.md) — ccusage(비용 가시화), claude-code-otel(팀용 셀프호스팅 관측 스택), 캐시 히트율 모니터링
- [배포·채택·거버넌스](./06-deployment-adoption-governance.md) — 감사로그, canary 롤아웃, feature flag/remote config

> **폐쇄망 관측 1순위**: Langfuse(트레이싱·비용·프롬프트 버전, MIT 오픈소스, Docker/K8s 셀프호스팅) + DeepEval/mcp-eval(CI eval) + OpenTelemetry 계측. Langfuse는 2026년 1월 ClickHouse 인수 후에도 오픈소스·셀프호스팅 유지. semantic convention 버전 pinning 필수(v1.41 기준 대부분 Development 안정성 badge).
