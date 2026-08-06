---
chunk_id: rag-claude-code-guide-001
title: Claude Code 운영 가이드
category: operations
section_path: "운영 > Claude Code"
audience: ['개발자', '운영자']
use_cases: ['Claude Code 일상 운영', '팀 표준화', '효율적 사용']
tags: ['Claude-Code', '/init', '/doctor', 'claude -p', 'auto-mode', 'CLAUDE.md']
priority: medium
source_documents: ['Ainativetipbook0805.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['Claude Code에서 가장 먼저 해야 할 것은?', '/init와 /doctor의 용도는?', 'claude -p는 언제 쓰는가?', 'Claude Code 권장 습관은?']
related_chunks: ['rag-gemini-cli-guide-001', 'rag-hooks-001', 'rag-cli-registration-001']
---
# Claude Code 운영 가이드

## 한 줄 요약
Claude Code는 "작업 범위 통제"와 "증거 기반 결과 확인"이 핵심이다. /init로 CLAUDE.md를 만들고, /doctor로 환경을 점검하며, 프로젝트별 MCP를 분리하는 것이 안정적이다.

## 핵심 명령
- `/init`: CLAUDE.md 초안 생성. 팀 규칙과 빌드/테스트 명령을 짧게 유지.
- `/doctor`: 환경 이상을 빠르게 찾는 데 유용.
- `claude mcp add <name> <command>`: 외부 도구 연결.
- `claude -p`: 비대화형 모드. CI, pre-commit, 자동 리팩터링 파이프라인에 적합.
- `/plugin`: 팀 공유 플러그인 관리.

## 권장 습관
- 작업 전 "무엇을 만들지"보다 "어떻게 확인할지"를 먼저 적는다.
- 하나의 요청에 너무 많은 목표를 섞지 않는다.
- 관련 파일과 제약을 구체적으로 지정한다.
- 결과를 받을 때는 코드와 검증 방법을 같이 받는다.

## 자주 쓰는 패턴
- "먼저 계획만."
- "구현은 나중."
- "테스트 포함."
- "실패 케이스 추가."
- "호환성 유지."

## 프로젝트 스코프 MCP
- 프로젝트 스코프 MCP는 승인 흐름이 붙기 때문에, 민감한 내부 서버는 전역보다 프로젝트 단위로 두는 편이 안전.
- 전역 MCP를 너무 많이 두면 컨텍스트와 관리 복잡도가 같이 늘어남.
