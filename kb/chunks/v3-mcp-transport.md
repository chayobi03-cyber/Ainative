---
chunk_id: "v3-mcp-transport"
title: "MCP 전송 방식: stdio와 Streamable HTTP"
category: "specification"
section_path: "MCP > Transport"
audience: ["개발자", "아키텍트", "운영자"]
use_cases: ["MCP 서버 전송 방식 선택", "로컬/원격 배포 설계"]
tags: ["MCP", "transport", "stdio", "streamable-http", "SSE", "deprecated"]
priority: "high"
confidence: "verified"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["MCP 전송 방식은 무엇이 있는가?", "SSE는 왜 사용하지 말아야 하는가?", "stdio의 한계는 무엇인가?"]
related_chunks: ["v3-mcp-spec", "v3-mcp-dev-rules"]
supersedes: ["rag-mcp-transport-001"]
---

# MCP 전송 방식: stdio와 Streamable HTTP

## 한 줄 요약
MCP 사양이 정의하는 live 전송 옵션은 stdio(로컬)와 Streamable HTTP(원격) 두 가지뿐이다. 구형 HTTP+SSE는 deprecated되었으므로 신규 구축에서는 배제해야 한다.

## 언제 참고하나
- MCP 서버의 전송 방식을 결정할 때
- 로컬 vs 원격 배포 아키텍처를 설계할 때
- SSE 기반 기존 구현의 마이그레이션을 계획할 때

## 핵심 내용

### stdio (로컬)
- 로컬 서브프로세스, stdin/stdout으로 newline-delimited JSON-RPC 통신.
- 구현이 단순하지만 동시 부하에 취약 (한 테스트에서 20 동시연결 중 22요청 중 20 실패 보고).
- Claude Code, Gemini CLI 모두 로컬 MCP 서버에 stdio를 사용.

### Streamable HTTP (원격)
- 단일 엔드포인트 `/mcp`, 필요 시 SSE 스트림 업그레이드.
- HTTP/1.1 chunked로 동작, HTTP/2 불필요.
- TypeScript SDK 1.10.0(2025-04-17)이 Streamable HTTP를 최초 지원.

### HTTP+SSE (deprecated)
- 2024-11-05 초기 방식 (POST/GET 두 엔드포인트).
- 2025-03-26에 deprecated 처리.
- 2026-07-28 stable에서 정식 Deprecated 라이프사이클로 분류, 향후 제거 대상.
- **신규 구축에서 절대 사용 금지.**

## 권고사항
- **로컬**: stdio
- **원격/사내 웹**: Streamable HTTP
- **SSE**: 신규 구축에서 배제
