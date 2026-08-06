---
chunk_id: chunk.131
source_file: 05_mcp_catalog/03-agent-frameworks-and-gateways.md
title: "에이전트 프레임워크 및 게이트웨이"
section: "MCP 게이트웨이"
section_id: mcp-gateways
category: catalog
tags: [agent-framework, langgraph, claude-agent-sdk, temporal, mcp-gateway, fastmcp]
---

# 에이전트 프레임워크 및 게이트웨이 - MCP 게이트웨이

### MCP Gateway 도입 시점

1단계(MCP 서버 몇 개)에서는 불필요. 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입을 검토합니다.

### 오픈소스 후보 (벤더 블로그 기준, 자체 PoC 필수)

| 게이트웨이 | 특징 | 비고 |
|------------|------|------|
| MCPX (Lunar) | Tool Groups, 툴 커스터마이징, 로컬/원격 MCP 인증 | 팀별 다른 툴 부분집합 |
| Bifrost (Maxim AI, Go) | MCP 클라이언트이자 서버, STDIO/HTTP/SSE 진재, 단일 /mcp 노출 | ⚠️ 자사 콘텐츠에서 자사 1위 |
| MetaMCP | 단일 엔드포인트 라우팅 + BM25 툴 필터링, 활동 로깅, 격리 보안, 웹 UI | BM25 툴 필터링이 툴 폭발에 유효 |
| IBM ContextForge | K8s 환경 세션 인식 라우팅 | 목록: e2b-dev/awesome-mcp-gateways |
| MCPJungle / Obot / Open Edison / Microsoft MCP Gateway | 데이터 유출 방지, 실행 통제 | 목록: e2b-dev/awesome-mcp-gateways |

### 평가 기준

- 런타임·언어 (Go vs Python 요청당 오버헤드 차이)
- 프로토콜 범위 (단순 진재만 하는지, REST/gRPC를 MCP 툴로 변환하는지)
- 레이트리밋·쿼터를 툴별/테넌트별/에이전트역할별로 걸 수 있는지
- 관측성 깊이 (툴 호출 활동이 쿼리 가능하고 SIEM으로 내보낼 수 있는지)