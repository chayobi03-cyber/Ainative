---
chunk_id: "v3-mcp-security-spec"
title: "MCP 보안: 사양 필수 통제 항목"
category: "security"
section_path: "MCP > 보안 > 필수 통제"
audience: ["개발자", "보안 담당자", "운영자"]
use_cases: ["MCP 서버 설계", "배포 전 보안 점검", "내부 감사 대응"]
tags: ["MCP", "OAuth", "token", "allowlist", "audit-log", "rug-pull", "RFC-8707", "scope"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["MCP 토큰 패스스루 금지 규칙은?", "RFC 8707 Resource Indicators가 왜 필요한가?", "MCP 세션 보안 요구사항은?", "로컬 서버 원클릭 설정 보안 요구사항은?", "Confused deputy 공격을 어떻게 막는가?"]
related_chunks: ["v3-mcp-security-cve", "v3-cli-registration"]
supersedes: ["rag-mcp-security-spec-001"]
---

# MCP 보안: 사양 필수 통제 항목

## 한 줄 요약
MCP 사양은 토큰 패스스루 금지, RFC 8707 Resource Indicators, 세션 보안, 로컬 consent, confused deputy 방지, 스코프 최소화를 필수 통제로 요구한다.

## 핵심 내용

### 1. 토큰 패스스루 금지
- "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server."
- "MCP clients MUST NOT send tokens to the MCP server other than ones issued by the MCP server's authorization server."

### 2. RFC 8707 Resource Indicators
- MCP clients MUST implement Resource Indicators for OAuth 2.0.
- `resource` 파라미터는 authorization·token 요청 모두에 포함, MCP 서버의 canonical URI 사용.
- MCP servers MUST validate that access tokens were issued specifically for them as the intended audience.
- 유효하지 않은/만료 토큰은 HTTP 401.

### 3. 세션
- "MCP servers MUST NOT use sessions for authentication"
- "MUST use secure, non-deterministic session IDs" (UUID·secure RNG)
- "SHOULD bind session IDs to user-specific information" (`<user_id>:<session_id>`)

### 4. 로컬 서버 원클릭 설정
- "MUST implement proper consent mechanisms prior to executing commands"
- 실행 명령 전체를 truncation 없이 표시
- 위험 작업(sudo, rm -rf) 경고, 명시적 승인
- stdio로 접근 제한

### 5. Confused deputy (proxy 서버) 방지
- "MUST implement per-client consent"
- 사용자별 승인 `client_id` 레지스트리를 3rd-party 인증 흐름 개시 전에 확인
- redirect_uri 정확 문자열 일치 (와일드카드 금지)
- state 파라미터 (암호학적 랜덤, 단회용, 10분 만료)
- `__Host-` 접두 + Secure/HttpOnly/SameSite=Lax 쿠키

### 6. 스코프 최소화 (2025-11-25)
- 최소 초기 스코프 (예: `mcp:tools-basic`) + WWW-Authenticate scope 챌린지로 증분 상승
- 와일드카드/omnibus 스코프 (`*`, `all`, `full-access`) 금지

## 운영 체크리스트
- [ ] 토큰 audience 검증(RFC 8707) 구현
- [ ] non-deterministic 세션 ID + user 바인딩
- [ ] 로컬 원클릭 consent 메커니즘
- [ ] per-client consent 레지스트리
- [ ] 최소 권한 스코프 (와일드카드 금지)
- [ ] allowlist, 감사로그 구현
