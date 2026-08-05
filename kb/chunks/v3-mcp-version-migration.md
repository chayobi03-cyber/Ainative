---
chunk_id: "v3-mcp-version-migration"
title: "MCP 사양 버전 마이그레이션 가이드"
category: "specification"
section_path: "MCP > 마이그레이션"
audience: ["개발자", "아키텍트"]
use_cases: ["사양 업그레이드 판단", "deprecated 기능 정리", "전송 방식 전환"]
tags: ["MCP", "migration", "2025-11-25", "2026-07-28", "deprecated", "stateless", "SSE"]
priority: "high"
confidence: "draft"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["갭 분석 신규 집필 — 원본은 버전 목록만 있고 이행 절차 없음"]
retrieval_questions: ["MCP 사양을 어느 버전으로 올려야 하나요?", "SSE에서 Streamable HTTP로 어떻게 옮기나요?", "2026-07-28 RC로 가면 무엇이 깨지나요?", "MCP deprecated 기능은 무엇인가요?"]
related_chunks: ["v3-mcp-spec", "v3-mcp-transport", "v3-mcp-dev-rules"]
---

# MCP 사양 버전 마이그레이션 가이드

## 한 줄 요약
신규 구축은 **2025-11-25 stable에 고정**하고, 2026-07-28 RC는 정식화 전까지 채택하지 않되
**stateless 전제로 설계**해 두어 이행 비용을 미리 없앤다.

> **집필 근거**: 원본 리서치 문서는 각 리비전의 변경점을 나열했지만 "무엇을 어떤 순서로
> 고쳐야 하는가"는 다루지 않았다. 아래 이행 순서는 원본에 기록된 변경점에서 도출한
> 설계 판단이며, 실제 적용 전 각 리비전 원문으로 재확인해야 한다.

## 버전 선택 결정표

| 상황 | 권장 | 이유 |
|---|---|---|
| 신규 서버 구축 | **2025-11-25** | 최신 stable. CIMD·incremental scope 확보 |
| 기존 2025-03-26 서버 | 2025-06-18 경유 후 2025-11-25 | structured output·elicitation이 중간 단계에 도입 |
| 2026-07-28 RC 채택 | **보류** | RC 단계. 정식화 시 core가 stateless로 바뀜 |
| SSE 기반 기존 서버 | 즉시 Streamable HTTP | 2025-03-26에 deprecated, RC에서 제거 대상 |

## 이행 순서 (깨질 위험이 낮은 순)

### 1. 전송 방식 정리 — 가장 먼저
구형 HTTP+SSE(POST/GET 2개 엔드포인트)를 단일 `/mcp` Streamable HTTP로 옮긴다.
로컬은 stdio 유지. 이 단계는 클라이언트 호환성이 가장 넓어 되돌리기도 쉽다.

### 2. 인증 강화 — 보안 부채 상환
- 토큰 audience 검증(RFC 8707 `resource` 파라미터) 구현
- 세션 ID를 비결정론적으로 생성하고 사용자 정보에 바인딩
- 와일드카드 스코프(`*`, `all`, `full-access`) 제거

**주의**: RFC 8707 `resource`의 MUST 요구는 완화 논의가 진행 중이고, Dynamic Client
Registration은 2025-11-25에서 SHOULD→MAY로 강등되며 CIMD로 대체되었다.
인증 구현 직전에 해당 리비전 원문을 다시 읽는다.

### 3. 상태 제거 — RC 대비 선투자
2026-07-28 RC의 stateless core를 미리 흡수한다. 서버를 가능한 한 stateless로 만들면
RC 정식화 시 이행 비용이 거의 0이 되고, 동시에 git worktree 병렬 세션 충돌도 사라진다.
상태가 꼭 필요하면 외부 저장소로 빼고 문서화한다.

### 4. deprecated 예고 항목 회피
RC 기준 Roots / Sampling / Logging이 deprecated 예정이다. 신규 구현은 대체 경로를 쓴다.

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
