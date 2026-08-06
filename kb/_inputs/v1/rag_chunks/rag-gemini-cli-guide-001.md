---
chunk_id: rag-gemini-cli-guide-001
title: Gemini CLI 운영 가이드
category: operations
section_path: "운영 > Gemini CLI"
audience: ['개발자', '운영자']
use_cases: ['Gemini CLI 일상 운영', '팀 표준화', '효율적 사용']
tags: ['Gemini-CLI', 'settings.json', 'checkpointing', 'excludeTools', 'GEMINI.md', 'extensions']
priority: medium
source_documents: ['Ainativetipbook0805.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['Gemini CLI 설정은 어디에?', 'checkpointing이란?', 'excludeTools는 무엇인가?', 'Gemini CLI 권장 습관은?']
related_chunks: ['rag-claude-code-guide-001', 'rag-cli-registration-001']
---
# Gemini CLI 운영 가이드

## 한 줄 요약
Gemini CLI는 설정 파일 기반 운영이 명확해서 팀 단위 표준화에 잘 맞는다. mcpServers와 command 기반 구성으로 서버 허용 범위와 실행 규칙을 통제할 수 있다.

## 핵심 명령/설정
- `gemini mcp <add|list|remove>`: MCP 서버 등록/관리
- `~/.gemini/settings.json` 또는 `.gemini/settings.json`: mcpServers 블록
- `/mcp`: 서버 관리
- `/settings`: 환경 설정 확인
- `gemini --checkpointing`: 파일 수정 전 스냅샷
- `Ctrl+L`: 화면 정리

## 권장 습관
- 프로젝트마다 필요한 MCP만 등록한다.
- 비밀값은 환경변수로 주고 설정 파일에 평문으로 넣지 않는다.
- 개인용 단축어와 팀 표준을 분리한다.
- 파일 수정형 작업은 checkpoint를 기본으로 둔다.

## 도구 제한 정책
- `excludeTools`와 include 정책을 쓰면, 필요한 도구만 보여주는 제한적 UI를 만들 수 있다.
- 툴 병합은 "가장 제한적 정책 승리" (excludeTools union, includeTools intersection)

## Custom Commands vs Extensions
- custom slash command와 extension을 분리하면 개인용 자동화와 팀용 자동화를 분리하기 쉽다.
