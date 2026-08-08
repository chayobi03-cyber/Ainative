---
chunk_id: v3-mcp-version-migration
title: MCP 사양 버전 마이그레이션 가이드
category: specification
section_path: MCP > 마이그레이션
audience: ["개발자", "아키텍트"]
use_cases: ["사양 업그레이드 판단", "deprecated 기능 정리", "전송 방식 전환"]
tags: ["MCP", "migration", "2025-11-25", "2026-07-28", "deprecated", "stateless", "SSE"]
priority: high
confidence: draft
freshness: "2026-08"
source_documents: ["갭 분석 신규 집필 — 원본은 버전 목록만 있고 이행 절차 없음"]
retrieval_questions: ["MCP 사양을 어느 버전으로 올려야 하나요?", "SSE에서 Streamable HTTP로 어떻게 옮기나요?", "2026-07-28로 가면 무엇이 깨지나요?", "MCP deprecated 기능은 무엇인가요?", "MCP 최신 stable 버전은?"]
related_chunks: ["v3-mcp-spec", "v3-mcp-transport", "v3-mcp-dev-rules"]
---

# MCP 사양 버전 마이그레이션 가이드

## 한 줄 요약
**2026-07-28이 현재 최신 stable이다**(2026-07-28 게시). 신규 구축은 처음부터
**stateless 전제**로 설계하고, 기존 서버는 전송 → 인증 → 상태제거 순으로 이행한다.

> **집필 근거**: 원본 리서치 문서(2026-08-04 작성)는 각 리비전의 변경점을 나열했지만
> "무엇을 어떤 순서로 고쳐야 하는가"는 다루지 않았다. 아래 이행 순서는 원본에 기록된
> 변경점에서 도출한 설계 판단이다.
>
> **정정 이력**: 원본은 2026-07-28을 release candidate로 기술했으나, 2026-08-05 확인 결과
> **정식 stable로 게시**됐다(RC 잠금 2026-05-29 → stable 게시 2026-07-28). 이에 따라
> "정식화까지 보류" 권고를 철회하고 채택 판단표를 다시 썼다.
> 출처: `github.com/modelcontextprotocol/modelcontextprotocol/releases`

## 버전 선택 결정표

| 상황 | 권장 | 이유 |
|---|---|---|
| 신규 서버 구축 | **2026-07-28** | 현재 최신 stable. stateless core로 수평 확장이 단순해짐 |
| 보수적 신규 구축 | 2025-11-25 | 클라이언트 호환 범위를 넓게 잡아야 할 때. 단 deprecated 항목을 안고 감 |
| 기존 2025-03-26 서버 | 2025-06-18 경유 후 상위로 | structured output·elicitation이 중간 단계에 도입 |
| SSE 기반 기존 서버 | 즉시 Streamable HTTP | 2025-03-26에 deprecated, 제거 대상 |

**2026-07-28을 기본 권장으로 바꾼 이유**: stateless core는 `initialize` 핸드셰이크와
`Mcp-Session-Id` 헤더를 없앤다. 어떤 요청이든 아무 서버 인스턴스에 떨어져도 되므로
sticky routing과 공유 세션 저장소가 프로토콜 계층에서 불필요해진다. 사내 배포에서
이 단순화의 가치가 크다. 또한 공식 deprecation 정책이 생겨 **12개월 유예**가 보장된다.

## 이행 순서 (깨질 위험이 낮은 순)

### 1. 전송 방식 정리 — 가장 먼저
구형 HTTP+SSE(POST/GET 2개 엔드포인트)를 단일 `/mcp` Streamable HTTP로 옮긴다.
로컬은 stdio 유지. 이 단계는 클라이언트 호환성이 가장 넓어 되돌리기도 쉽다.

### 2. 인증 강화 — 보안 부채 상환
- 토큰 audience 검증(RFC 8707 `resource` 파라미터) 구현
- 세션 ID를 비결정론적으로 생성하고 사용자 정보에 바인딩
- 와일드카드 스코프(`*`, `all`, `full-access`) 제거

추가로 2026-07-28에서 확정된 항목(사양 changelog 원문 대조):
- 인가 서버가 RFC 9207 `iss`를 내려주고, 클라이언트가 **코드 교환 전에** 기록해 둔
  issuer와 대조한다(SEP-2468)
- DCR 사용 시 `application_type`을 명시한다 — OIDC redirect URI 충돌 회피(SEP-837)
- 자격증명을 **issuer를 키로** 보관한다. 인가 서버 간 재사용 금지, 서버 변경 시 재등록(SEP-2352)

**주의**: RFC 8707 `resource`의 MUST 요구는 완화 논의가 진행 중이다.
Dynamic Client Registration은 2025-11-25에서 SHOULD→MAY로 강등된 데 이어
**2026-07-28에서 정식 deprecated 됐다**(대체: Client ID Metadata Documents).
하위 호환을 위해 남아 있을 뿐이므로 신규 구현은 CIMD로 간다.
인증 구현 직전에 해당 리비전 원문을 다시 읽는다.

### 3. 상태 제거 — 2026-07-28의 핵심 변화
stateless core를 흡수한다. 서버를 stateless로 만들면 수평 확장 시 sticky routing이
불필요해지고, git worktree 병렬 세션 충돌도 함께 사라진다.
상태가 꼭 필요하면 외부 저장소로 빼고 문서화한다.

여기서 함께 깨지는 것들이 있다 — **라이브러리 업그레이드만으로 끝나지 않는다.**
`server/discover` 구현, 서버 개시 요청의 MRTR 전환, `subscriptions/listen` 전환,
`ping`·`logging/setLevel` 제거 대응이 같은 단계에 묶인다.
항목별 상세와 SEP 번호는 `v3-mcp-2026-07-28-changes`에 있다.

### 4. deprecated 항목 정리
2026-07-28에서 Roots / Sampling / Logging이 deprecated 됐다. 공식 deprecation 정책상
**deprecation과 제거 사이에 12개월 유예**가 있으므로 즉시 깨지지는 않지만,
신규 구현은 처음부터 대체 경로를 쓴다.

| deprecated 예정 | 대체 |
|---|---|
| Roots | tool parameters로 경로를 명시적으로 전달 |
| Sampling | 직접 provider API 호출 |
| Logging | stderr + OpenTelemetry |

## 이행 검증 체크리스트
- [ ] MCP Inspector `--method tools/list` 통과 (전송 전환 후)
- [ ] 스키마 `$ref`/`anyOf`가 실제 노출 형태로 확인됨
- [ ] 만료·타 대상 토큰이 HTTP 401로 거부되는지 테스트
- [ ] stdout에 JSON-RPC 외 출력이 없는지 확인
- [ ] 골든셋 회귀 재실행 — 전송 전환은 조용히 응답 형태를 바꿀 수 있다

## 롤백
전송 전환은 클라이언트 설정 한 줄이므로 서버를 이전 엔드포인트와 **병행 운영**하다가
전환이 안정되면 구 엔드포인트를 닫는다. 인증 강화는 롤백이 어렵다 — 스테이징에서 먼저 검증한다.
