---
chunk_id: "v3-agents-md"
title: "AGENTS.md 단일 소스 전략"
category: "development"
section_path: "컨텍스트 엔지니어링 > AGENTS.md"
audience: ["개발자", "아키텍트"]
use_cases: ["3사 CLI 컨텍스트 통합", "drift 방지", "모노레포 컨텍스트 관리"]
tags: ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "AAIF", "single-source", "monorepo"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["AGENTS.md란?", "3사 CLI 컨텍스트 중복을 어떻게 해결하는가?", "AGENTS.md에 무엇을 넣어야 하는가?", "모노레포에서 AGENTS.md는?"]
related_chunks: ["v3-file-memory", "v3-llms-txt"]
supersedes: ["rag-agents-md-001"]
---

# AGENTS.md 단일 소스 전략

## 한 줄 요약
3사 CLI가 각자 다른 컨텍스트 파일을 읽는 파편화를 AGENTS.md 하나로 수렴한다. 2025년 12월 Linux Foundation 산하 Agentic AI Foundation(AAIF)이 결성되어 AGENTS.md는 60,000개 이상의 오픈소스 repo와 다수 에이전트 프레임워크에 채택되었다.

## 배경
- 2025년 12월 Linux Foundation이 OpenAI, Anthropic, Block을 창립 멤버로 Agentic AI Foundation(AAIF) 결성
- Anthropic은 MCP를, OpenAI는 AGENTS.md를 기증
- 60,000개 이상의 오픈소스 repo와 Codex, Cursor, Devin, Factory, Gemini CLI, GitHub Copilot, Jules, VS Code, Amp 등에 채택

## 전략
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

## AGENTS.md에 넣을 것
- 정확한 명령어 (`uv run pytest -m "not integration"`, 플래그 포함)
- 언어 기본값과 **다른** 규칙만
- 하지 말아야 할 것 (금지 경로, 금지 패턴)
- ❌ 언어 기본 스타일 재설명, 일반론, 장문의 아키텍처 서사

## 모노레포
- 각 패키지에 AGENTS.md를 둔다
- 에이전트는 편집 중인 파일에 가장 가까운 파일을 읽는다
- OpenAI의 Codex 저장소는 디렉터리 트리 전반에 88개의 AGENTS.md 사용

## 보안 주의
- NVIDIA가 간접 AGENTS.md 인젝션 공격 완화를 다룬 기술 블로그를 발행
- 외부에서 받은 repo의 AGENTS.md를 무비판 신뢰 금지
- 사내 규칙: 외부 repo 작업 시 AGENTS.md를 사람이 먼저 읽는다

## 난이도/소요
하 | 1시간
