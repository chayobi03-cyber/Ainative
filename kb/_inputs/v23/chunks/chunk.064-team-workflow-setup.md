---
chunk_id: chunk.064
source_file: 03_operations/02-team-workflow.md
title: "팀 워크플로우"
section: "설정법"
section_id: setup
category: operations
tags: [team, workflow, collaboration, version-control, onboarding]
---

# 팀 워크플로우 - 설정법

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
