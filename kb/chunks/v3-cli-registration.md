---
chunk_id: "v3-cli-registration"
title: "Claude Code와 Gemini CLI MCP 등록 및 호환성"
category: "reference"
section_path: "운영 > CLI 등록"
audience: ["개발자", "운영자"]
use_cases: ["MCP 서버 등록", "클라이언트 설정", "이식성 확보"]
tags: ["Claude-Code", "Gemini-CLI", "mcpServers", "managed-settings", "compatibility"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["Claude Code에 MCP 서버를 어떻게 등록하는가?", "Gemini CLI에 MCP 서버를 어떻게 등록하는가?", "두 CLI 간 MCP 서버 이식성은?", "managed-settings.json이란?"]
related_chunks: ["v3-claude-code-guide", "v3-gemini-cli-guide"]
supersedes: ["rag-cli-registration-001"]
---

# Claude Code와 Gemini CLI MCP 등록 및 호환성

## 한 줄 요약
두 클라이언트 모두 stdio + Streamable HTTP를 지원하고 `mcpServers` JSON 키를 공유하므로 서버 자체는 이식 가능하다. 차이는 컨텍스트 파일, 확장 패키징, 신뢰/승인 UX, redaction 정책에 있다.

## Claude Code
- 프로젝트 스코프: `.mcp.json` (루트)
- 사용자 스코프: `~/.claude.json`
- CLI 등록: `claude mcp add <name> <command>`
- 설정 정밀도: **managed > project > user > local**
- `managed-settings.json` + `managed-mcp.json`으로 IT 강제 정책 (예: `Bash(curl *)` deny — 하위 스코프 오버라이드 불가)
- `strictKnownMarketplaces` (마켓플레이스 allowlist)
- MCP 출력은 `MAX_MCP_OUTPUT_TOKENS`(기본 25,000)로 제어

## Gemini CLI
- 설정: `~/.gemini/settings.json` 또는 `.gemini/settings.json`의 `mcpServers` 블록
- CLI: `gemini mcp <add|list|remove>`
- Extensions: `gemini-extension.json` (mcpServers, `contextFileName`=GEMINI.md, `excludeTools`, `${extensionPath}`)
- 시크릿은 `"$MY_KEY"` 환경변수 확장 권장
- `*TOKEN*/*SECRET*/*PASSWORD*/*KEY*/*AUTH*/*CREDENTIAL*` 자동 redaction
- 툴 병합은 "가장 제한적 정책 승리" (excludeTools union, includeTools intersection)
- `gemini --checkpointing`으로 파일 수정 전 스냅샷

## 호환성 요약
- 두 클라이언트 모두 stdio + Streamable HTTP 지원
- `mcpServers` JSON 키 공유 → 서버 자체 이식 가능
- 차이: 컨텍스트 파일(CLAUDE.md vs GEMINI.md), 확장 패키징(plugin vs extension), 신뢰/승인 UX, redaction 정책
- 생성 에이전트는 양쪽 config를 모두 산출하도록 설계할 것
