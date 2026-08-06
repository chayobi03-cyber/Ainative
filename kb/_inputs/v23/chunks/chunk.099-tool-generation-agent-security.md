---
chunk_id: chunk.099
source_file: 01_concepts/07-tool-generation-agent.md
title: "툴 생성 에이전트"
section: "보안 고려사항"
section_id: security
category: concept
tags: [tool-generation-agent, mcp, skills, workflow, roadmap]
---

# 툴 생성 에이전트 - 보안 고려사항

### MCP 보안 통제 (사양 필수)

- 토큰 패스스루 금지: "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server."
- RFC 8707 Resource Indicators: resource 파라미터는 authorization·token 요청 모두에 포함
- 세션: "MCP servers MUST NOT use sessions for authentication", secure non-deterministic session IDs (UUID), user-specific binding
- 로컬 서버 원클릭 설정: 실행 명령 전 consent 메커니즘 MUST 구현, 위험 작업 경고
- Confused deputy 방지: per-client consent, client_id 레지스트리, redirect_uri 정확 문자열 일치
- 스코프 최소화: 최소 초기 스코프 + WWW-Authenticate scope 챌린지로 증분 상승. 와일드카드/omnibus 스코프 금지

### 실제 보안 사고

- mcp-remote CVE-2025-6514: CVSS 9.6 OS 커맨드 인젝션, 437,000+ 다운로드
- Cursor CVE-2025-54136(MCPoison), CVE-2025-54135(CurXecute): config swap/rug pull
- Postmark MCP 백도어: 유지관리자가 공식 패키지에 BCC 로직 추가로 전 메일 탈취
- arXiv:2508.12538: 배포된 1,800+ MCP 서버 중 30%+가 최소 하나 이상의 취약점
- MCPTox 벤치: 최고 공격성공률 o1-mini 72.8%, 강한 모델이 오히려 더 취약. Claude-3.7-Sonnet조차 거부율 3% 미만

### rug pull 완화

ETDI(서명된 JWT에 툴 정의 바인딩, 정의 변경 시 서명 무효화) 제안. 툴 정의 서명/해시 고정으로 방지.