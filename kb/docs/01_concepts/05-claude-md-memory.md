---
id: concept.claude-md-memory
title: CLAUDE.md 메모리 시스템
category: concepts
tags: [claude-md, memory, project-rules, context, configuration]
source_urls:
  - https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/
  - https://news.creeta.com/en/claude-code-best-practices-2026/
  - https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/
last_reviewed: 2026-08-05
chunking_policy: whole-document
---

# CLAUDE.md 메모리 시스템

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

## 운영 가이드

### CLAUDE.md 작성 원칙

1. **짧고 명확하게**: 에이전트가 매 세션마다 읽는 파일, 불필요한 내용 배제
2. **"무엇인가"가 아닌 "어떻게 작동하는가"**: 프로젝트 구조, 네이밍, 접근 불가 영역 명시
3. **안정적인 규칙만**: 자주 변경되지 않는 규칙만 포함
4. **주기적 업데이트**: 워크플로우 변화 시 업데이트 (주 1회 권장)
5. **중복 금지**: 동일 지침이 CLAUDE.md와 Skills/Rules에 중복되지 않도록 주의

### `/init` 명령 활용

- 프로젝트 분석 후 CLAUDE.md 자동 생성
- 저장소의 구조와 주요 파일을 분석하여 적절한 규칙 제안
- 주기적 재실행으로 최신 상태 유지

### 메모리 라우팅 패턴

CLAUDE.md를 통해 에이전트가 정보를 어디에 저장할지 지시:

```markdown
## 데이터 라우팅
- 음성 메모: projects/X/ai-docs/ 또는 personal/diary/
- TODO: project-specific tasks.md
- 프로젝트 사실: projects/X/overview.md
- 태그와 프로젝트 링크: 원본 텍스트 하단에 추가
```

## 예외 사례

### CLAUDE.md가 너무 큰 경우

- 2026년 이전에는 모든 지침을 CLAUDE.md에 넣는 경향이 있었음
- 해결: 항상 활성 규칙만 CLAUDE.md에 유지, 나머지는 Rules 또는 Skills로 분산
- 지침 간 중복 제거 필수

### Rules가 로드되지 않는 경우

- `.claude/rules/` 디렉토리 경로 확인
- 매칭되는 파일이 실제로 접근되어야 로드됨
- `InstructionsLoaded` 훅으로 로드 시점 확인 가능

### /init으로 생성된 내용이 부정확한 경우

- 프로젝트에 대한 추가 설명을 `/init` 명령에 포함
- 생성된 CLAUDE.md를 수동으로 검토 및 수정
- 정기적으로 재실행하여 최신화

## 보안 고려사항

- CLAUDE.md는 저장소에 커밋되므로 민감 정보 배제
- 접근 불가 영역(`.env`, `secrets/`)을 명시적으로 선언
- `permissions.deny`와 CLAUDE.md 규칙을 함께 사용하여 다층 방어

## 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [Skills (스킬)](./02-skills.md)
- [Hooks (훅)](./03-hooks.md)
- [Subagents (서브에이전트)](./06-subagents.md)
- [보안 및 거버넌스](../03_operations/01-security-governance.md)

## 출처

- [My Claude Code Setup After 4 Months of Daily Use (2026) — Daniil Okhlopkov](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)
- [Claude Code Best Practices 2026 — Creeta News](https://news.creeta.com/en/claude-code-best-practices-2026/)
- [Claude Code Documentation: 2026 Working Guide — Petronella Tech](https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/)
