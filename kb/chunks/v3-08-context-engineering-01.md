---
chunk_id: "v3-08-context-engineering-01"
title: "컨텍스트 엔지니어링 — 정의"
category: "concept"
section_path: "01_concepts > 컨텍스트 엔지니어링"
audience: ["개발자", "신규입사자"]
tags: ["agents-md", "compact", "context-engineering", "llms-txt", "memory"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/08-context-engineering.md"]
source_urls: ["https://agents.md/", "https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://www.anthropic.com/engineering/writing-tools-for-agents", "https://www.linuxfoundation.org/press/linux-foundation-launches-agentic-ai-foundation"]
retrieval_questions: ["컨텍스트 엔지니어링란 무엇인가?", "컨텍스트 엔지니어링의 핵심 개념은?", "컨텍스트 엔지니어링는 어떻게 설정하는가?", "컨텍스트 엔지니어링 초기 구성 절차는?"]
related_chunks: ["v3-08-context-engineering-02", "v3-08-context-engineering-03"]
supersedes: ["chunk.102", "chunk.103"]
---

# 컨텍스트 엔지니어링 (1/3)

> **범위**: 정의, 설정법 · **출처 문서**: `01_concepts/08-context-engineering.md`

## 정의

컨텍스트 엔지니어링은 AI 에이전트에게 제공되는 컨텍스트(지시, 규칙, 문서, 메모리)를 체계적으로 관리하여 가장 놓치기 쉬운 고ROI 영역을 다루는 분야입니다.

### 핵심 개념

| 개념 | 설명 |
|------|------|
| AGENTS.md 단일 소스 | 3사 CLI(Claude Code, Gemini CLI, Codex)가 각자 다른 컨텍스트 파일을 읽는 파편화를 AGENTS.md 하나로 수렴 |
| 파일 기반 메모리 | 에이전트가 중간 결과·다음 단계를 파일에 쓰고 다음 세션에서 다시 읽게 하는 패턴 |
| llms.txt | 사내 API 문서·SDK 레퍼런스를 에이전트가 읽기 좋은 단일 마크다운 인덱스로 제공 |
| compact 지시문 | 컨텍스트 압축 시 보존할 정보를 명시하는 CLAUDE.md 블록 |

2025년 12월 Linux Foundation이 OpenAI, Anthropic, Block을 창립 멤버로 Agentic AI Foundation(AAIF)을 결성했으며, AGENTS.md는 60,000개 이상의 오픈소스 repo와 에이전트 프레임워크(Codex, Cursor, Devin, Gemini CLI, GitHub Copilot, Jules, VS Code, Amp)에 채택되었습니다.

## 설정법

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
