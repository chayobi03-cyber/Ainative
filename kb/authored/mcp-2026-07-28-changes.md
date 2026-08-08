---
chunk_id: v3-mcp-2026-07-28-changes
title: MCP 2026-07-28 파괴적 변경 전체 목록
category: specification
section_path: MCP > 2026-07-28 변경점
audience: ["개발자", "아키텍트"]
use_cases: ["사양 업그레이드 영향 평가", "기존 서버 호환성 점검", "신규 서버 설계"]
tags: ["MCP", "2026-07-28", "stateless", "MRTR", "server/discover", "subscriptions/listen", "resultType", "CIMD", "RFC 9207", "SEP"]
priority: high
confidence: verified
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["사양 저장소 changelog 원문 대조 신규 집필"]
source_urls: ["https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/specification/2026-07-28/changelog.mdx"]
retrieval_questions:
  - "MCP 2026-07-28에서 무엇이 깨지나요?"
  - "서버 개시 요청이 없어졌다는데 대신 무엇을 쓰나요?"
  - "MCP에서 ping이 사라졌나요?"
  - "resultType은 무엇이고 왜 필수가 됐나요?"
  - "MCP 알림 구독은 이제 어떻게 하나요?"
related_chunks: ["v3-mcp-spec", "v3-mcp-version-migration", "v3-mcp-transport"]
---

# MCP 2026-07-28 파괴적 변경 전체 목록

## 한 줄 요약
2026-07-28은 **전송 계층과 요청 모델을 함께 갈아엎은** 리비전이다. 세션·핸드셰이크·
서버 개시 요청이 사라지고 그 자리를 `server/discover`, `subscriptions/listen`,
Multi Round-Trip Requests가 대신한다. 기존 서버는 라이브러리 업그레이드만으로 넘어가지 않는다.

> **출처**: 사양 저장소의 2026-07-28 changelog 원문을 직접 대조했다(1차 출처).
> 각 항목의 SEP 번호를 함께 적었으므로 원문에서 바로 찾아볼 수 있다.
> 정정 이력은 `kb/corrections.yaml`의 C-002·V-005.

## 1. 상태 제거 — 요청 모델 자체가 바뀐다

`initialize` / `notifications/initialized` 핸드셰이크와 `Mcp-Session-Id` 헤더가
**제거됐다**(SEP-2575, SEP-2567). 모든 요청이 스스로를 설명한다.

| 무엇을 | 어디에 |
|---|---|
| 프로토콜 버전 | `_meta`의 `io.modelcontextprotocol/protocolVersion` |
| 클라이언트 역량 | `_meta`의 `io.modelcontextprotocol/clientCapabilities` |
| 클라이언트 신원 | `_meta`의 `io.modelcontextprotocol/clientInfo` |
| 서버 신원 | `_meta`의 `io.modelcontextprotocol/serverInfo` |

버전이 맞지 않으면 `UnsupportedProtocolVersionError`를 돌려준다.
`tools/list`·`resources/list`·`prompts/list`는 더 이상 연결마다 다른 결과를 낼 수 없고,
서버는 상태 대신 **서버가 발급한 명시적 핸들**을 툴 인자로 받는다(SEP-2567).

**신설 `server/discover`.** 서버가 반드시 구현해야 하는 RPC로 지원 프로토콜 버전·역량·
신원을 광고한다(SEP-2575). 클라이언트는 다른 요청 전에 호출하거나 stdio에서 하위 호환
탐지에 쓴다.

## 2. Multi Round-Trip Requests — 서버가 클라이언트에게 되묻는 방식

`roots/list`, `sampling/createMessage`, `elicitation/create` 같은 **서버 개시 요청이
전부 사라졌다**(SEP-2322). 열린 스트림이 필요했기 때문이다.

대신 서버는 처리 도중 입력이 필요하면 `resultType: "input_required"`인
`InputRequiredResult`를 `inputRequests`와 함께 **반환**한다. 클라이언트는 답을
`inputResponses`에 담아 **원래 요청을 재시도**한다.

이에 따라 모든 결과에 `resultType`이 필수가 됐다 — 보통은 `"complete"`,
MRTR 중간 결과는 `"input_required"`. 이전 리비전 응답에 이 필드가 없으면
클라이언트는 `"complete"`로 취급해야 한다.

URL mode elicitation의 `notifications/elicitation/complete`와 `elicitationId`도 함께
제거됐다. 재시도로 결과를 알게 되므로 서버는 상관 식별자를 `requestState`에 넣는다.

## 3. 구독 모델 — HTTP GET이 사라졌다

HTTP GET 엔드포인트와 `resources/subscribe`/`resources/unsubscribe`가
**`subscriptions/listen` 하나로 대체**됐다(SEP-2575). POST 응답을 길게 열어 두는
스트림이며 클라이언트가 받을 종류를 고른다 — `toolsListChanged`,
`promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions`.
서버는 알림에 `io.modelcontextprotocol/subscriptionId`를 붙인다.

요청에 딸린 알림(`notifications/progress`, `notifications/message`)은 그 요청의
응답 스트림으로 흐른다.

**SSE 재개가 없어졌다.** `Last-Event-ID` 헤더와 SSE 이벤트 ID 기반 재전송이
제거됐으므로, 스트림이 끊기면 클라이언트가 **새 요청 ID로 다시 보내야 한다**.
재시도가 멱등하지 않은 툴이 있다면 여기서 깨진다.

