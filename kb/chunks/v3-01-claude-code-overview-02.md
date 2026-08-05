---
chunk_id: "v3-01-claude-code-overview-02"
title: "Claude Code 개요 — 예외 사례"
category: "concept"
section_path: "01_concepts > Claude Code 개요"
audience: ["개발자", "신규입사자"]
tags: ["agent", "architecture", "claude-code", "overview"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/01-claude-code-overview.md"]
source_urls: ["https://code.claude.com/docs/en/mcp-quickstart", "https://news.creeta.com/en/claude-code-best-practices-2026/", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/"]
retrieval_questions: ["Claude Code 개요에서 자주 발생하는 문제는?", "Claude Code 개요 트러블슈팅 방법은?", "Claude Code 개요의 Claude Code가 아닌 것은 무엇인가?", "Claude Code 개요의 Plan Mode (계획 모드)은 무엇인가?"]
related_chunks: ["v3-01-claude-code-overview-01", "v3-claude-code-guide", "v3-cli-registration"]
supersedes: ["chunk.004", "chunk.005"]
---

# Claude Code 개요 (2/2)

> **범위**: 예외 사례, 보안 고려사항 · **출처 문서**: `01_concepts/01-claude-code-overview.md`

## 예외 사례

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

## 보안 고려사항

- MCP 서버 추가 시 비밀키는 환경 변수로 관리, JSON에 평문 금지
- 프로젝트 스코프 서버는 저장소 클론 시 자동 실행되지 않음 — 승인 프롬프트 필요
- `permissions.deny` 배열을 통해 특정 도구/파일 접근 차단 가능
- Hooks를 통한 사전 커밋 검증으로 민감 파일 유출 방지
