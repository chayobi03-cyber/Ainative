---
chunk_id: chunk.103
source_file: 01_concepts/08-context-engineering.md
title: "컨텍스트 엔지니어링"
section: "설정법"
section_id: setup
category: concept
tags: [context-engineering, agents-md, memory, llms-txt, compact]
---

# 컨텍스트 엔지니어링 - 설정법

### AGENTS.md 단일 소스 전략

```
repo/
├── AGENTS.md              # ← 정본. 프로젝트 개요, 빌드/테스트 명령, 코드 스타일
├── CLAUDE.md              # @AGENTS.md + Claude 전용 항목만
├── GEMINI.md              # AGENTS.md 내용 참조 + Gemini 전용
└── packages/
    └── mcp-gen/AGENTS.md  # 서브프로젝트별 오버라이드
```

```markdown
<!-- CLAUDE.md -->
@AGENTS.md

## Claude Code 전용
- 서브에이전트는 model: haiku 사용
- .claude/hooks/ 의 가드를 우회하지 말 것
```

### AGENTS.md에 넣을 것

- 정확한 명령어 (uv run pytest -m "not integration", 플래그 포함)
- 언어 기본값과 다른 규칙만
- 하지 말아야 할 것 (금지 경로, 금지 패턴)
- 언어 기본 스타일 재설명, 일반론, 장문의 아키텍처 서사는 제외

### 모노레포

각 패키지에 AGENTS.md를 둡니다. 에이전트는 편집 중인 파일에 가장 가까운 파일을 읽습니다. OpenAI의 Codex 저장소는 디렉터리 트리 전반에 88개의 AGENTS.md를 사용합니다.

### 파일 기반 메모리 패턴

```markdown
<!-- CONTINUE.md — 세션 종료 시 에이전트가 갱신 -->
## Next Session
- **Active Task:** mcp-gen-042
- **Current Focus:** search_customers 툴 스키마 확정
- **Blockers:** 사내 CRM API 페이지네이션 스펙 미확인
## Recent Changes
- FastMCP 서버 스켈레톤 생성
- mcp-eval 골든셋 12/30 작성
```
Stop hook으로 자동 갱신을 강제하면 더 안정적입니다.