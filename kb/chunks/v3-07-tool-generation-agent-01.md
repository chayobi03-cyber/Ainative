---
chunk_id: "v3-07-tool-generation-agent-01"
title: "툴 생성 에이전트 — 정의"
category: "concept"
section_path: "01_concepts > 툴 생성 에이전트"
audience: ["개발자", "신규입사자"]
tags: ["mcp", "roadmap", "skills", "tool-generation-agent", "workflow"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/07-tool-generation-agent.md"]
source_urls: ["https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://www.anthropic.com/engineering/advanced-tool-use", "https://www.anthropic.com/engineering/building-effective-agents", "https://www.anthropic.com/engineering/code-execution-with-mcp", "https://www.anthropic.com/engineering/multi-agent-research-system", "https://www.anthropic.com/engineering/writing-tools-for-agents"]
retrieval_questions: ["툴 생성 에이전트란 무엇인가?", "툴 생성 에이전트의 핵심 개념은?", "툴 생성 에이전트의 3단계 로드맵은 무엇인가?", "Skills vs MCP vs Subagent vs Slash Command 선택 기준을 알려줘"]
related_chunks: ["v3-07-tool-generation-agent-02", "v3-07-tool-generation-agent-03"]
supersedes: ["chunk.095"]
---

# 툴 생성 에이전트 (1/3)

> **범위**: 정의 · **출처 문서**: `01_concepts/07-tool-generation-agent.md`

## 정의

툴 생성 에이전트는 사내 개발팀이 필요로 하는 MCP 서버, Skills, Hooks, 워크플로우 자동화를 자동으로 생성·검증·배포하는 AI 에이전트입니다. 단순한 "코드 생성기"가 아니라, 검증 하네스가 내장된 생성기로 설계되어야 합니다.

Anthropic 공식 가이드(2025-09-11 "Writing effective tools for agents — with agents")는 툴을 "결정론적 시스템과 비결정론적 에이전트 간의 계약"으로 규정하며, 툴 품질은 프롬프트 엔지니어링과 eval 반복으로만 확보된다고 결론짓습니다. 따라서 생성 에이전트는 MCP 서버 코드와 함께 mcp-eval 테스트 케이스, MCP Inspector 계약 테스트를 동시에 산출해야 "배포 후 회수 불가" 제약을 견딜 수 있습니다.

### 3단계 로드맵

| 단계 | 내용 | 산출물 |
|------|------|--------|
| 1단계 | MCP 서버 생성 에이전트 (최우선) | FastMCP 서버 코드, .mcp.json/Gemini settings, mcp-eval 케이스, Inspector 스크립트, README/보안 체크리스트 |
| 2단계 | Skills/프롬프트팩 생성 | SKILL.md, description 품질 검사기, plugin 패키징, 마켓플레이스 배포 |
| 3단계 | 워크플로우 자동화 | LangGraph/Temporal 기반 결정론적 워크플로우, HITL 승인 게이트 |

### Skills vs MCP vs Subagent vs Slash Command 선택 기준

| 도구 | 역할 | 적합한 용도 |
|------|------|------------|
| MCP | 배관 (외부 시스템/DB/사내 API 연결) | live 서버, 실제 tools/resources/prompts. 세션 시작 시 툴 정의가 컨텍스트 소비 |
| Skill | 지식/절차 (체크리스트, 하우스 스타일, 반복 워크플로우) | 대형 도메인 지식. progressive disclosure로 70-90% 토큰 절감 |
| Slash command | 사용자가 통제하는 명시적 트리거 (/name) | 서브에이전트/스킬을 파이프라인으로 호출 |
| Subagent | 격리된 컨텍스트 창의 병렬 워커 | 긴 코드리뷰, 깊은 리서치, 컨텍스트 오염 방지 |

흔한 실수: 커밋 메시지 포맷을 Skill로 (→ CLAUDE.md), 배포 체크리스트를 Skill로 (→ slash command), GitHub 접근을 Skill에 기대 (→ MCP).
