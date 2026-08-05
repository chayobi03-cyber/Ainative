---
chunk_id: "v3-component-selection"
title: "Skills vs MCP vs Subagent vs Slash Command 선택 기준"
category: "architecture"
section_path: "설계 원칙 > 컴포넌트 선택"
audience: ["아키텍트", "개발자", "기술 기획자"]
use_cases: ["컴포넌트 선택 결정", "아키텍처 설계", "흔한 실수 방지"]
tags: ["MCP", "Skills", "Subagent", "slash-command", "plugin", "selection-criteria"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["MCP와 Skills 중 무엇을 먼저 만들어야 하는가?", "커밋 메시지 포맷은 Skill로 만들어야 하는가?", "Subagent는 언제 쓰는가?", "plugin과 skill의 차이는?"]
related_chunks: ["v3-agent-skills", "v3-workflow-patterns"]
supersedes: ["rag-component-selection-001"]
---

# Skills vs MCP vs Subagent vs Slash Command 선택 기준

## 한 줄 요약
MCP는 배관(외부 시스템 연결), Skill은 지식/절차, Slash command는 명시적 트리거, Subagent는 격리된 병렬 워커다. 각자 목적이 다르므로 흔한 실수를 피해 올바른 컴포넌트를 선택해야 한다.

## 선택 기준

### MCP = 배관
- 외부 시스템/DB/사내 API 연결, live 서버, 실제 tools/resources/prompts
- 세션 시작 시 툴 정의가 시스템 프롬프트에 로드되어 컨텍스트 소비

### Skill = 지식/절차
- 체크리스트, 하우스 스타일, 반복 워크플로우, 번들 스크립트
- auto-detection 가치가 큰 대형 도메인 지식에 적합
- progressive disclosure로 70-90% 토큰 절감

### Slash command = 명시적 트리거
- 사용자가 통제하는 명시적 트리거 (`/name`)
- 서브에이전트/스킬을 파이프라인으로 호출 가능

### Subagent = 격리된 병렬 워커
- 긴 코드리뷰, 깊은 리서치, 컨텍스트 오염 방지
- 각자 컨텍스트·토큰 독립 소비 (과다 병렬 시 사용량 급증)

## 흔한 실수
- 커밋 메시지 포맷을 Skill로 (→ CLAUDE.md가 맞음)
- 배포 체크리스트를 Skill로 (→ slash command가 맞음)
- GitHub 접근을 Skill에 기대 (→ MCP가 맞음)
- "plugin vs skill"은 갈림길이 아니다 — skill은 역량 단위, plugin은 배포 단위

## Gemini CLI 매핑
| Claude Code | Gemini CLI |
|---|---|
| CLAUDE.md (컨텍스트) | GEMINI.md |
| plugin (패키징) | extension |
| slash command | custom commands |
| skills/ (SKILL.md) | skills/ (동일 표준) |
| subagent | sub-agents (preview) |
