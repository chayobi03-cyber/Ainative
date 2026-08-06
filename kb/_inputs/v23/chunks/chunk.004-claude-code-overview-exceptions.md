---
chunk_id: chunk.004
source_file: 01_concepts/01-claude-code-overview.md
title: "Claude Code 개요"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [claude-code, overview, architecture, agent]
---

# Claude Code 개요 - 예외 사례

### Claude Code가 아닌 것

- 챗봇이 아님 — 도구를 실행하는 에이전트
- 자동완성이 아님 — 전체 코드베이스에 접근하여 작업 수행
- IDE 플러그인이 아님 — 터미널에서 독립 실행

### Plan Mode (계획 모드)

복잡한 작업에서 실행 전 계획을 수립하는 모드:

| 작업 유형 | Plan Mode 권장 |
|-----------|---------------|
| 단순 버그 수정 (1-2 파일) | 선택적 |
| 3+ 파일에 걸친 기능 | 권장 |
| 리팩토링/아키텍처 변경 | 권장 |
| DB 마이그레이션 | 항상 권장 |
| 보안 관련 변경 | 항상 권장 |

진입 방법: `claude --plan`, `/plan` 슬래시 명령, 또는 `Shift + Tab`