## 4. 제거된 메서드

| 제거 | 대체 |
|---|---|
| `ping` | 없음 — 전송 계층 keepalive를 쓴다 |
| `logging/setLevel` | 요청별로 `_meta`의 `io.modelcontextprotocol/logLevel` |
| `notifications/roots/list_changed` | Roots 자체가 deprecated (SEP-2577) |
| `tasks/list` | `tasks/get` 폴링 |

로그 레벨이 요청 단위가 됐으므로, 서버는 이 필드가 없는 요청에 대해
`notifications/message`를 **보내면 안 된다.**

## 5. Tasks 확장

experimental Tasks가 공식 확장 `io.modelcontextprotocol/tasks`로 이동했다(SEP-2663).
차단형 `tasks/result`가 `tasks/get` 폴링으로 바뀌었고, 클라이언트→서버 입력을 위한
`tasks/update`가 생겼다. 서버는 요청별 opt-in 없이 태스크 핸들을 반환할 수 있다.

`ClientCapabilities`·`ServerCapabilities`에 `extensions` 필드가 추가돼 선택적 확장을 선언한다.

## 6. 전송·캐싱

- Streamable HTTP POST에 `Mcp-Method`·`Mcp-Name` 헤더가 **필수**다(SEP-2243).
  게이트웨이·WAF가 본문을 파싱하지 않고 라우팅·계량할 수 있다.
  사용자 정의 헤더는 `x-mcp-header`로 실어 보낸다.
- `CacheableResult`가 생겨 `tools/list`·`prompts/list`·`resources/list`·
  `resources/read`·`resources/templates/list` 결과에 `ttlMs`와 `cacheScope`가 필요하다(SEP-2549).
  `cacheScope`는 `"public"` 또는 `"private"`이며 중간 캐시 허용 여부를 정한다.
- 서버는 `tools/list`를 **결정론적 순서로** 반환해야 한다. 클라이언트 캐싱과
  LLM 프롬프트 캐시 적중률이 여기에 달려 있다.
- OpenTelemetry 트레이스 컨텍스트를 `_meta`의 `traceparent`·`tracestate`·`baggage`로
  전파하는 관례가 문서화됐다(SEP-414).

## 7. 인증

- 인가 서버는 RFC 9207에 따라 `iss`를 포함해야 하고, 클라이언트는 **코드 교환 전에**
  기록해 둔 issuer와 대조해야 한다(SEP-2468).
- Dynamic Client Registration 시 `application_type`을 반드시 지정한다 —
  OpenID Connect의 redirect URI 충돌을 피하기 위함이다(SEP-837).
- 자격증명은 **issuer를 키로** 보관하며 인가 서버 간에 재사용하지 않는다.
  서버가 바뀌면 재등록해야 한다(SEP-2352).
- **DCR(RFC 7591)이 deprecated 됐다.** Client ID Metadata Documents(CIMD)가 대체이며,
  하위 호환을 위해 남아 있을 뿐이다.

## 8. 스키마·오류 코드

- `inputSchema`/`outputSchema`가 JSON Schema 2020-12 키워드를 전부 허용하도록 완화됐고
  `structuredContent`는 임의 JSON 값을 받는다. `$ref` 해석 요구사항과 조합 키워드의
  리소스 상한이 추가됐다(SEP-2106).
- resource not found 오류 코드가 `-32002` → `-32602`(Invalid Params)로 바뀌었다.
- 오류 코드 할당 정책이 생겼다 — `-32000`~`-32019`는 구현 정의, `-32020`~`-32099`는
  사양 예약. `HeaderMismatch`가 `-32001`→`-32020`,
  `MissingRequiredClientCapability`가 `-32003`→`-32021`,
  `UnsupportedProtocolVersion`이 `-32004`→`-32022`로 재번호됐다(SEP-2596).

## 9. Deprecated (기능은 남아 있음)

| 대상 | 대체 | 근거 |
|---|---|---|
| Roots | 툴 파라미터·리소스 URI·설정으로 경로 전달 | SEP-2577 |
| Sampling | provider API 직접 호출 | SEP-2577 |
| Logging | stderr 또는 OpenTelemetry | SEP-2577 |
| HTTP+SSE 전송 | Streamable HTTP (2025-03-26부터 deprecated) | SEP-2596 |
| `includeContext`의 `"thisServer"`·`"allServers"` | 생략하거나 `"none"` | SEP-2596 |
| DCR (RFC 7591) | CIMD | PR #2858 |

사양 기능 생명주기 정책이 채택돼 Active / Deprecated / Removed 상태와
**제거까지 최소 12개월 유예**, deprecated 기능 레지스트리가 규정됐다(SEP-2596).

## 이행 시 먼저 확인할 것

- [ ] 세션 상태에 의존하는 툴이 있는가 — 있으면 서버 발급 핸들로 옮긴다
- [ ] `sampling/createMessage`나 `elicitation/create`를 쓰는가 — MRTR로 다시 쓴다
- [ ] 재시도가 멱등하지 않은 툴이 있는가 — SSE 재개가 없어져 재요청이 늘어난다
- [ ] `ping`으로 헬스체크를 하는가 — 전송 계층으로 옮긴다
- [ ] 게이트웨이가 `Mcp-Method`·`Mcp-Name` 헤더를 통과시키는가
- [ ] 인가 서버가 `iss`를 내려주는가, 클라이언트가 대조하는가
