---
chunk_id: "v3-mcp-gateway"
title: "MCP Gateway 도입 판단"
category: "architecture"
section_path: "MCP 운영 > Gateway"
audience: ["아키텍트", "운영자"]
use_cases: ["MCP 서버 수 증가 대응", "인증·권한 중앙화", "토큰 비용 최적화"]
tags: ["MCP-gateway", "MCPX", "Bifrost", "MetaMCP", "tool-explosion", "aggregation"]
priority: "low"
confidence: "mixed"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["MCP Gateway란?", "언제 MCP Gateway를 도입해야 하는가?", "MCP Gateway 오픈소스 후보는?"]
related_chunks: ["v3-deployment-governance", "v3-cli-registration"]
supersedes: ["rag-mcp-gateway-001"]
---

# MCP Gateway 도입 판단

## 한 줄 요약
여러 MCP 서버를 단일 엔드포인트 뒤로 짚하고 인증·권한·감사를 한 곳에서 처리하는 MCP Gateway는, 서버가 5개를 넘거나 여러 팀이 쓰기 시작할 때 도입을 고려한다.

## 왜 필요한가
10개 MCP 서버를 운영하는 팀은 10개의 커넥션, 10벌의 크리덴셜, 그리고 모든 AI 클라이언트가 매 요청마다 로드하는 10개의 툴 카탈로그를 유지해야 한다. 개수가 늘면 서버별 설정, 부재한 접근 제어, 수백 개 툴 정의를 컨텍스트에 밀어 넣는 토큰 비용이 주된 장애물이 된다.

## 오픈소스 후보 (⚠️ 벤더 콘텐츠 오염 주의, 자체 PoC 필수)

| 게이트웨이 | 특징 |
|---|---|
| MCPX (Lunar) | Tool Groups, 툴 커스터마이징, 팀별 다른 툴 부분집합 |
| Bifrost (Maxim AI, Go) | STDIO/HTTP/SSE 연결, 단일 /mcp 노출, LLM 라우팅 |
| MetaMCP | 단일 엔드포인트 라우팅 + BM25 툴 필터링, 격리 보안 |
| Microsoft MCP Gateway | K8s 세션 인식 라우팅·라이프사이클 관리 |
| Open Edison | 데이터 유출 방지·실행 통제 |

## 평가 기준
- 런타임·언어 (Go vs Python 오버헤드)
- 프로토콜 범위 (단순 짚만 vs REST/gRPC 변환)
- 레이트리밋·쿼터 (툴별/테넌트별/에이전트역할별)
- 관측성 깊이 (툴 호출 활동이 쿼리 가능하고 SIEM으로 내보낼 수 있는가)

## 판단 가이드
- **1단계(MCP 서버 몇 개)에서는 불필요**
- 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입
- "게이트웨이 도입"은 되돌리기 어려운 결정이므로 `managed-mcp.json` 거버넌스로 먼저 버티고, 필요가 실증되면 도입

## 주의사항
- MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심함 (Bifrost 관련 글 다수가 Maxim AI 자사 콘텐츠에서 자사를 1위로 놓음)
- 순위를 신뢰하지 말고 자체 PoC로 검증
