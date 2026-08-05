---
chunk_id: "v3-05-claude-md-memory-01"
title: "CLAUDE.md 메모리 시스템 — 정의"
category: "concept"
section_path: "01_concepts > CLAUDE.md 메모리 시스템"
audience: ["개발자", "신규입사자"]
tags: ["claude-md", "configuration", "context", "memory", "project-rules"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/05-claude-md-memory.md"]
source_urls: ["https://news.creeta.com/en/claude-code-best-practices-2026/", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/"]
retrieval_questions: ["CLAUDE.md 메모리 시스템란 무엇인가?", "CLAUDE.md 메모리 시스템의 핵심 개념은?", "CLAUDE.md 메모리 시스템의 핵심 특성은 무엇인가?", "CLAUDE.md 메모리 시스템의 2026년 3계층 지침 분할은 무엇인가?", "CLAUDE.md 메모리 시스템의 CLAUDE.md 작성은 무엇인가?"]
related_chunks: ["v3-05-claude-md-memory-02", "v3-01-skills-setup", "v3-02-hooks-setup"]
supersedes: ["chunk.029", "chunk.030"]
---

# CLAUDE.md 메모리 시스템 (1/2)

> **범위**: 정의, 설정법 · **출처 문서**: `01_concepts/05-claude-md-memory.md`

## 정의

`CLAUDE.md`는 Claude Code 세션이 시작될 때 가장 먼저 읽는 파일로, 에이전트의 "운영체제" 역할을 합니다. 프로젝트 규칙, 아키텍처 결정, 코딩 표준, 메모리 라우팅을 포함하며, 항상 활성화되는(always-on) 컨텍스트를 제공합니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 위치 | 프로젝트 루트 또는 `~/.claude/` (사용자 글로벌) |
| 로딩 | 세션 시작 시 자동 로드 (항상 활성) |
| 역할 | 프로젝트 구조, 네이밍 컨벤션, 접근 불가 영역, 워크플로우 규칙 |
| 2026년 발전 | 5개 프리미티브(Rules, Skills, Subagents, Hooks, Output Styles)와 병행 |

### 2026년 3계층 지침 분할

`CLAUDE.md`를 가볍게 유지하고, 스코프별 지침은 분산 배치:

| 계층 | 위치 | 로딩 방식 | 용도 |
|------|------|-----------|------|
| CLAUDE.md | 프로젝트 루트 | 항상 로드 | 안정적인 전역 규칙 |
| Path-scoped Rules | `.claude/rules/*.md` | 매칭 파일 접근 시만 로드 | 특정 경로 규칙 |
| Skills | `.claude/skills/<name>/SKILL.md` | 온디맨드 | 반복되는 워크플로우 |

## 설정법

### 1. CLAUDE.md 작성

```markdown
# 프로젝트 이름

## 아키텍처
- 파일은 150줄 미만으로 유지, 링크로 탐색
- AI는 원본 콘텐츠를 편집하지 않음

## 코딩 표준
- Python: PEP 8 준수, 타입 힌트 필수
- 함수는 단일 책임 원칙
- 모든 공개 함수에 docstring

## 접근 불가 영역
- .env 파일 절대 수정 금지
- migrations/ 디렉토리는 읽기 전용
- production 브랜치에 직접 푸시 금지

## 워크플로우
- PR 생성 전 테스트 실행
- 커밋 메시지는 Conventional Commits 형식
- 보안 관련 변경은 계획 모드 필수
```

### 2. /init 명령으로 자동 생성

```bash
# 프로젝트에서 Claude Code 시작 후
/init

# 추가 설명과 함께
/init This is a FastAPI backend with PostgreSQL database
```

Claude가 프로젝트를 분석하여 `CLAUDE.md` 초안을 생성합니다. 주기적으로 재실행하여 업데이트할 수 있습니다.

### 3. Rules 디렉토리 (2026년 신기능)

```
.claude/rules/
├── frontend.md      # 프론트엔드 파일 접근 시 로드
├── database.md      # DB 관련 파일 접근 시 로드
└── security.md      # 보안 관련 파일 접근 시 로드
```

Rules는 해당 경로의 파일이 편집될 때만 로드되어 컨텍스트를 절약합니다.
