---
chunk_id: "v3-07-tool-generation-agent-03"
title: "툴 생성 에이전트 — 예외 사례"
category: "concept"
section_path: "01_concepts > 툴 생성 에이전트"
audience: ["개발자", "신규입사자"]
tags: ["mcp", "roadmap", "skills", "tool-generation-agent", "workflow"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/07-tool-generation-agent.md"]
source_urls: ["https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://www.anthropic.com/engineering/advanced-tool-use", "https://www.anthropic.com/engineering/building-effective-agents", "https://www.anthropic.com/engineering/code-execution-with-mcp", "https://www.anthropic.com/engineering/multi-agent-research-system", "https://www.anthropic.com/engineering/writing-tools-for-agents"]
retrieval_questions: ["툴 생성 에이전트에서 자주 발생하는 문제는?", "툴 생성 에이전트 트러블슈팅 방법은?", "툴 생성 에이전트의 보안 고려사항은?", "툴 생성 에이전트 권한 설정은 어떻게 하는가?"]
related_chunks: ["v3-07-tool-generation-agent-01", "v3-07-tool-generation-agent-02"]
supersedes: ["chunk.098", "chunk.099"]
---

# 툴 생성 에이전트 (3/3)

> **범위**: 예외 사례, 보안 고려사항 · **출처 문서**: `01_concepts/07-tool-generation-agent.md`

## 예외 사례

### 실패·안티패턴

- Gartner는 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망. McKinsey는 23%의 기업만이 AI 에이전트를 스케일한다고 봄
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과. 파일럿의 88%는 출시되지 못함
- 내부 헬프데스크가 강력한 첫 에이전트인 이유: 데이터를 소유하고 있고 실패 비용이 낮기 때문
- 비용 사고: 한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금을 기록. Microsoft는 비용 초과로 롤아웃 공개 철회
- 가장 흔한 비용 급증 원인: 서브에이전트 팬아웃(하나의 태스크가 20개 이상 병렬 에이전트 스폰)과 autocompact 루프

### 흔한 실수

- 커밋 메시지 포맷을 Skill로 만들기 (→ CLAUDE.md가 적합)
- 배포 체크리스트를 Skill로 만들기 (→ slash command가 적합)
- GitHub 접근을 Skill에 기대기 (→ MCP가 적합)
- "plugin vs skill"을 갈림길로 보기 — skill은 역량 단위, plugin은 배포 단위

### 주의사항

- 커뮤니티 블로그 비중이 높음. hook 이벤트 개수, 버전 번호, 모델 가격 등은 출처마다 상이
- MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심함. 자체 PoC 필수
- 기업 도입 수치는 대부분 2차 인용. 1차 발표 확인 전까지 참고 수준만
- 가격은 도입기 할인이 걸려 있어 재확인 필요

## 보안 고려사항

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
