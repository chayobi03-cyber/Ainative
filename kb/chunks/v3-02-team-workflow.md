---
chunk_id: "v3-02-team-workflow"
title: "팀 워크플로우"
category: "operations"
section_path: "03_operations > 팀 워크플로우"
audience: ["운영자"]
tags: ["collaboration", "onboarding", "team", "version-control", "workflow"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/02-team-workflow.md"]
source_urls: ["https://medium.com/@kinjal01radadiya/how-sub-agents-work-in-claude-code-a-complete-guide-bafc66bbaf70", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/"]
retrieval_questions: ["팀 워크플로우란 무엇인가?", "팀 워크플로우의 핵심 개념은?", "팀 워크플로우는 어떻게 설정하는가?", "팀 워크플로우 초기 구성 절차는?", "팀 워크플로우 운영 시 주의점은?"]
related_chunks: ["v3-doctor-command", "v3-06-deployment-adoption-governance-01", "v3-06-deployment-adoption-governance-02"]
supersedes: ["chunk.063", "chunk.064", "chunk.065", "chunk.066"]
---

# 팀 워크플로우

> **범위**: 정의, 설정법, 운영 가이드, 예외 사례 · **출처 문서**: `03_operations/02-team-workflow.md`

## 정의

팀 워크플로우는 Claude Code 설정을 버전 관리하고, 팀원 간 일관성을 유지하며, 서브에이전트와 스킬을 공유하는 체계입니다.

## 설정법

### 1. 버전 관리 대상 파일

| 파일 | 용도 | Git 커밋 |
|------|------|----------|
| `CLAUDE.md` | 프로젝트 규칙 | 권장 |
| `.mcp.json` | 프로젝트 스코프 MCP 서버 | 권장 |
| `.claude/settings.json` | 프로젝트 훅 및 권한 | 권장 |
| `.claude/skills/` | 프로젝트 스킬 | 권장 |
| `.claude/agents/` | 프로젝트 서브에이전트 | 권장 |
| `.claude/rules/` | 경로 스코프 규칙 | 권장 |

### 2. 팀 온보딩 체크리스트

- [ ] Claude Code 설치 및 `claude doctor` 검증
- [ ] 저장소 클론 후 `claude` 실행
- [ ] 프로젝트 스코프 MCP 서버 승인
- [ ] `CLAUDE.md` 검토
- [ ] 환경 변수 설정 (API 토큰 등)
- [ ] 팀 스킬 및 에이전트 숙지

### 3. 서브에이전트 팀 패턴

```
리서치 에이전트 → 데이터 수집
    ↓
작성 에이전트 → 섹션 작성
    ↓
리뷰 에이전트 → 품질 검토
```

## 운영 가이드

- 에이전트 설정 파일을 버전 관리하여 팀 일관성 유지
- 팀 위키에 각 에이전트의 용도, 사용 시기, 프롬프트 예시, 한계 기록
- 1-2개의 전문 에이전트로 시작, 실제 성능 기반 개선
- 서브에이전트에 완전한 컨텍스트 전달 (메인 대화 기록 접근 불가)
- 구조화된 데이터 반환 (JSON이 산문보다 파싱 용이)
- 독립 작업은 병렬 실행, 결과는 메인 컨텍스트에서 취합

## 예외 사례

- local 스코프 서버는 다른 팀원에게 공유되지 않음
- 사용자 스코프 에이전트는 개인만 사용 가능
- 서브에이전트가 메인 대화 기록을 볼 수 없으므로 컨텍스트를 명시적으로 전달
